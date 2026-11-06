//! Testa o bora de ponta a ponta com um catálogo de mentira, sem precisar de root.

use std::fs;
use std::io::Write;
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Output, Stdio};

const RECEITA_YAML: &str = r#"id: teste/{nome}
nome: Receita {nome}
descricao: Cria o arquivo {nome} na pasta de teste.
risco: baixo
precisa_root: false
familias:
  ubuntu: testada
  debian: testada
parametros:
  alvo:
    tipo: caminho
    pergunta: Em que pasta?
  falhar:
    tipo: booleano
    padrao: false
testes:
  - distro: ubuntu
    versao: "26.04"
    data: 2026-11-04
    por: testes
    onde: conteiner
    resultado: ok
"#;

const SCRIPTS: &[(&str, &str)] = &[
    (
        "verificar.sh",
        r#"#!/usr/bin/env bash
set -euo pipefail
source "$BORA_LIB"
[ -f "$BORA_ALVO/{nome}" ] && exit 0
exit 1
"#,
    ),
    (
        "aplicar.sh",
        r#"#!/usr/bin/env bash
set -euo pipefail
source "$BORA_LIB"
echo "aplicar {nome}" >> "$BORA_ALVO/ordem"
echo "familia=$BORA_FAMILIA distro=$BORA_DISTRO" > "$BORA_ALVO/{nome}"
if [ "$BORA_FALHAR" = sim ]; then echo "algo deu errado em 10.20.30.40"; exit 3; fi
msg "criei {nome}"
"#,
    ),
    (
        "testar.sh",
        r#"#!/usr/bin/env bash
set -euo pipefail
source "$BORA_LIB"
conferir "arquivo {nome} existe" test -f "$BORA_ALVO/{nome}"
resultado_dos_testes
"#,
    ),
    (
        "desfazer.sh",
        r#"#!/usr/bin/env bash
set -euo pipefail
source "$BORA_LIB"
echo "desfazer {nome}" >> "${BORA_ALVO:?}/ordem"
rm -f -- "${BORA_ALVO:?}/{nome}"
"#,
    ),
];

const ROLE: &str = r#"id: exemplo
nome: Rolê de exemplo
descricao: Aplica as receitas um e dois.
para_quem: [curiosos]
status: rascunho
familias: [ubuntu]
perguntas:
  - id: pasta
    texto: Onde?
receitas:
  - id: teste/um
    alvo: "{pasta}"
  - id: teste/dois
    alvo: "{pasta}"
pronto_quando: Os dois arquivos existem.
como_desfazer: Apaga os dois arquivos.
"#;

struct Ambiente {
    base: PathBuf,
}

impl Drop for Ambiente {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.base);
    }
}

fn raiz_do_projeto() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR"))
}

