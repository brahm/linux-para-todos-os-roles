//! bora: leva você até o rolê, com receitas testadas e um jeito de voltar atrás.
//!
//! Este arquivo é a porta de entrada. Ele lê a linha de comando (com o `clap`),
//! escolhe o subcomando e chama os outros módulos. A lógica de verdade mora neles:
//!
//! - `diag`: descobre a distro, a memória, o disco e o que já está instalado.
//! - `fonte` e `catalogo`: acham e leem as receitas e os rolês (embutidos no
//!   binário ou, com `BORA_RAIZ`, direto da pasta do repositório).
//! - `plano`: monta um plano a partir de um rolê ou de receitas avulsas e confere
//!   se ele vale para esta máquina.
//! - `executor`: roda os scripts de cada receita, guarda o estado em
//!   `/var/lib/bora` e sabe desfazer.
//! - `snapshot`: tira o snapshot do sistema antes de aplicar.
//! - `modelos`: escolhe os modelos de IA locais que cabem na máquina.
//! - `ajuda`: monta a pergunta pronta para colar num chat de IA.
//! - `ui`: cores, menus e perguntas no terminal.
//!
//! O fluxo típico do menu é: diagnóstico, escolha do rolê, perguntas, plano,
//! validação e, por fim, `sudo bora aplicar`. O mapa completo está em
//! `docs/arquitetura.md`.

mod ajuda;
mod catalogo;
mod diag;
mod executor;
mod fonte;
mod modelos;
mod plano;
mod snapshot;
mod ui;

use catalogo::{Catalogo, Receita, texto_de};
use clap::{Arg, ArgAction, ArgMatches, Command, error::ErrorKind};
use diag::Diag;
use serde_norway::{Mapping, Value};
use std::collections::BTreeMap;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use ui::{Erro, Opcao, R};

/// A versão vem do `Cargo.toml` na hora de compilar; não existe outro lugar para mudar.
const VERSAO: &str = env!("CARGO_PKG_VERSION");

/// Roda o diagnóstico da máquina.
///
/// `BORA_OS_RELEASE` aponta para outro `os-release`. Os testes usam isso para
/// fingir que estão no Fedora, no Arch ou numa distro que o `bora` recusa.
fn coletar_diag() -> Diag {
    let osr = std::env::var_os("BORA_OS_RELEASE").map(PathBuf::from);
    diag::coletar(osr.as_deref())
}

/// Lê o catálogo e avisa, sem parar, se alguma receita ou rolê veio com erro.
/// Os itens com problema ficam de fora; o `bora conferir` diz quais são.
fn carregar_catalogo(f: &fonte::Fonte) -> Catalogo {
    let c = Catalogo::carregar(&f.raiz);
    if !c.erros.is_empty() {
        ui::aviso(
            "O catálogo tem problemas; as receitas e rolês com erro ficam de fora. Rode bora conferir.",
        );
    }
    c
}

/// Para tudo (código de saída 2) se a distro não for suportada, mostrando o
/// motivo. Se for suportada mas com ressalvas, só mostra os avisos.
fn exigir_suportada(d: &Diag) -> R<()> {
    if !d.suportada {
        for p in &d.problemas {
            ui::erro(p);
        }
        return Err(Erro::Codigo(2));
    }
    for a in &d.avisos {
        ui::aviso(a);
    }
    Ok(())
}

/// Imprime o plano validado: uma linha por receita, com o risco quando ele não
/// é baixo, e os parâmetros escolhidos logo abaixo.
fn mostrar_plano(v: &plano::PlanoValidado) {
    ui::titulo(&format!(
        "Plano: {}",
        v.objetivo.as_deref().unwrap_or("receitas avulsas")
    ));
    for (i, p) in v.passos.iter().enumerate() {
        let risco = match p.receita.risco.as_str() {
            "medio" => " · risco médio",
            "alto" => " · risco alto",
            _ => "",
        };
        println!(
            "  {}. {}{}",
            i + 1,
            ui::negrito(&p.receita.nome),
            ui::apagado(risco)
        );
        println!("{}", ui::apagado(&format!("     {}", p.receita.descricao)));
        if !p.parametros.is_empty() {
            let t: Vec<String> = p
                .parametros
                .iter()
                .map(|(k, v)| format!("{k}={v}"))
                .collect();
            println!("{}", ui::apagado(&format!("     {}", t.join(", "))));
        }
    }
    for a in &v.avisos {
        ui::aviso(a);
    }
}

/// Mostra a lista de problemas de um plano e devolve o erro com código 2.
fn erros_do_plano(titulo: &str, erros: Vec<String>) -> Erro {
    ui::erro(titulo);
    for e in erros {
        eprintln!("  - {e}");
    }
    Erro::Codigo(2)
}

