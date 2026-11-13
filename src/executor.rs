//! Aplica e desfaz planos, receita por receita, guardando o necessário para voltar atrás.
//!
//! Cada aplicação vira uma **execução**, numa pasta própria:
//!
//! ```text
//! /var/lib/bora/execucoes/20261113-142501/
//!   execucao.json          situação geral e de cada passo
//!   plano.yaml             o plano como foi aplicado
//!   passos/01-base-atualizar/
//!     receita/             cópia da receita (os scripts que rodaram)
//!     comum.sh             cópia das funções comuns
//!     estado/              o que a receita guardou para desfazer ($BORA_ESTADO)
//!     saida.log            tudo o que os scripts escreveram
//! ```
//!
//! A cópia da receita é de propósito: o `desfazer` roda os mesmos scripts que
//! aplicaram, mesmo que o `bora` tenha sido atualizado no meio do caminho.
//!
//! O contrato com os scripts: `verificar.sh` sai com 0 se já está aplicado e 1
//! se precisa aplicar; `aplicar.sh`, `testar.sh` e `desfazer.sh` saem com 0
//! quando dá certo. Os parâmetros chegam como variáveis `BORA_<NOME>`.

use crate::ajuda::{self, UltimoErro};
use crate::catalogo::{Catalogo, Receita, Valor};
use crate::diag::Diag;
use crate::plano::{self, PlanoValidado};
use crate::snapshot;
use crate::ui::{self, Erro, R};
use serde::{Deserialize, Serialize};
use serde_norway::Value;
use std::collections::VecDeque;
use std::fs::{self, File, OpenOptions};
use std::io::{BufRead, BufReader, Write};
use std::os::fd::AsRawFd;
use std::os::unix::fs::{DirBuilderExt, PermissionsExt};
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

/// Variáveis de quem chamou que passam para as receitas.
const HERDADAS: &[&str] = &[
    "PATH",
    "LANG",
    "LANGUAGE",
    "LC_ALL",
    "LC_MESSAGES",
    "TERM",
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "no_proxy",
    "NO_PROXY",
    "BORA_PERMITIR_SEM_SYSTEMD",
];
/// O `PATH` de sistema, para os scripts acharem `apt`, `ufw` e companhia mesmo
/// quando o `sudo` entrega um `PATH` curto.
const PATH_PADRAO: &str = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin";

/// Onde o `bora` guarda as execuções. `BORA_DIR_ESTADO` muda isso nos testes,
/// para não precisar de root nem sujar `/var/lib`.
pub fn dir_estado() -> PathBuf {
    std::env::var_os("BORA_DIR_ESTADO")
        .map(PathBuf::from)
        .unwrap_or_else(|| "/var/lib/bora".into())
}

/// Onde fica o log geral. `BORA_DIR_LOG` muda isso nos testes.
pub fn dir_log() -> PathBuf {
    std::env::var_os("BORA_DIR_LOG")
        .map(PathBuf::from)
        .unwrap_or_else(|| "/var/log/bora".into())
}

/// Data e hora local, no formato dos registros.
fn agora() -> String {
    chrono::Local::now().format("%Y-%m-%dT%H:%M:%S").to_string()
}

/// Se o `bora` está rodando como root.
pub fn e_root() -> bool {
    // SAFETY: geteuid não tem pré-condições.
    unsafe { libc::geteuid() == 0 }
}