impl Ambiente {
    fn novo(nome: &str) -> Ambiente {
        let base = std::env::temp_dir().join(format!("bora-teste-{nome}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&base);
        let catalogo = base.join("catalogo");
        fs::create_dir_all(catalogo.join("objetivos")).unwrap();
        fs::create_dir_all(base.join("alvo")).unwrap();
        fs::copy(
            raiz_do_projeto().join("receitas/comum.sh"),
            catalogo.join("receitas/comum.sh"),
        )
        .or_else(|_| {
            fs::create_dir_all(catalogo.join("receitas"))?;
            fs::copy(
                raiz_do_projeto().join("receitas/comum.sh"),
                catalogo.join("receitas/comum.sh"),
            )
        })
        .unwrap();
        for n in ["um", "dois", "tres"] {
            let pasta = catalogo.join("receitas/teste").join(n);
            fs::create_dir_all(&pasta).unwrap();
            fs::write(
                pasta.join("receita.yaml"),
                RECEITA_YAML.replace("{nome}", n),
            )
            .unwrap();
            for (arquivo, corpo) in SCRIPTS {
                let caminho = pasta.join(arquivo);
                fs::write(&caminho, corpo.replace("{nome}", n)).unwrap();
                fs::set_permissions(&caminho, fs::Permissions::from_mode(0o755)).unwrap();
            }
        }
        fs::write(catalogo.join("objetivos/exemplo.yaml"), ROLE).unwrap();
        Ambiente { base }
    }

    fn alvo(&self) -> PathBuf {
        self.base.join("alvo")
    }

    fn estado(&self) -> PathBuf {
        self.base.join("estado")
    }

    fn comando(&self, args: &[&str], os_release: &str) -> Command {
        let mut c = Command::new(env!("CARGO_BIN_EXE_bora"));
        c.args(args)
            .current_dir(&self.base)
            .env("BORA_RAIZ", self.base.join("catalogo"))
            .env("BORA_DIR_ESTADO", self.estado())
            .env("BORA_DIR_LOG", self.base.join("log"))
            .env(
                "BORA_OS_RELEASE",
                raiz_do_projeto().join("testes/os-release").join(os_release),
            )
            .env("BORA_PERMITIR_SEM_SYSTEMD", "1")
            .env("NO_COLOR", "1");
        c
    }

    fn rodar_com(&self, args: &[&str], entrada: &str, os_release: &str, esperado: i32) -> Output {
        let mut filho = self
            .comando(args, os_release)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()
            .unwrap();
        filho
            .stdin
            .take()
            .unwrap()
            .write_all(entrada.as_bytes())
            .unwrap();
        let saida = filho.wait_with_output().unwrap();
        assert_eq!(
            saida.status.code(),
            Some(esperado),
            "bora {args:?}\n--- saída ---\n{}\n--- erros ---\n{}",
            String::from_utf8_lossy(&saida.stdout),
            String::from_utf8_lossy(&saida.stderr)
        );
        saida
    }

    fn bora(&self, args: &[&str]) -> Output {
        self.rodar_com(args, "", "ubuntu-26.04", 0)
    }

    fn bora_falha(&self, args: &[&str], codigo: i32) -> Output {
        self.rodar_com(args, "", "ubuntu-26.04", codigo)
    }

    fn plano(&self, receitas: &[&str], falhar: Option<&str>, nome: &str) -> String {
        let alvo = self.alvo().display().to_string();
        let lista = receitas.join(",");
        let mut args: Vec<String> = vec![
            "plano".into(),
            "--receitas".into(),
            lista,
            "-o".into(),
            nome.into(),
        ];
        for r in receitas {
            args.push("-p".into());
            args.push(format!("{r}.alvo={alvo}"));
        }
        if let Some(f) = falhar {
            args.push("-p".into());
            args.push(format!("{f}.falhar=sim"));
        }
        let refs: Vec<&str> = args.iter().map(String::as_str).collect();
        self.bora(&refs);
        self.base.join(nome).display().to_string()
    }

    fn ordem(&self) -> Vec<String> {
        fs::read_to_string(self.alvo().join("ordem"))
            .map(|t| t.lines().map(str::to_string).collect())
            .unwrap_or_default()
    }

    fn arquivos(&self) -> Vec<String> {
        let mut v: Vec<String> = fs::read_dir(self.alvo())
            .unwrap()
            .flatten()
            .map(|e| e.file_name().to_string_lossy().to_string())
            .collect();
        v.sort();
        v
    }
}

fn texto(o: &Output) -> String {
    String::from_utf8_lossy(&o.stdout).to_string()
}

fn erros(o: &Output) -> String {
    String::from_utf8_lossy(&o.stderr).to_string()
}

const APLICAR: &[&str] = &["--sem-perguntar", "--sem-snapshot"];

fn aplicar(a: &Ambiente, plano: &str) -> Output {
    let mut args = vec!["aplicar", plano];
    args.extend_from_slice(APLICAR);
    a.bora(&args)
}

#[test]
fn aplicar_de_novo_e_desfazer() {
    let a = Ambiente::novo("ciclo");
    let plano = a.plano(
        &["teste/um", "teste/dois", "teste/tres"],
        None,
        "plano.yaml",
    );
    assert!(texto(&aplicar(&a, &plano)).contains("Pronto"));
    assert_eq!(a.arquivos(), ["dois", "ordem", "tres", "um"]);
    assert!(
        fs::read_to_string(a.alvo().join("um"))
            .unwrap()
            .contains("familia=ubuntu distro=ubuntu")
    );

    assert!(texto(&aplicar(&a, &plano)).contains("Tudo já estava aplicado"));

    a.bora(&["desfazer", "--sem-perguntar"]);
    assert_eq!(
        a.ordem(),
        [
            "aplicar um",
            "aplicar dois",
            "aplicar tres",
            "desfazer tres",
            "desfazer dois",
            "desfazer um"
        ]
    );
    assert_eq!(a.arquivos(), ["ordem"]);
    assert!(texto(&a.bora(&["desfazer", "--sem-perguntar"])).contains("Não há nada para desfazer"));
}

#[test]
fn pula_o_que_ja_estava_aplicado_e_nao_desfaz() {
    let a = Ambiente::novo("pula");
    fs::write(a.alvo().join("dois"), "já existia").unwrap();
    let plano = a.plano(&["teste/um", "teste/dois"], None, "plano.yaml");
    aplicar(&a, &plano);
    assert_eq!(a.ordem(), ["aplicar um"]);
    a.bora(&["desfazer", "--sem-perguntar"]);
    assert_eq!(
        fs::read_to_string(a.alvo().join("dois")).unwrap(),
        "já existia"
    );
    assert_eq!(a.ordem(), ["aplicar um", "desfazer um"]);
}

#[test]
fn falha_no_meio_para_e_desfaz_o_que_mudou() {
    let a = Ambiente::novo("falha");
    let plano = a.plano(
        &["teste/um", "teste/dois", "teste/tres"],
        Some("teste/dois"),
        "plano.yaml",
    );
    let mut args = vec!["aplicar", plano.as_str()];
    args.extend_from_slice(APLICAR);
    let r = a.bora_falha(&args, 1);
    assert!(
        erros(&r).contains("a etapa aplicar falhou (código 3)"),
        "{}",
        erros(&r)
    );
    assert!(!a.alvo().join("tres").exists());

    let pasta = fs::read_dir(a.estado().join("execucoes"))
        .unwrap()
        .flatten()
        .next()
        .unwrap()
        .path();
    let exec: serde_json::Value =
        serde_json::from_str(&fs::read_to_string(pasta.join("execucao.json")).unwrap()).unwrap();
    let situacoes: Vec<&str> = exec["passos"]
        .as_array()
        .unwrap()
        .iter()
        .map(|p| p["situacao"].as_str().unwrap())
        .collect();
    assert_eq!(situacoes, ["aplicada", "falhou", "pendente"]);

    let erro = fs::read_to_string(a.estado().join("ultimo-erro.json")).unwrap();
    assert!(erro.contains("teste/dois"));
    assert!(erro.contains("IP-LOCAL"));
    assert!(!erro.contains("10.20.30.40"));
    assert!(texto(&a.bora(&["ajuda"])).contains("receita teste/dois, na etapa aplicar"));

    a.bora(&["desfazer", "--sem-perguntar"]);
    let ordem = a.ordem();
    assert_eq!(&ordem[ordem.len() - 2..], ["desfazer dois", "desfazer um"]);
    assert_eq!(a.arquivos(), ["ordem"]);
}

#[test]
fn desfaz_da_mais_nova_para_a_mais_antiga() {
    let a = Ambiente::novo("ordem");
    let p1 = a.plano(&["teste/um"], None, "a.yaml");
    aplicar(&a, &p1);
    std::thread::sleep(std::time::Duration::from_millis(1100));
    let p2 = a.plano(&["teste/dois"], None, "b.yaml");
    aplicar(&a, &p2);
    let mut ids: Vec<String> = fs::read_dir(a.estado().join("execucoes"))
        .unwrap()
        .flatten()
        .map(|e| e.file_name().to_string_lossy().to_string())
        .collect();
    ids.sort();
    let r = a.bora_falha(&["desfazer", &ids[0], "--sem-perguntar"], 2);
    assert!(erros(&r).contains("mais recente"));
    a.bora(&["desfazer", "--sem-perguntar"]);
    assert!(!a.alvo().join("dois").exists());
    assert!(a.alvo().join("um").exists());
}

#[test]
fn desfazer_usa_a_copia_da_receita() {
    let a = Ambiente::novo("copia");
    let plano = a.plano(&["teste/um"], None, "plano.yaml");
    aplicar(&a, &plano);
    // Mesmo que a receita mude no catálogo, o desfazer usa a cópia guardada na aplicação.
    fs::write(
        a.base.join("catalogo/receitas/teste/um/desfazer.sh"),
        "#!/usr/bin/env bash\nexit 9\n",
    )
    .unwrap();
    a.bora(&["desfazer", "--sem-perguntar"]);
    assert!(!a.alvo().join("um").exists());
}

#[test]
fn role_com_perguntas() {
    let a = Ambiente::novo("role");
    let resposta = format!("pasta={}", a.alvo().display());
    let r = a.bora(&["plano", "exemplo", "-r", &resposta, "-o", "-"]);
    assert!(texto(&r).contains("objetivo: exemplo"));
    assert!(texto(&r).contains(&format!("alvo: {}", a.alvo().display())));
    let r = a.bora_falha(&["plano", "exemplo", "-o", "-"], 2);
    assert!(erros(&r).contains("falta a resposta"));
}

const ROLE_PERFIS: &str = r#"id: perfis
nome: Rolê com perfis
descricao: A receita dois só entra no perfil completo.
para_quem: [curiosos]
status: rascunho
familias: [ubuntu]
perguntas:
  - id: pasta
    texto: Onde?
  - id: perfil
    texto: Qual perfil?
    opcoes: [simples, completo]
    rotulos:
      simples: só a receita um
      completo: as duas receitas
    padrao: simples
receitas:
  - id: teste/um
    alvo: "{pasta}"
  - id: teste/dois
    quando: {perfil: completo}
    alvo: "{pasta}"
pronto_quando: Os arquivos existem.
como_desfazer: Apaga os arquivos.
"#;

#[test]
fn role_com_perfis() {
    let a = Ambiente::novo("perfis");
    fs::write(a.base.join("catalogo/objetivos/perfis.yaml"), ROLE_PERFIS).unwrap();
    let pasta = format!("pasta={}", a.alvo().display());
    let r = a.bora(&["plano", "perfis", "-r", &pasta, "-o", "-"]);
    assert!(texto(&r).contains("teste/um"), "{}", texto(&r));
    assert!(!texto(&r).contains("teste/dois"), "{}", texto(&r));
    let r = a.bora(&[
        "plano",
        "perfis",
        "-r",
        &pasta,
        "-r",
        "perfil=completo",
        "-o",
        "-",
    ]);
    assert!(texto(&r).contains("teste/dois"), "{}", texto(&r));
    let r = a.bora_falha(
        &[
            "plano",
            "perfis",
            "-r",
            &pasta,
            "-r",
            "perfil=outro",
            "-o",
            "-",
        ],
        2,
    );
    assert!(erros(&r).contains("simples, completo"), "{}", erros(&r));
    // No menu: o rolê com perfis é o segundo; a pasta, o perfil 2 (completo) e salvar.
    let entrada = format!("2\n{}\n2\n3\n", a.alvo().display());
    let r = a.rodar_com(&[], &entrada, "ubuntu-26.04", 0);
    let saida = texto(&r);
    assert!(saida.contains("as duas receitas"), "{saida}");
    let salvo = saida
        .split("Plano salvo em ")
        .nth(1)
        .unwrap()
        .split_whitespace()
        .next()
        .unwrap();
    assert!(
        fs::read_to_string(Path::new(salvo))
            .unwrap()
            .contains("teste/dois")
    );
}

#[test]
fn simular_nao_muda_nada() {
    let a = Ambiente::novo("simular");
    let plano = a.plano(&["teste/um", "teste/dois"], None, "plano.yaml");
    let r = a.bora(&["aplicar", &plano, "--simular"]);
    assert!(
        texto(&r).contains("2 de 2 receitas seriam aplicadas"),
        "{}",
        texto(&r)
    );
    assert!(a.arquivos().is_empty());
}

#[test]
fn menu_com_receitas_avulsas() {
    let a = Ambiente::novo("menu-avulsas");
    // Opção 2 (receitas avulsas, logo depois do rolê), receita 1, a pasta, e 3 (salvar para depois).
    let entrada = format!("2\n1\n{}\n3\n", a.alvo().display());
    let r = a.rodar_com(&[], &entrada, "ubuntu-26.04", 0);
    assert!(texto(&r).contains("Plano salvo em"), "{}", texto(&r));
}

#[test]
fn menu_com_role() {
    let a = Ambiente::novo("menu-role");
    let entrada = format!("1\n{}\n3\n", a.alvo().display());
    let r = a.rodar_com(&[], &entrada, "ubuntu-26.04", 0);
    let saida = texto(&r);
    let salvo = saida
        .split("Plano salvo em ")
        .nth(1)
        .unwrap()
        .split_whitespace()
        .next()
        .unwrap();
    assert!(
        fs::read_to_string(Path::new(salvo))
            .unwrap()
            .contains("objetivo: exemplo")
    );
}

#[test]
fn validar_recusa_plano_ruim() {
    let a = Ambiente::novo("ruim");
    let caminho = a.base.join("ruim.yaml");
    fs::write(
        &caminho,
        "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: teste/nao-existe\n",
    )
    .unwrap();
    let r = a.bora_falha(&["validar", &caminho.display().to_string()], 2);
    assert!(erros(&r).contains("não existe no catálogo"));
}

#[test]
fn distro_fora_do_escopo() {
    let a = Ambiente::novo("mx");
    let r = a.rodar_com(&["plano", "--receitas", "teste/um"], "", "mx-25", 2);
    assert!(erros(&r).contains("MX Linux"));
}

#[test]
fn catalogo_embutido() {
    // Sem BORA_RAIZ, o bora usa as receitas que vêm dentro do binário.
    let saida = Command::new(env!("CARGO_BIN_EXE_bora"))
        .args(["conferir"])
        .env_remove("BORA_RAIZ")
        .env("NO_COLOR", "1")
        .output()
        .unwrap();
    assert!(String::from_utf8_lossy(&saida.stdout).contains("Catálogo em ordem"));
}

#[test]
fn ajuda_e_erros_em_portugues() {
    let a = Ambiente::novo("cli");
    assert!(texto(&a.bora(&["--help"])).contains("Comandos"));
    let r = a.bora_falha(&["inventado"], 2);
    assert!(erros(&r).contains("comando desconhecido"));
}