/// Lê um plano do disco e confere contra o catálogo e a máquina.
/// Devolve o YAML cru (que vai junto para o registro da execução) e o validado.
fn carregar_validado(caminho: &Path, c: &Catalogo, d: &Diag) -> R<(Value, plano::PlanoValidado)> {
    let cru = plano::ler(caminho).map_err(|e| {
        ui::erro(&e);
        Erro::Codigo(2)
    })?;
    let v = plano::validar(&cru, c, d).map_err(|e| erros_do_plano("O plano tem problemas:", e))?;
    Ok((cru, v))
}

/// Separa uma lista de `nome=valor` em pares. `rotulo` é o nome da opção
/// (`--resposta`, `--parametro`) e só aparece na mensagem de erro.
fn pares(valores: Option<Vec<String>>, rotulo: &str) -> R<Vec<(String, String)>> {
    let mut saida = Vec::new();
    for par in valores.unwrap_or_default() {
        let Some((k, v)) = par.split_once('=') else {
            return Err(format!("{rotulo} precisa ser no formato nome=valor: {par}").into());
        };
        saida.push((k.trim().to_string(), v.to_string()));
    }
    Ok(saida)
}

/// Atalho para ler uma opção que pode aparecer várias vezes na linha de comando.
fn lista(m: &ArgMatches, nome: &str) -> Option<Vec<String>> {
    m.get_many::<String>(nome).map(|v| v.cloned().collect())
}

// Comandos ---------------------------------------------------------------

/// `bora diag`: mostra o diagnóstico, em texto ou em JSON.
/// Sai com 2 se a distro não é suportada, para scripts poderem testar.
fn cmd_diag(m: &ArgMatches) -> R<i32> {
    let d = coletar_diag();
    if m.get_flag("json") {
        println!("{}", serde_json::to_string_pretty(&d).unwrap_or_default());
    } else {
        println!("{}", diag::formatar(&d));
    }
    Ok(if d.suportada { 0 } else { 2 })
}

/// `bora modelos`: lista os modelos de IA locais, diz quais cabem na máquina
/// e qual o `bora` sugere. A lista vem de `receitas/ia/ollama/modelos.yaml`.
fn cmd_modelos(m: &ArgMatches, f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    let lista = modelos::carregar(&f.raiz).map_err(Erro::Msg)?;
    let maq = modelos::Maquina::de(&d);
    if m.get_flag("json") {
        let avaliados: Vec<serde_json::Value> = lista
            .modelos
            .iter()
            .map(|m| {
                serde_json::json!({
                    "modelo": m,
                    "memoria_gb": m.memoria_gb(),
                    "lugar": modelos::avaliar(m, &maq),
                })
            })
            .collect();
        let saida = serde_json::json!({
            "maquina": maq,
            "verificado_em": lista.verificado_em,
            "modelos": avaliados,
            "sugestao": modelos::sugerir(&lista, &maq),
        });
        println!(
            "{}",
            serde_json::to_string_pretty(&saida).unwrap_or_default()
        );
    } else {
        ui::titulo("Modelos de IA locais");
        println!("{}", modelos::formatar(&lista, &maq, &d.hardware.video));
    }
    Ok(0)
}

/// `bora lista`: mostra os rolês (● disponível, ○ não, com o motivo) e as
/// receitas com o nível de teste na família de distro desta máquina.
fn cmd_lista(f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    let c = carregar_catalogo(f);
    ui::titulo("Rolês");
    for r in &c.roles {
        let disp = if d.suportada {
            c.disponibilidade(r, &d)
        } else {
            Err("distro não suportada".into())
        };
        let marca = if disp.is_ok() {
            ui::verde("●")
        } else {
            ui::apagado("○")
        };
        println!(
            "  {marca} {:<24} {} {}",
            r.id,
            r.nome,
            ui::apagado(&format!("({})", r.status))
        );
        if let Err(motivo) = disp {
            println!("{}", ui::apagado(&format!("      {motivo}")));
        }
    }
    ui::titulo("Receitas");
    let fam = d.distro.familia.clone().unwrap_or_default();
    for r in &c.receitas {
        let nivel = if fam.is_empty() { "-" } else { r.nivel(&fam) };
        println!("  {:<24} {:<28} {}", r.id, r.nome, ui::apagado(nivel));
    }
    Ok(0)
}