/// Impede duas execuções do bora ao mesmo tempo.
pub struct Trava(#[allow(dead_code)] File);

impl Trava {
    /// Pega a trava em `/var/lib/bora/bora.trava`, sem esperar. O `flock` solta
    /// sozinho quando o processo termina, até se ele cair no meio.
    pub fn pegar() -> R<Trava> {
        fs::create_dir_all(dir_estado())?;
        let f = OpenOptions::new()
            .create(true)
            .truncate(false)
            .write(true)
            .open(dir_estado().join("bora.trava"))?;
        // SAFETY: o descritor é válido enquanto f existir.
        if unsafe { libc::flock(f.as_raw_fd(), libc::LOCK_EX | libc::LOCK_NB) } != 0 {
            return Err("outro bora já está rodando nesta máquina; espere ele terminar".into());
        }
        Ok(Trava(f))
    }
}

/// O log geral, em /var/log/bora/bora.log.
fn registrar(texto: &str) {
    let caminho = dir_log().join("bora.log");
    if let Some(p) = caminho.parent() {
        let _ = fs::create_dir_all(p);
    }
    if let Ok(mut f) = OpenOptions::new().create(true).append(true).open(caminho) {
        let _ = writeln!(f, "{} {texto}", agora());
    }
}

/// Um passo da execução, como fica no `execucao.json`. A `situacao` vai de
/// "pendente" para "ja-aplicada", "pulada", "aplicando", "aplicada", "falhou",
/// "desfeita" ou "erro-ao-desfazer". `pasta` é o nome da pasta do passo.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PassoExec {
    pub receita: String,
    pub parametros: Vec<(String, serde_json::Value)>,
    pub pasta: String,
    pub precisa_root: bool,
    pub situacao: String,
    pub inicio: Option<String>,
    pub fim: Option<String>,
    pub mensagem: String,
}

impl PassoExec {
    /// Os parâmetros de volta como `Valor`, para montar o ambiente do desfazer.
    fn valores(&self) -> Vec<(String, Valor)> {
        self.parametros
            .iter()
            .map(|(k, v)| (k.clone(), Valor::de_json(v)))
            .collect()
    }
}

/// O conteúdo do `execucao.json`. A `situacao` geral vai de "em-andamento" para
/// "concluida", "falhou", "sem-mudancas", "desfeita" ou "desfeita-em-parte".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DadosExec {
    pub id: String,
    pub inicio: String,
    pub fim: Option<String>,
    pub objetivo: Option<String>,
    pub familia: String,
    pub snapshot: Option<String>,
    pub situacao: String,
    pub passos: Vec<PassoExec>,
}

/// Uma execução: a pasta dela e os dados do `execucao.json`.
pub struct Execucao {
    pub pasta: PathBuf,
    pub dados: DadosExec,
}

impl Execucao {
    /// Cria a pasta da execução, com o id tirado da data e hora (e um número no
    /// fim se duas caírem no mesmo segundo), e grava o plano e os passos pendentes.
    fn nova(pv: &PlanoValidado, cru: &Value) -> R<Execucao> {
        let base = dir_estado().join("execucoes");
        fs::create_dir_all(&base)?;
        let _ = fs::set_permissions(dir_estado(), fs::Permissions::from_mode(0o755));
        let carimbo = chrono::Local::now().format("%Y%m%d-%H%M%S").to_string();
        let mut id = carimbo.clone();
        let mut n = 1;
        while base.join(&id).exists() {
            n += 1;
            id = format!("{carimbo}-{n}");
        }
        let pasta = base.join(&id);
        fs::DirBuilder::new().mode(0o700).create(&pasta)?;
        fs::write(pasta.join("plano.yaml"), plano::para_texto(cru))?;
        let passos = pv
            .passos
            .iter()
            .enumerate()
            .map(|(i, p)| PassoExec {
                receita: p.receita.id.clone(),
                parametros: p
                    .parametros
                    .iter()
                    .map(|(k, v)| (k.clone(), v.para_json()))
                    .collect(),
                pasta: format!("{:02}-{}", i + 1, p.receita.id.replace('/', "-")),
                precisa_root: p.receita.precisa_root,
                situacao: "pendente".into(),
                inicio: None,
                fim: None,
                mensagem: String::new(),
            })
            .collect();
        let e = Execucao {
            pasta,
            dados: DadosExec {
                id,
                inicio: agora(),
                fim: None,
                objetivo: pv.objetivo.clone(),
                familia: pv.familia.clone(),
                snapshot: None,
                situacao: "em-andamento".into(),
                passos,
            },
        };
        e.salvar()?;
        Ok(e)
    }