/// `bora plano`: monta um plano sem menus, para scripts e agentes.
///
/// Aceita um rolê com respostas (`-r pergunta=valor`) ou receitas avulsas
/// (`--receitas a,b`), mais parâmetros (`-p receita.nome=valor`). O plano é
/// validado antes de ser salvo, então um plano salvo sempre é aplicável aqui.
fn cmd_plano(m: &ArgMatches, f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    exigir_suportada(&d)?;
    let c = carregar_catalogo(f);
    let familia = d.distro.familia.clone().unwrap_or_default();
    // Agrupa os parâmetros por receita. O id da receita tem barra
    // ("seguranca/firewall"), então o nome do parâmetro é o que vem depois
    // do último ponto.
    let mut params: BTreeMap<String, Mapping> = BTreeMap::new();
    for (chave, valor) in pares(lista(m, "parametro"), "--parametro")? {
        let Some((rid, nome)) = chave.rsplit_once('.') else {
            return Err(format!(
                "--parametro precisa ser receita.nome=valor, por exemplo seguranca/firewall.perfil=desktop: {chave}"
            )
            .into());
        };
        params
            .entry(rid.to_string())
            .or_default()
            .insert(Value::String(nome.into()), Value::String(valor));
    }
    let cru = if let Some(receitas) = m.get_one::<String>("receitas") {
        let ids: Vec<String> = receitas
            .split(',')
            .map(|s| s.trim().to_string())
            .filter(|s| !s.is_empty())
            .collect();
        plano::montar_de_receitas(&ids, &familia, &params)
    } else if let Some(id) = m.get_one::<String>("role") {
        let Some(role) = c.role(id) else {
            ui::erro(&format!(
                "rolê desconhecido: {id}. Veja a lista com bora lista."
            ));
            return Ok(2);
        };
        if let Err(motivo) = c.disponibilidade(role, &d) {
            ui::erro(&format!(
                "o rolê {} não está disponível nesta máquina: {motivo}",
                role.nome
            ));
            return Ok(2);
        }
        let respostas: BTreeMap<String, String> = pares(lista(m, "resposta"), "--resposta")?
            .into_iter()
            .collect();
        let mut cru = match plano::montar_de_role(role, &respostas, &familia) {
            Ok(p) => p,
            Err(e) => {
                ui::erro(&e);
                return Ok(2);
            }
        };
        for (rid, extra) in &params {
            plano::acrescentar_parametros(&mut cru, rid, extra);
        }
        cru
    } else {
        ui::erro("diga um rolê (bora plano ID) ou receitas avulsas (bora plano --receitas a,b)");
        return Ok(2);
    };
    let mut cru = cru;
    let v = plano::validar(&cru, &c, &d)
        .map_err(|e| erros_do_plano("O plano gerado tem problemas:", e))?;
    // Se o plano tem um modelo de IA "automático", grava no arquivo o modelo
    // escolhido, para a aplicação não mudar de ideia depois.
    plano::fixar_modelo(&mut cru, &v);
    let saida = m
        .get_one::<String>("saida")
        .map(String::as_str)
        .unwrap_or("plano.yaml");
    if saida == "-" {
        print!("{}", plano::para_texto(&cru));
    } else {
        plano::salvar(&cru, Path::new(saida))?;
        mostrar_plano(&v);
        println!();
        ui::ok(&format!(
            "Plano salvo em {saida}. Para aplicar: sudo bora aplicar {saida}"
        ));
    }
    Ok(0)
}

/// `bora validar`: confere um plano sem aplicar nada.
fn cmd_validar(m: &ArgMatches, f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    exigir_suportada(&d)?;
    let c = carregar_catalogo(f);
    let (_, v) = carregar_validado(Path::new(m.get_one::<String>("plano").unwrap()), &c, &d)?;
    mostrar_plano(&v);
    println!();
    ui::ok("O plano é válido para esta máquina.");
    Ok(0)
}

/// `bora aplicar`: aplica um plano, receita por receita.
///
/// Com `--simular`, só roda o `verificar.sh` de cada receita e conta quantas
/// mudariam. Sem ele, pede confirmação e entrega para o `executor`, que tira o
/// snapshot e aplica. Se uma receita falha, ele para ali e a pessoa decide se
/// roda `sudo bora desfazer`.
fn cmd_aplicar(m: &ArgMatches, f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    exigir_suportada(&d)?;
    let c = carregar_catalogo(f);
    let (cru, v) = carregar_validado(Path::new(m.get_one::<String>("plano").unwrap()), &c, &d)?;
    mostrar_plano(&v);
    if m.get_flag("simular") {
        let mudariam = executor::simular(&v, &d, &c)?;
        println!();
        ui::info(&format!(
            "{mudariam} de {} receitas seriam aplicadas.",
            v.passos.len()
        ));
        return Ok(0);
    }
    let perguntar = !m.get_flag("sem-perguntar");
    println!();
    if perguntar && !ui::confirmar("Aplicar este plano?", false)? {
        println!("Nada foi alterado.");
        return Ok(1);
    }
    let op = executor::Opcoes {
        sem_snapshot: m.get_flag("sem-snapshot"),
        passo_a_passo: m.get_flag("passo-a-passo"),
        perguntar,
    };
    let situacao = executor::aplicar(&v, &cru, &d, &c, &op)?;
    if situacao == "concluida" {
        println!();
        ui::ok("Pronto. O plano foi aplicado e cada receita passou no teste.");
        if let Some(role) = v.objetivo.as_deref().and_then(|o| c.role(o)) {
            ui::info(&format!("Para conferir você mesmo: {}", role.pronto_quando));
        }
        ui::info("Para voltar atrás: sudo bora desfazer");
    }
    Ok(0)
}