    /// Lê uma execução do disco. Pasta sem `execucao.json` legível é ignorada.
    fn carregar(pasta: &Path) -> Option<Execucao> {
        let texto = fs::read_to_string(pasta.join("execucao.json")).ok()?;
        Some(Execucao {
            pasta: pasta.to_path_buf(),
            dados: serde_json::from_str(&texto).ok()?,
        })
    }

    /// Grava o `execucao.json` num arquivo temporário e troca de nome depois.
    /// Assim, se a energia cair no meio, fica o arquivo velho inteiro, nunca um pela metade.
    fn salvar(&self) -> R<()> {
        let tmp = self.pasta.join("execucao.json.tmp");
        fs::write(
            &tmp,
            serde_json::to_string_pretty(&self.dados).map_err(|e| e.to_string())?,
        )?;
        fs::rename(tmp, self.pasta.join("execucao.json"))?;
        Ok(())
    }

    /// A pasta do passo `i`.
    fn pasta_passo(&self, i: usize) -> PathBuf {
        self.pasta.join("passos").join(&self.dados.passos[i].pasta)
    }

    /// Marca a situação final e a hora do fim.
    fn encerrar(&mut self, situacao: &str) -> R<()> {
        self.dados.situacao = situacao.into();
        self.dados.fim = Some(agora());
        self.salvar()
    }
}

/// Todas as execuções, da mais antiga para a mais nova. O id começa pela data,
/// então a ordem alfabética das pastas já é a ordem do tempo.
pub fn listar_execucoes() -> Vec<Execucao> {
    let base = dir_estado().join("execucoes");
    let mut pastas: Vec<PathBuf> = fs::read_dir(base)
        .map(|r| r.flatten().map(|e| e.path()).collect())
        .unwrap_or_default();
    pastas.sort();
    pastas
        .iter()
        .filter_map(|p| Execucao::carregar(p))
        .collect()
}

/// A execução mais recente que ainda não foi desfeita por completo.
pub fn ultima_desfazivel() -> Option<Execucao> {
    listar_execucoes()
        .into_iter()
        .rev()
        .find(|e| !["desfeita", "sem-mudancas"].contains(&e.dados.situacao.as_str()))
}

/// A pessoa que chamou o bora: quem rodou o sudo, ou o próprio usuário, se
/// não for root. Vazio quando o bora foi aberto direto como root.
fn pessoa() -> String {
    let valida = |v: &str| !v.is_empty() && v != "root" && !v.contains(['/', ':', '\n']);
    if let Ok(v) = std::env::var("SUDO_USER")
        && valida(&v)
    {
        return v;
    }
    if !e_root() {
        for var in ["USER", "LOGNAME"] {
            if let Ok(v) = std::env::var(var)
                && valida(&v)
            {
                return v;
            }
        }
    }
    String::new()
}

/// Monta as variáveis de ambiente dos scripts. O ambiente começa vazio
/// (`env_clear` em `rodar`): só passam as variáveis de `HERDADAS`, mais as do
/// `bora` (`BORA_FAMILIA`, `BORA_ESTADO`, `BORA_LIB`...) e um `BORA_<NOME>` por
/// parâmetro. Assim nenhuma variável estranha de quem chamou muda a receita.
fn ambiente(
    params: &[(String, Valor)],
    familia: &str,
    d: &Diag,
    estado: &Path,
    lib: &Path,
) -> Vec<(String, String)> {
    let mut env: Vec<(String, String)> = HERDADAS
        .iter()
        .filter_map(|k| std::env::var(k).ok().map(|v| (k.to_string(), v)))
        .collect();
    match env.iter_mut().find(|(k, _)| k == "PATH") {
        Some((_, v)) if !v.contains("/sbin") => *v = format!("{PATH_PADRAO}:{v}"),
        Some(_) => {}
        None => env.push(("PATH".into(), PATH_PADRAO.into())),
    }
    let home = if e_root() {
        "/root".into()
    } else {
        std::env::var("HOME").unwrap_or_else(|_| "/tmp".into())
    };
    env.extend([
        ("HOME".to_string(), home),
        ("DEBIAN_FRONTEND".into(), "noninteractive".into()),
        ("BORA_FAMILIA".into(), familia.into()),
        ("BORA_DISTRO".into(), d.distro.id.clone()),
        ("BORA_VERSAO".into(), d.distro.versao.clone()),
        (
            "BORA_BASE".into(),
            d.distro.base.clone().unwrap_or_default(),
        ),
        ("BORA_ESTADO".into(), estado.display().to_string()),
        ("BORA_LIB".into(), lib.display().to_string()),
        ("BORA_PESSOA".into(), pessoa()),
    ]);
    for (nome, valor) in params {
        env.push((
            format!("BORA_{}", nome.to_uppercase()),
            valor.para_ambiente(),
        ));
    }
    env
}