/// `bora desfazer`: volta atrás a última execução, ou uma escolhida pelo id.
///
/// Só deixa desfazer da mais nova para a mais antiga. Desfazer fora de ordem
/// pode deixar o sistema num estado que nenhuma das duas execuções conhece.
fn cmd_desfazer(m: &ArgMatches) -> R<i32> {
    let d = coletar_diag();
    let alvo = if let Some(id) = m.get_one::<String>("execucao") {
        let Some(alvo) = executor::listar_execucoes()
            .into_iter()
            .find(|e| &e.dados.id == id)
        else {
            ui::erro(&format!(
                "execução não encontrada: {id}. Veja bora historico."
            ));
            return Ok(2);
        };
        if let Some(ultima) = executor::ultima_desfazivel()
            && ultima.dados.id != alvo.dados.id
        {
            ui::erro(&format!(
                "desfaça antes a execução mais recente ({}); o bora desfaz da mais nova para a mais antiga",
                ultima.dados.id
            ));
            return Ok(2);
        }
        alvo
    } else {
        match executor::ultima_desfazivel() {
            Some(e) => e,
            None => {
                println!("Não há nada para desfazer.");
                return Ok(0);
            }
        }
    };
    let ok = executor::desfazer(alvo, &d, !m.get_flag("sem-perguntar"))?;
    Ok(if ok { 0 } else { 1 })
}

/// `bora ajuda`: imprime a pergunta pronta para o chat de IA. O texto vai para a
/// saída padrão (dá para redirecionar) e o lembrete vai para a saída de erro.
fn cmd_ajuda(m: &ArgMatches) -> R<i32> {
    let pergunta = lista(m, "pergunta").map(|v| v.join(" "));
    println!("{}", ajuda::montar(&coletar_diag(), pergunta.as_deref()));
    println!();
    eprintln!(
        "{}",
        ui::apagado(
            "Copie o texto acima e cole no chat de IA que você usa. Confira antes se não há nada pessoal nele."
        )
    );
    Ok(0)
}

/// `bora conferir`: confere o catálogo inteiro, para quem contribui e para o CI.
/// Erros de formato, a lista de modelos e o status de teste fora da regra
/// fazem o comando sair com 1.
fn cmd_conferir(f: &fonte::Fonte) -> R<i32> {
    let mut c = Catalogo::carregar(&f.raiz);
    if let Err(e) = modelos::carregar(&f.raiz) {
        c.erros.push(e);
    }
    if !c.erros.is_empty() {
        for e in &c.erros {
            ui::erro(e);
        }
        return Ok(1);
    }
    let status = c.status_fora_da_regra();
    if !status.is_empty() {
        for e in &status {
            ui::erro(e);
        }
        return Ok(1);
    }
    let plural =
        |n: usize, um: &str, varios: &str| format!("{n} {}", if n == 1 { um } else { varios });
    ui::ok(&format!(
        "Catálogo em ordem: {} e {}.",
        plural(c.receitas.len(), "receita", "receitas"),
        plural(c.roles.len(), "rolê", "rolês")
    ));
    Ok(0)
}

// Menu -------------------------------------------------------------------

/// Onde o menu salva os planos: em `/var/lib/bora/planos` quando roda como
/// root, e em `~/.local/share/bora/planos` (ou `$XDG_DATA_HOME`) quando não.
fn pasta_planos() -> PathBuf {
    if executor::e_root() {
        return executor::dir_estado().join("planos");
    }
    let base = std::env::var_os("XDG_DATA_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            PathBuf::from(std::env::var_os("HOME").unwrap_or_else(|| "/tmp".into()))
                .join(".local/share")
        });
    base.join("bora/planos")
}

/// Troca, no texto de uma pergunta, o que depende da máquina:
/// {sugestao_de_modelo} vira o modelo que o "bora modelos" sugere.
fn preencher_da_maquina(texto: &str, c: &Catalogo, d: &Diag) -> String {
    const MARCA: &str = "{sugestao_de_modelo}";
    if !texto.contains(MARCA) {
        return texto.to_string();
    }
    let sugestao = match modelos::carregar(&c.raiz) {
        Ok(l) => modelos::sugerir(&l, &modelos::Maquina::de(d)).motivo,
        Err(_) => "o bora não conseguiu ler a lista de modelos".into(),
    };
    texto.replace(MARCA, &sugestao)
}

/// Faz, no menu, as perguntas dos parâmetros de uma receita.
///
/// Pula os parâmetros que o rolê já fixou (`fixos`) e os que não têm pergunta.
/// O tipo do parâmetro decide o jeito de perguntar: lista de opções, sim ou não,
/// ou texto livre, que repete a pergunta até o valor ser aceito.
fn perguntar_parametros(rec: &Receita, fixos: &[String], c: &Catalogo, d: &Diag) -> R<Mapping> {
    let mut valores = Mapping::new();
    for p in &rec.parametros {
        if fixos.contains(&p.nome) || p.pergunta.is_empty() {
            continue;
        }
        let pergunta = format!(
            "\n{}: {}",
            rec.nome,
            preencher_da_maquina(&p.pergunta, c, d)
        );
        let padrao = p.padrao.as_ref().and_then(texto_de);
        let valor = loop {
            match p.tipo.as_str() {
                "escolha" => {
                    let opcoes: Vec<Opcao> = p
                        .opcoes
                        .iter()
                        .map(|o| Opcao::new(o, p.rotulo(o), true))
                        .collect();
                    let i = ui::escolher(
                        &pergunta,
                        &opcoes,
                        padrao
                            .as_ref()
                            .and_then(|d| p.opcoes.iter().position(|o| o == d)),
                    )?;
                    break Value::String(p.opcoes[i].clone());
                }
                "booleano" => {
                    let atual = matches!(
                        p.converter(p.padrao.as_ref()),
                        Ok(catalogo::Valor::Booleano(true))
                    );
                    break Value::Bool(ui::confirmar(&pergunta, atual)?);
                }
                _ => {
                    let bruto = ui::perguntar(&pergunta, padrao.as_deref())?;
                    match p.converter(Some(&Value::String(bruto.clone()))) {
                        Ok(_) => break Value::String(bruto),
                        Err(e) => ui::erro(&e),
                    }
                }
            }
        };
        valores.insert(Value::String(p.nome.clone()), valor);
    }
    Ok(valores)
}

/// Roda o próprio `bora` de novo com outros argumentos, trocando o processo atual
/// (`exec`). Se não for root, passa pelo `sudo`, levando junto as variáveis que
/// mudam o comportamento do `bora`. Só volta daqui se o `exec` falhar.
fn reexecutar(args: &[&str]) -> R<i32> {
    let exe = std::env::current_exe()?;
    let mut cmd = if executor::e_root() {
        let mut c = std::process::Command::new(&exe);
        c.args(args);
        c
    } else {
        if !diag::comando_existe("sudo") {
            return Err(format!(
                "o sudo não está instalado; entre como root e rode: bora {}",
                args.join(" ")
            )
            .into());
        }
        let mut c = std::process::Command::new("sudo");
        c.arg("--preserve-env=BORA_RAIZ,BORA_PERMITIR_SEM_SYSTEMD")
            .arg(&exe)
            .args(args);
        c
    };
    Err(Erro::Msg(format!(
        "não consegui rodar o bora de novo: {}",
        cmd.exec()
    )))
}

/// Última etapa do menu: valida o plano, mostra e pergunta o que fazer com ele
/// (aplicar, simular, salvar ou voltar). Aplicar e simular salvam o plano e
/// chamam `bora aplicar` com `sudo`, então a senha só é pedida nessa hora.
fn menu_finalizar(mut cru: Value, c: &Catalogo, d: &Diag) -> R<()> {
    let v = match plano::validar(&cru, c, d) {
        Ok(v) => v,
        Err(erros) => {
            for e in erros {
                ui::erro(&e);
            }
            return Ok(());
        }
    };
    plano::fixar_modelo(&mut cru, &v);
    mostrar_plano(&v);
    println!();
    let i = ui::escolher(
        "O que fazer com o plano?",
        &[
            Opcao::new("Aplicar agora", "pede a senha de administrador", true),
            Opcao::new("Só simular", "mostra o que mudaria, sem mudar nada", true),
            Opcao::new(
                "Salvar para depois",
                "para revisar, versionar ou aplicar em outra máquina",
                true,
            ),
            Opcao::new("Voltar", "", true),
        ],
        Some(0),
    )?;
    if i == 3 {
        return Ok(());
    }
    let pasta = pasta_planos();
    std::fs::create_dir_all(&pasta)?;
    let nome = format!(
        "{}-{}.yaml",
        v.objetivo.as_deref().unwrap_or("avulso"),
        chrono::Local::now().format("%Y%m%d-%H%M%S")
    );
    let caminho = pasta.join(nome);
    plano::salvar(&cru, &caminho)?;
    let c = caminho.display().to_string();
    if i == 2 {
        ui::ok(&format!("Plano salvo em {c}"));
        ui::info(&format!("Para aplicar: sudo bora aplicar {c}"));
        return Err(Erro::Codigo(0));
    }
    if i == 1 {
        reexecutar(&["aplicar", &c, "--simular"])
    } else {
        reexecutar(&["aplicar", &c])
    }
    .map(|_| ())
}