/// Roda um script da receita, mostrando e guardando a saída. Devolve o código e as últimas linhas.
fn rodar(
    script: &Path,
    env: &[(String, String)],
    cwd: &Path,
    log: &Path,
    mostrar: bool,
) -> (i32, Vec<String>) {
    let mut ultimas: VecDeque<String> = VecDeque::with_capacity(60);
    if let Some(p) = log.parent() {
        let _ = fs::create_dir_all(p);
    }
    let mut saida_log = OpenOptions::new().create(true).append(true).open(log).ok();
    let mut escrever = |linha: &str| {
        if let Some(f) = saida_log.as_mut() {
            let _ = writeln!(f, "{linha}");
        }
    };
    escrever(&format!(
        "### {} em {}",
        script.file_name().unwrap_or_default().to_string_lossy(),
        agora()
    ));
    // A saída e os erros do script vão para o mesmo cano, na ordem em que
    // saem. Cada linha vai para o log, para a tela (se `mostrar`) e para as
    // últimas 60, que viram a mensagem de erro e o `bora ajuda`.
    let (leitor, escritor) = match std::io::pipe() {
        Ok(p) => p,
        Err(e) => return (126, vec![e.to_string()]),
    };
    let escritor_erro = match escritor.try_clone() {
        Ok(e) => e,
        Err(e) => return (126, vec![e.to_string()]),
    };
    let filho = Command::new(script)
        .current_dir(cwd)
        .env_clear()
        .envs(env.iter().map(|(k, v)| (k, v)))
        .stdin(Stdio::null())
        .stdout(escritor)
        .stderr(escritor_erro)
        .spawn();
    let mut filho = match filho {
        Ok(f) => f,
        Err(e) => {
            escrever(&format!("erro ao rodar: {e}"));
            return (126, vec![e.to_string()]);
        }
    };
    let mut buf = Vec::new();
    let mut leitor = BufReader::new(leitor);
    loop {
        buf.clear();
        match leitor.read_until(b'\n', &mut buf) {
            Ok(0) | Err(_) => break,
            Ok(_) => {}
        }
        let bruta = String::from_utf8_lossy(&buf);
        let bruta = bruta.trim_end_matches('\n').trim_end_matches('\r');
        // Barras de progresso reescrevem a linha com \r; fica só a última versão.
        let linha = bruta.rsplit('\r').next().unwrap_or("").to_string();
        escrever(&linha);
        if mostrar {
            println!("{}{linha}", ui::apagado("  │ "));
        }
        if ultimas.len() == 60 {
            ultimas.pop_front();
        }
        ultimas.push_back(linha);
    }
    let codigo = filho.wait().ok().and_then(|s| s.code()).unwrap_or(1);
    escrever(&format!("### código de saída: {codigo}"));
    (codigo, ultimas.into())
}