/// O menu de rolês, que abre quando o `bora` roda sem comando.
///
/// As opções são os rolês do catálogo (os indisponíveis aparecem apagados, com
/// o motivo) e mais cinco fixas no fim. Por isso o índice escolhido é comparado
/// com `n_roles`: abaixo dele é um rolê, a partir dele é uma das fixas.
fn cmd_menu(f: &fonte::Fonte) -> R<i32> {
    let d = coletar_diag();
    println!(
        "{}{}",
        ui::negrito("bora"),
        ui::apagado(&format!(" {VERSAO} · Linux para todos os rolês"))
    );
    println!("{}", diag::resumo(&d));
    exigir_suportada(&d)?;
    let c = carregar_catalogo(f);
    let fam = d.distro.familia.clone().unwrap_or_default();
    loop {
        println!();
        let mut opcoes: Vec<Opcao> = c
            .roles
            .iter()
            .map(|r| match c.disponibilidade(r, &d) {
                Ok(()) => Opcao::new(&r.nome, &r.descricao, true),
                Err(motivo) => Opcao::new(&r.nome, motivo, false),
            })
            .collect();
        let n_roles = opcoes.len();
        opcoes.extend([
            Opcao::new(
                "Receitas avulsas",
                "escolher uma ou mais receitas do catálogo",
                !c.receitas.is_empty(),
            ),
            Opcao::new("Ver o diagnóstico completo", "", true),
            Opcao::new(
                "Desfazer a última aplicação",
                "",
                executor::ultima_desfazivel().is_some(),
            ),
            Opcao::new("Montar uma pergunta para a IA", "bora ajuda", true),
            Opcao::new("Sair", "", true),
        ]);
        let i = ui::escolher("O que você quer fazer com este computador?", &opcoes, None)?;
        if i < n_roles {
            let role = &c.roles[i];
            ui::titulo(&role.nome);
            println!("{}", role.descricao);
            println!(
                "{}",
                ui::apagado(&format!("Pronto quando: {}", role.pronto_quando))
            );
            println!(
                "{}",
                ui::apagado(&format!("Para voltar atrás: {}", role.como_desfazer))
            );
            let mut respostas = BTreeMap::new();
            let da_maquina = |t: &str| preencher_da_maquina(t, &c, &d);
            for p in &role.perguntas {
                let resposta = if p.opcoes.is_empty() {
                    ui::perguntar(&da_maquina(&p.texto), p.padrao.as_deref())?
                } else {
                    let opcoes: Vec<Opcao> = p
                        .opcoes
                        .iter()
                        .map(|o| Opcao::new(o, da_maquina(p.rotulo(o)), true))
                        .collect();
                    let padrao = p
                        .padrao
                        .as_ref()
                        .and_then(|d| p.opcoes.iter().position(|o| o == d));
                    let i = ui::escolher(&format!("\n{}", da_maquina(&p.texto)), &opcoes, padrao)?;
                    p.opcoes[i].clone()
                };
                respostas.insert(p.id.clone(), resposta);
            }
            let mut cru = match plano::montar_de_role(role, &respostas, &fam) {
                Ok(p) => p,
                Err(e) => {
                    ui::erro(&e);
                    continue;
                }
            };
            for item in role.receitas.iter().filter(|i| i.entra(&respostas)) {
                let rec = c.receita(&item.id).unwrap();
                let fixos: Vec<String> = item.parametros.iter().map(|(k, _)| k.clone()).collect();
                let extra = perguntar_parametros(rec, &fixos, &c, &d)?;
                plano::acrescentar_parametros(&mut cru, &item.id, &extra);
            }
            menu_finalizar(cru, &c, &d)?;
            continue;
        }
        match i - n_roles {
            0 => {
                let ops: Vec<Opcao> = c
                    .receitas
                    .iter()
                    .map(|r| {
                        if r.aplicavel(&fam) {
                            Opcao::new(&r.nome, &r.descricao, true)
                        } else {
                            Opcao::new(
                                &r.nome,
                                format!("ainda não funciona na família {fam}"),
                                false,
                            )
                        }
                    })
                    .collect();
                let escolhidas = ui::escolher_varios("\nQuais receitas?", &ops)?;
                if escolhidas.is_empty() {
                    continue;
                }
                let mut params = BTreeMap::new();
                let mut ids = Vec::new();
                for j in escolhidas {
                    let r = &c.receitas[j];
                    params.insert(r.id.clone(), perguntar_parametros(r, &[], &c, &d)?);
                    ids.push(r.id.clone());
                }
                menu_finalizar(plano::montar_de_receitas(&ids, &fam, &params), &c, &d)?;
            }
            1 => {
                println!();
                println!("{}", diag::formatar(&d));
            }
            2 => return reexecutar(&["desfazer"]),
            3 => {
                println!();
                println!("{}", ajuda::montar(&d, None));
            }
            _ => return Ok(0),
        }
    }
}

// Linha de comando -------------------------------------------------------

/// Cria um subcomando com a ajuda em português (`-h`, `--help`).
/// O `clap` traz a ajuda em inglês por padrão, então ela é desligada e refeita.
fn sub(nome: &'static str, sobre: &'static str) -> Command {
    Command::new(nome).about(sobre).disable_help_flag(true).arg(
        Arg::new("help")
            .short('h')
            .long("help")
            .action(ArgAction::Help)
            .help("mostra esta ajuda"),
    )
}

/// Descreve toda a linha de comando do `bora`: subcomandos, opções e textos de ajuda.
/// Para um comando novo, acrescente aqui e trate em `principal`.
fn comando() -> Command {
    let modelo = "{about}\n\nUso: {usage}\n\n{all-args}{after-help}";
    Command::new("bora")
        .about("Leva você até o rolê, com receitas testadas e um jeito de voltar atrás.")
        .after_help("\nSem comando, o bora abre o menu de rolês.")
        .help_template(modelo)
        .subcommand_help_heading("Comandos")
        .next_help_heading("Opções")
        .subcommand_value_name("COMANDO")
        .disable_help_flag(true)
        .disable_version_flag(true)
        .disable_help_subcommand(true)
        .arg(
            Arg::new("help")
                .short('h')
                .long("help")
                .action(ArgAction::Help)
                .help("mostra esta ajuda"),
        )
        .arg(
            Arg::new("versao")
                .long("versao")
                .alias("version")
                .action(ArgAction::SetTrue)
                .help("mostra a versão"),
        )
        .subcommand(
            sub(
                "diag",
                "descobre distro, memória, disco e o que já está instalado",
            )
            .arg(
                Arg::new("json")
                    .long("json")
                    .action(ArgAction::SetTrue)
                    .help("saída em JSON, para agentes e scripts"),
            ),
        )
        .subcommand(sub("lista", "lista os rolês e as receitas do catálogo"))
        .subcommand(
            sub(
                "modelos",
                "mostra os modelos de IA locais que cabem nesta máquina e qual o bora sugere",
            )
            .arg(
                Arg::new("json")
                    .long("json")
                    .action(ArgAction::SetTrue)
                    .help("saída em JSON, para agentes e scripts"),
            ),
        )
        .subcommand(
            sub("plano", "monta um plano sem menus, para scripts e agentes")
                .arg(Arg::new("role").value_name("ROLÊ").help("o id do rolê"))
                .arg(
                    Arg::new("receitas")
                        .long("receitas")
                        .value_name("A,B")
                        .help("receitas avulsas separadas por vírgula, no lugar de um rolê"),
                )
                .arg(
                    Arg::new("resposta")
                        .short('r')
                        .long("resposta")
                        .value_name("PERGUNTA=VALOR")
                        .action(ArgAction::Append)
                        .help("resposta a uma pergunta do rolê"),
                )
                .arg(
                    Arg::new("parametro")
                        .short('p')
                        .long("parametro")
                        .value_name("RECEITA.NOME=VALOR")
                        .action(ArgAction::Append)
                        .help("parâmetro de uma receita"),
                )
                .arg(
                    Arg::new("saida")
                        .short('o')
                        .long("saida")
                        .value_name("ARQUIVO")
                        .help("onde salvar (padrão: plano.yaml; - para a tela)"),
                ),
        )
        .subcommand(
            sub("validar", "confere um plano sem aplicar nada")
                .arg(Arg::new("plano").required(true).value_name("PLANO")),
        )
        .subcommand(
            sub(
                "aplicar",
                "aplica um plano, receita por receita (precisa de sudo)",
            )
            .arg(Arg::new("plano").required(true).value_name("PLANO"))
            .arg(
                Arg::new("simular")
                    .long("simular")
                    .action(ArgAction::SetTrue)
                    .help("só mostra o que mudaria"),
            )
            .arg(
                Arg::new("passo-a-passo")
                    .long("passo-a-passo")
                    .action(ArgAction::SetTrue)
                    .help("explica cada etapa e pergunta antes de aplicar"),
            )
            .arg(
                Arg::new("sem-snapshot")
                    .long("sem-snapshot")
                    .action(ArgAction::SetTrue)
                    .help("não cria snapshot do sistema antes"),
            )
            .arg(
                Arg::new("sem-perguntar")
                    .long("sem-perguntar")
                    .action(ArgAction::SetTrue)
                    .help("não pede confirmação (para scripts)"),
            ),
        )
        .subcommand(
            sub("desfazer", "desfaz a última aplicação (precisa de sudo)")
                .arg(
                    Arg::new("execucao")
                        .value_name("EXECUÇÃO")
                        .help("o id da execução; o padrão é a mais recente"),
                )
                .arg(
                    Arg::new("sem-perguntar")
                        .long("sem-perguntar")
                        .action(ArgAction::SetTrue)
                        .help("não pede confirmação"),
                ),
        )
        .subcommand(sub("historico", "mostra o que o bora já aplicou e desfez"))
        .subcommand(
            sub(
                "ajuda",
                "monta uma pergunta pronta para colar num chat de IA",
            )
            .arg(
                Arg::new("pergunta")
                    .num_args(0..)
                    .value_name("DÚVIDA")
                    .help("sua dúvida, opcional"),
            ),
        )
        .subcommand(sub("conferir", "confere o catálogo (para quem contribui)"))
        .subcommand(sub("versao", "mostra a versão"))
}