/// Copia uma pasta inteira, recursivamente.
fn copiar_pasta(de: &Path, para: &Path) -> std::io::Result<()> {
    fs::create_dir_all(para)?;
    for e in fs::read_dir(de)? {
        let e = e?;
        let destino = para.join(e.file_name());
        if e.file_type()?.is_dir() {
            copiar_pasta(&e.path(), &destino)?;
        } else {
            fs::copy(e.path(), &destino)?;
        }
    }
    Ok(())
}

/// Guarda uma cópia da receita, para desfazer com os mesmos scripts que aplicaram.
fn copiar_receita(rec: &Receita, destino: &Path, lib: &Path) -> R<()> {
    if destino.exists() {
        fs::remove_dir_all(destino)?;
    }
    copiar_pasta(&rec.pasta, destino)?;
    fs::copy(lib, destino.parent().unwrap().join("comum.sh"))?;
    Ok(())
}

/// Recusa o plano se alguma receita precisa de root e o `bora` não está como root.
pub fn conferir_root(pv: &PlanoValidado) -> R<()> {
    if pv.passos.iter().any(|p| p.receita.precisa_root) && !e_root() {
        return Err(
            "este plano muda o sistema; rode com sudo, por exemplo: sudo bora aplicar plano.yaml"
                .into(),
        );
    }
    Ok(())
}

/// Guarda o erro de um passo para o `bora ajuda`, com as últimas 40 linhas
/// da saída já limpas de dados pessoais.
fn guardar_erro(d: &DadosExec, i: usize, etapa: &str, ultimas: &[String]) {
    let p = &d.passos[i];
    let inicio = ultimas.len().saturating_sub(40);
    ajuda::guardar_erro(UltimoErro {
        execucao: d.id.clone(),
        objetivo: d.objetivo.clone(),
        receita: p.receita.clone(),
        parametros: p
            .valores()
            .into_iter()
            .map(|(k, v)| (k, v.to_string()))
            .collect(),
        etapa: etapa.into(),
        saida: ajuda::limpar(&ultimas[inicio..].join("\n")),
    });
}

/// Roda só o verificar de cada receita e conta o que mudaria.
pub fn simular(pv: &PlanoValidado, d: &Diag, c: &Catalogo) -> R<usize> {
    conferir_root(pv)?;
    let _trava = Trava::pegar()?;
    ui::titulo("Simulação: nada será alterado");
    let tmp = dir_estado().join("simulacao");
    fs::create_dir_all(&tmp)?;
    let mut mudariam = 0;
    for (i, p) in pv.passos.iter().enumerate() {
        let env = ambiente(&p.parametros, &pv.familia, d, &tmp, &c.lib());
        let script = p.receita.pasta.join(Receita::nome_do_script(
            &p.receita.pasta,
            "verificar",
            &pv.familia,
        ));
        let (codigo, ultimas) = rodar(
            &script,
            &env,
            &p.receita.pasta,
            &dir_log().join("simulacao.log"),
            false,
        );
        let n = i + 1;
        match codigo {
            0 => ui::ok(&format!("{n}. {}: já está aplicada", p.receita.nome)),
            1 => {
                mudariam += 1;
                ui::aviso(&format!("{n}. {}: vai ser aplicada", p.receita.nome));
                for l in ultimas.iter().rev().take(5).rev() {
                    ui::info(&ui::apagado(l));
                }
            }
            _ => {
                ui::erro(&format!(
                    "{n}. {}: a verificação falhou (código {codigo})",
                    p.receita.nome
                ));
                for l in ultimas.iter().rev().take(10).rev() {
                    ui::info(l);
                }
            }
        }
    }
    Ok(mudariam)
}

/// As opções do `bora aplicar` que mudam o jeito de aplicar.
pub struct Opcoes {
    pub sem_snapshot: bool,
    pub passo_a_passo: bool,
    pub perguntar: bool,
}