/// Traduz os erros do `clap` para mensagens curtas em português.
fn traduzir_erro(e: &clap::Error) -> String {
    let contexto = |k| e.get(k).map(|v| v.to_string()).unwrap_or_default();
    use clap::error::ContextKind as C;
    match e.kind() {
        ErrorKind::InvalidSubcommand => format!(
            "comando desconhecido: {}. Veja bora --help.",
            contexto(C::InvalidSubcommand)
        ),
        ErrorKind::UnknownArgument => format!(
            "opção desconhecida: {}. Veja bora --help.",
            contexto(C::InvalidArg)
        ),
        ErrorKind::MissingRequiredArgument => {
            format!("falta um argumento: {}", contexto(C::InvalidArg))
        }
        ErrorKind::TooManyValues | ErrorKind::ArgumentConflict => {
            "argumentos demais ou que não combinam. Veja bora --help.".into()
        }
        _ => "não entendi o comando. Veja bora --help.".into(),
    }
}

/// Lê a linha de comando, abre o catálogo e chama o subcomando certo.
/// Devolve o código de saída do processo.
fn principal() -> R<i32> {
    let m = match comando().try_get_matches() {
        Ok(m) => m,
        Err(e) if matches!(e.kind(), ErrorKind::DisplayHelp | ErrorKind::DisplayVersion) => {
            let _ = e.print();
            return Ok(0);
        }
        Err(e) => {
            ui::erro(&traduzir_erro(&e));
            return Ok(2);
        }
    };
    if m.get_flag("versao") || m.subcommand_name() == Some("versao") {
        println!("bora {VERSAO}");
        return Ok(0);
    }
    let fonte =
        fonte::abrir().map_err(|e| Erro::Msg(format!("não consegui abrir o catálogo: {e}")))?;
    match m.subcommand() {
        Some(("diag", s)) => cmd_diag(s),
        Some(("lista", _)) => cmd_lista(&fonte),
        Some(("modelos", s)) => cmd_modelos(s, &fonte),
        Some(("plano", s)) => cmd_plano(s, &fonte),
        Some(("validar", s)) => cmd_validar(s, &fonte),
        Some(("aplicar", s)) => cmd_aplicar(s, &fonte),
        Some(("desfazer", s)) => cmd_desfazer(s),
        Some(("historico", _)) => {
            executor::imprimir_historico();
            Ok(0)
        }
        Some(("ajuda", s)) => cmd_ajuda(s),
        Some(("conferir", _)) => cmd_conferir(&fonte),
        _ => cmd_menu(&fonte),
    }
}

/// Converte o resultado de `principal` em código de saída. Os erros que chegam
/// aqui já foram explicados na tela, ou são mensagens que só faltava mostrar.
fn main() {
    let codigo = match principal() {
        Ok(c) => c,
        Err(Erro::Codigo(c)) => c,
        Err(Erro::Cancelado) => {
            println!();
            println!("Cancelado. Nada foi alterado.");
            1
        }
        Err(Erro::Msg(m)) => {
            ui::erro(&m);
            1
        }
    };
    std::process::exit(codigo);
}