/// Aplica o plano. Devolve a situação final da execução.
pub fn aplicar(pv: &PlanoValidado, cru: &Value, d: &Diag, c: &Catalogo, op: &Opcoes) -> R<String> {
    conferir_root(pv)?;
    let _trava = Trava::pegar()?;
    let mut e = Execucao::nova(pv, cru)?;
    let id = e.dados.id.clone();
    registrar(&format!(
        "aplicar {id}: início ({} passos)",
        pv.passos.len()
    ));
    ui::titulo(&format!("Aplicando o plano ({id})"));

    // Fase 1: copia cada receita para a pasta da execução e roda o verificar.
    // Se algum verificar quebra, nada mudou ainda, e o bora para por aqui.
    // Primeiro, o que já está aplicado.
    let mut pendentes: Vec<String> = Vec::new();
    for (i, p) in pv.passos.iter().enumerate() {
        let pasta = e.pasta_passo(i);
        copiar_receita(&p.receita, &pasta.join("receita"), &c.lib())?;
        fs::create_dir_all(pasta.join("estado"))?;
        let env = ambiente(
            &p.parametros,
            &pv.familia,
            d,
            &pasta.join("estado"),
            &pasta.join("comum.sh"),
        );
        let copia = pasta.join("receita");
        let script = copia.join(Receita::nome_do_script(&copia, "verificar", &pv.familia));
        let (codigo, ultimas) = rodar(&script, &env, &copia, &pasta.join("saida.log"), false);
        match codigo {
            0 => e.dados.passos[i].situacao = "ja-aplicada".into(),
            1 => pendentes.push(p.receita.id.clone()),
            _ => {
                e.dados.passos[i].situacao = "falhou".into();
                e.dados.passos[i].mensagem = format!("a verificação falhou com código {codigo}");
                e.encerrar("falhou")?;
                guardar_erro(&e.dados, i, "verificar", &ultimas);
                registrar(&format!(
                    "aplicar {id}: {} verificar falhou ({codigo})",
                    p.receita.id
                ));
                for l in ultimas.iter().rev().take(10).rev() {
                    ui::info(l);
                }
                return Err(format!(
                    "a verificação de {} falhou antes de qualquer mudança. Rode bora ajuda para montar uma pergunta com o erro.",
                    p.receita.id
                )
                .into());
            }
        }
    }
    e.salvar()?;

    if pendentes.is_empty() {
        e.encerrar("sem-mudancas")?;
        ui::ok("Tudo já estava aplicado. Nada mudou.");
        registrar(&format!("aplicar {id}: nada a fazer"));
        return Ok("sem-mudancas".into());
    }

    // Fase 2: snapshot do sistema antes da primeira mudança. Se ele falha,
    // o bora para sem mudar nada. Sem ferramenta de snapshot, pergunta.
    // Snapshot do sistema antes da primeira mudança.
    if op.sem_snapshot {
        ui::aviso("Sem snapshot do sistema, como você pediu. Cada receita ainda sabe se desfazer.");
    } else if matches!(snapshot::ferramenta(), Some("timeshift") | Some("snapper")) {
        ui::info(
            "Criando um snapshot do sistema antes de mudar qualquer coisa. Pode levar alguns minutos.",
        );
        match snapshot::criar(&format!("bora {id}, antes de aplicar")) {
            Ok(nome) => {
                ui::ok(&format!("Snapshot criado: {nome}"));
                registrar(&format!("aplicar {id}: snapshot {nome}"));
                e.dados.snapshot = Some(nome);
                e.salvar()?;
            }
            Err(falha) => {
                e.encerrar("sem-mudancas")?;
                return Err(
                    format!("não consegui criar o snapshot: {falha}. Nada foi alterado.").into(),
                );
            }
        }
    } else {
        let vai_configurar = pendentes.iter().any(|p| p == "sistema/snapshot");
        ui::aviso("Esta máquina ainda não tem snapshot do sistema configurado.");
        if vai_configurar {
            ui::info(
                "O plano configura o snapshot; a partir dele, as próximas mudanças terão um ponto de volta.",
            );
        }
        ui::info(
            "Cada receita sabe se desfazer, mas sem snapshot não há como voltar o sistema inteiro.",
        );
        if op.perguntar && !ui::confirmar("Continuar mesmo assim?", vai_configurar)? {
            e.encerrar("sem-mudancas")?;
            return Err(Erro::Cancelado);
        }
    }

    // Fase 3: aplica e testa cada receita pendente, na ordem do plano. A
    // situação é salva antes e depois de cada etapa: se a máquina desligar no
    // meio, o `desfazer` sabe até onde foi ("aplicando" também é desfeito).
    let total = pv.passos.len();
    for (i, p) in pv.passos.iter().enumerate() {
        let rotulo = format!("[{}/{total}] {}", i + 1, p.receita.nome);
        if e.dados.passos[i].situacao == "ja-aplicada" {
            ui::ok(&format!("{rotulo}: já estava aplicada"));
            continue;
        }
        ui::titulo(&rotulo);
        if op.passo_a_passo {
            for secao in ["O que faz", "O que muda no sistema"] {
                let texto = p.receita.secao_leiame(secao);
                if !texto.is_empty() {
                    println!("{}", ui::negrito(secao));
                    println!("{texto}");
                }
            }
            if !ui::confirmar("Aplicar esta etapa?", true)? {
                e.dados.passos[i].situacao = "pulada".into();
                e.salvar()?;
                continue;
            }
        }
        let pasta = e.pasta_passo(i);
        let env = ambiente(
            &p.parametros,
            &pv.familia,
            d,
            &pasta.join("estado"),
            &pasta.join("comum.sh"),
        );
        let copia = pasta.join("receita");
        e.dados.passos[i].inicio = Some(agora());
        e.dados.passos[i].situacao = "aplicando".into();
        e.salvar()?;
        registrar(&format!("aplicar {id}: {} início", p.receita.id));

        for etapa in ["aplicar", "testar"] {
            let script = copia.join(Receita::nome_do_script(&copia, etapa, &pv.familia));
            let (codigo, ultimas) = rodar(&script, &env, &copia, &pasta.join("saida.log"), true);
            if codigo != 0 {
                let passo = &mut e.dados.passos[i];
                passo.situacao = "falhou".into();
                passo.fim = Some(agora());
                passo.mensagem = format!("{etapa} falhou com código {codigo}");
                e.encerrar("falhou")?;
                guardar_erro(&e.dados, i, etapa, &ultimas);
                registrar(&format!(
                    "aplicar {id}: {} {etapa} falhou ({codigo})",
                    p.receita.id
                ));
                return Err(format!(
                    "{}: a etapa {etapa} falhou (código {codigo}). Para voltar ao estado anterior: sudo bora desfazer. Para pedir ajuda a uma IA: bora ajuda.",
                    p.receita.nome
                )
                .into());
            }
            if etapa == "aplicar" {
                e.dados.passos[i].situacao = "aplicada".into();
                e.salvar()?;
            }
        }
        e.dados.passos[i].fim = Some(agora());
        e.salvar()?;
        ui::ok(&format!("{}: aplicada e testada", p.receita.nome));
        registrar(&format!("aplicar {id}: {} ok", p.receita.id));
    }
    e.encerrar("concluida")?;
    registrar(&format!("aplicar {id}: concluída"));
    Ok("concluida".into())
}

/// Desfaz os passos de uma execução, do último para o primeiro.
pub fn desfazer(mut e: Execucao, d: &Diag, perguntar: bool) -> R<bool> {
    if e.dados.passos.iter().any(|p| p.precisa_root) && !e_root() {
        return Err("desfazer muda o sistema; rode com sudo: sudo bora desfazer".into());
    }
    let _trava = Trava::pegar()?;
    let id = e.dados.id.clone();
    // Só desfaz o que pode ter mudado algo e ainda tem a cópia da receita.
    // "erro-ao-desfazer" entra para dar para tentar de novo depois de corrigir.
    let alvos: Vec<usize> = (0..e.dados.passos.len())
        .filter(|&i| {
            ["aplicada", "aplicando", "falhou", "erro-ao-desfazer"]
                .contains(&e.dados.passos[i].situacao.as_str())
                && e.pasta_passo(i).join("receita").exists()
        })
        .collect();
    if alvos.is_empty() {
        e.dados.situacao = "desfeita".into();
        e.salvar()?;
        ui::ok("Esta execução não mudou nada que precise ser desfeito.");
        return Ok(true);
    }
    ui::titulo(&format!("Desfazendo a execução {id}"));
    for &i in alvos.iter().rev() {
        println!("  - {}", e.dados.passos[i].receita);
    }
    if perguntar && !ui::confirmar("Desfazer estas receitas, da última para a primeira?", true)? {
        return Err(Erro::Cancelado);
    }
    registrar(&format!("desfazer {id}: início"));
    // Desfaz de trás para a frente. Se um desfazer falha, para: os anteriores
    // podem depender deste, e seguir em frente pioraria a bagunça.
    let mut tudo_certo = true;
    for &i in alvos.iter().rev() {
        let pasta = e.pasta_passo(i);
        let receita = pasta.join("receita");
        let env = ambiente(
            &e.dados.passos[i].valores(),
            &e.dados.familia,
            d,
            &pasta.join("estado"),
            &pasta.join("comum.sh"),
        );
        let script = receita.join(Receita::nome_do_script(
            &receita,
            "desfazer",
            &e.dados.familia,
        ));
        let nome = e.dados.passos[i].receita.clone();
        ui::titulo(&format!("Desfazendo {nome}"));
        let (codigo, ultimas) = rodar(&script, &env, &receita, &pasta.join("saida.log"), true);
        if codigo == 0 {
            e.dados.passos[i].situacao = "desfeita".into();
            ui::ok(&format!("{nome}: desfeita"));
            registrar(&format!("desfazer {id}: {nome} ok"));
            e.salvar()?;
        } else {
            e.dados.passos[i].situacao = "erro-ao-desfazer".into();
            e.dados.passos[i].mensagem = format!("desfazer falhou com código {codigo}");
            tudo_certo = false;
            guardar_erro(&e.dados, i, "desfazer", &ultimas);
            registrar(&format!("desfazer {id}: {nome} falhou ({codigo})"));
            ui::erro(&format!(
                "{nome}: não consegui desfazer (código {codigo}). Parei aqui."
            ));
            break;
        }
    }
    e.dados.situacao = if tudo_certo {
        "desfeita"
    } else {
        "desfeita-em-parte"
    }
    .into();
    e.salvar()?;
    if !tudo_certo {
        if let (Some(s), Some(como)) = (&e.dados.snapshot, snapshot::como_restaurar()) {
            ui::info(&format!(
                "O snapshot {s} ainda permite voltar o sistema inteiro: {como}"
            ));
        }
        ui::info(
            "Depois de corrigir, rode sudo bora desfazer de novo; ele continua de onde parou.",
        );
    }
    Ok(tudo_certo)
}

/// `bora historico`: uma linha por execução e uma por passo, com a situação.
pub fn imprimir_historico() {
    let execucoes = listar_execucoes();
    if execucoes.is_empty() {
        println!("Nenhum plano foi aplicado nesta máquina ainda.");
        return;
    }
    for e in execucoes {
        let d = &e.dados;
        let situacao = match d.situacao.as_str() {
            "em-andamento" => "em andamento ou interrompida",
            "concluida" => "concluída",
            "falhou" => "falhou",
            "desfeita" => "desfeita",
            "desfeita-em-parte" => "desfeita em parte",
            "sem-mudancas" => "sem mudanças",
            outra => outra,
        };
        println!(
            "{}  {situacao:<28} {}",
            d.id,
            d.objetivo.as_deref().unwrap_or("receitas avulsas")
        );
        for p in &d.passos {
            println!(
                "{}",
                ui::apagado(&format!("    {:<16} {}", p.situacao, p.receita))
            );
        }
    }
}
