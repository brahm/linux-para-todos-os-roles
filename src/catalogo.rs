//! Leitura e conferência do catálogo: receitas e rolês.
//!
//! - Uma **receita** é uma pasta em `receitas/<area>/<nome>/` com um
//!   `receita.yaml` (o que é, parâmetros, famílias, testes), um `LEIAME.md` e
//!   quatro scripts: `verificar.sh`, `aplicar.sh`, `testar.sh` e `desfazer.sh`.
//!   O contrato completo está em `receitas/README.md`.
//! - Um **rolê** é um arquivo em `objetivos/<id>.yaml`: perguntas para a pessoa
//!   e a lista de receitas que entram, com parâmetros e condições.
//!
//! A leitura é tolerante: uma receita com erro fica de fora e o erro vai para
//! `Catalogo::erros`, sem derrubar as outras. O `bora conferir` e o `cargo test`
//! exigem a lista vazia.

use crate::diag::Diag;
use regex::Regex;
use serde_norway::{Mapping, Value};
use std::fmt;
use std::fs;
use std::net::IpAddr;
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

// Os valores aceitos em cada campo do YAML. Para criar uma família, um nível
// ou um tipo de parâmetro, comece por aqui e depois ensine o resto do código.

/// As famílias de distro. `diag` decide a família da máquina a partir do `os-release`.
pub const FAMILIAS: &[&str] = &[
    "ubuntu",
    "debian",
    "fedora",
    "arch",
    "fedora-imutavel",
    "opensuse",
];
/// Quanto uma receita foi testada numa família, do mais confiável ao que nem existe.
pub const NIVEIS: &[&str] = &[
    "testada",
    "herdada",
    "comunidade",
    "planejada",
    "nao-se-aplica",
];
/// Os níveis em que o `bora` aceita aplicar a receita.
pub const NIVEIS_APLICAVEIS: &[&str] = &["testada", "herdada", "comunidade"];
const RISCOS: &[&str] = &["baixo", "medio", "alto"];
const TIPOS: &[&str] = &[
    "escolha", "lista", "cidr", "texto", "booleano", "inteiro", "caminho",
];
const PUBLICOS: &[&str] = &["curiosos", "estudantes", "entusiastas"];
const STATUS_ROLE: &[&str] = &["planejado", "rascunho", "testado"];
/// Os quatro scripts que toda receita precisa ter.
const SCRIPTS: &[&str] = &["verificar", "aplicar", "testar", "desfazer"];
/// As seções obrigatórias do `LEIAME.md` de cada receita. O teste
/// `leiame_com_todas_as_secoes` confere todas; o `--passo-a-passo` mostra duas.
#[cfg_attr(not(test), allow(dead_code))]
pub const SECOES_LEIAME: &[&str] = &[
    "O que faz",
    "Por que",
    "O que muda no sistema",
    "Como conferir",
    "Como desfazer",
    "Fontes",
];

// Formatos de id: receita é `area/nome`, rolê é `nome`, parâmetro é `nome_com_sublinhado`.
static ID_RECEITA: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"^[a-z0-9-]+/[a-z0-9-]+$").unwrap());
static ID_ROLE: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[a-z0-9-]+$").unwrap());
static ID_PARAM: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"^[a-z][a-z0-9_]*$").unwrap());
// `{pergunta}` dentro de um parâmetro de rolê: vira a resposta da pergunta.
pub static REFERENCIA: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\{([a-z_][a-z0-9_]*)\}").unwrap());

/// Um valor de parâmetro, já conferido.
#[derive(Debug, Clone, PartialEq)]
pub enum Valor {
    Texto(String),
    Booleano(bool),
    Inteiro(i64),
}

impl fmt::Display for Valor {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Valor::Texto(s) => write!(f, "{s}"),
            Valor::Booleano(true) => write!(f, "sim"),
            Valor::Booleano(false) => write!(f, "não"),
            Valor::Inteiro(n) => write!(f, "{n}"),
        }
    }
}

impl Valor {
    /// Como o valor chega à receita, na variável de ambiente.
    pub fn para_ambiente(&self) -> String {
        match self {
            Valor::Booleano(true) => "sim".into(),
            Valor::Booleano(false) => "nao".into(),
            outro => outro.to_string(),
        }
    }

    /// Para o registro da execução, em JSON.
    pub fn para_json(&self) -> serde_json::Value {
        match self {
            Valor::Texto(s) => serde_json::Value::String(s.clone()),
            Valor::Booleano(b) => serde_json::Value::Bool(*b),
            Valor::Inteiro(n) => serde_json::Value::Number((*n).into()),
        }
    }

    /// O caminho de volta, ao ler o registro de uma execução antiga.
    pub fn de_json(v: &serde_json::Value) -> Valor {
        match v {
            serde_json::Value::Bool(b) => Valor::Booleano(*b),
            serde_json::Value::Number(n) => Valor::Inteiro(n.as_i64().unwrap_or(0)),
            serde_json::Value::String(s) => Valor::Texto(s.clone()),
            outro => Valor::Texto(outro.to_string()),
        }
    }
}

/// Texto de um valor YAML simples, como a pessoa escreveu.
pub fn texto_de(v: &Value) -> Option<String> {
    match v {
        Value::String(s) => Some(s.clone()),
        Value::Bool(b) => Some(b.to_string()),
        Value::Number(n) => Some(n.to_string()),
        Value::Null => None,
        _ => None,
    }
}

/// Faixas de endereço de rede local (RFC 1918 e IPv6 de uso local).
const REDES_LOCAIS: &[(&str, u8)] = &[
    ("10.0.0.0", 8),
    ("172.16.0.0", 12),
    ("192.168.0.0", 16),
    ("fc00::", 7),
];

/// O endereço como número, e quantos bits ele tem (32 no IPv4, 128 no IPv6).
fn bits(ip: &IpAddr) -> (u128, u8) {
    match ip {
        IpAddr::V4(v) => (u32::from(*v) as u128, 32),
        IpAddr::V6(v) => (u128::from(*v), 128),
    }
}

/// A máscara de rede com `prefixo` bits ligados à esquerda. Exemplo: prefixo
/// 24 em 32 bits dá 255.255.255.0. O prefixo 0 é tratado à parte porque o
/// deslocamento de 32 ou 128 bits estoura.
fn mascara(prefixo: u8, largura: u8) -> u128 {
    if prefixo == 0 {
        0
    } else {
        let todos: u128 = if largura == 128 {
            u128::MAX
        } else {
            (1u128 << largura) - 1
        };
        todos & !((1u128 << (largura - prefixo)) - 1)
    }
}

/// Confere uma rede em CIDR e devolve a forma normalizada (endereço da rede).
pub fn rede_local(texto: &str) -> Result<String, ()> {
    let (ip, prefixo) = texto.split_once('/').ok_or(())?;
    let ip: IpAddr = ip.trim().parse().map_err(|_| ())?;
    let prefixo: u8 = prefixo.trim().parse().map_err(|_| ())?;
    let (valor, largura) = bits(&ip);
    if prefixo > largura {
        return Err(());
    }
    let rede = valor & mascara(prefixo, largura);
    let local = REDES_LOCAIS.iter().any(|(base, p)| {
        let base: IpAddr = base.parse().unwrap();
        let (b, l) = bits(&base);
        l == largura && prefixo >= *p && (rede & mascara(*p, l)) == b
    });
    if !local {
        return Err(());
    }
    let endereco = match ip {
        IpAddr::V4(_) => IpAddr::V4((rede as u32).into()).to_string(),
        IpAddr::V6(_) => IpAddr::V6(rede.into()).to_string(),
    };
    Ok(format!("{endereco}/{prefixo}"))
}

/// Um parâmetro de receita, como está no `receita.yaml`. O `tipo` diz como o
/// valor é conferido em `converter`; `pergunta` é o que o menu pergunta (vazio
/// quando o parâmetro não é perguntado) e `rotulos` explicam cada opção.
#[derive(Debug, Clone)]
pub struct Parametro {
    pub nome: String,
    pub tipo: String,
    pub padrao: Option<Value>,
    pub opcoes: Vec<String>,
    pub rotulos: Vec<(String, String)>,
    pub pergunta: String,
    pub descricao: String,
}

impl Parametro {
    /// Um parâmetro vazio, só com nome e tipo. Usado na leitura e nos testes.
    pub fn novo(nome: &str, tipo: &str) -> Self {
        Parametro {
            nome: nome.into(),
            tipo: tipo.into(),
            padrao: None,
            opcoes: vec![],
            rotulos: vec![],
            pergunta: String::new(),
            descricao: String::new(),
        }
    }

    /// A explicação de uma opção, ou texto vazio se não houver.
    pub fn rotulo(&self, opcao: &str) -> &str {
        self.rotulos
            .iter()
            .find(|(k, _)| k == opcao)
            .map(|(_, v)| v.as_str())
            .unwrap_or("")
    }

    /// Confere e converte um valor. O erro vem em português, pronto para mostrar.
    pub fn converter(&self, valor: Option<&Value>) -> Result<Valor, String> {
        let n = &self.nome;
        let Some(texto) = valor.and_then(texto_de) else {
            return Err(format!("o parâmetro {n} não tem valor"));
        };
        match self.tipo.as_str() {
            "escolha" => {
                if self.opcoes.contains(&texto) {
                    Ok(Valor::Texto(texto))
                } else {
                    Err(format!(
                        "{n} precisa ser uma destas opções: {}",
                        self.opcoes.join(", ")
                    ))
                }
            }
            "lista" => {
                // Várias opções, separadas por vírgula ou espaço, sem repetir.
                let mut escolhidas: Vec<String> = Vec::new();
                for item in texto.split(|c: char| c == ',' || c.is_whitespace()) {
                    let item = item.trim().to_lowercase();
                    if item.is_empty() || escolhidas.contains(&item) {
                        continue;
                    }
                    if !self.opcoes.contains(&item) {
                        return Err(format!(
                            "{n}: {item} não é uma opção; escolha entre {}, separadas por vírgula",
                            self.opcoes.join(", ")
                        ));
                    }
                    escolhidas.push(item);
                }
                if escolhidas.is_empty() {
                    return Err(format!(
                        "{n} precisa de pelo menos uma destas opções: {}",
                        self.opcoes.join(", ")
                    ));
                }
                Ok(Valor::Texto(escolhidas.join(",")))
            }
            "booleano" => match texto.trim().to_lowercase().as_str() {
                "sim" | "s" | "true" | "1" | "yes" => Ok(Valor::Booleano(true)),
                "não" | "nao" | "n" | "false" | "0" | "no" => Ok(Valor::Booleano(false)),
                _ => Err(format!("{n} precisa ser sim ou não")),
            },
            "inteiro" => texto
                .trim()
                .parse::<i64>()
                .map(Valor::Inteiro)
                .map_err(|_| format!("{n} precisa ser um número inteiro")),
            // Rede só local: o firewall usa esse valor, e uma rede pública aqui
            // abriria a porta para a internet.
            "cidr" => {
                let t = texto.trim();
                if t == "auto" {
                    return Ok(Valor::Texto(t.into()));
                }
                if !t.contains('/')
                    || t.split_once('/')
                        .map(|(ip, _)| ip.parse::<IpAddr>().is_err())
                        .unwrap_or(true)
                {
                    return Err(format!(
                        "{n} precisa ser uma rede como 192.168.0.0/24, ou auto"
                    ));
                }
                rede_local(t).map(Valor::Texto).map_err(|_| {
                    format!(
                        "{n} precisa ser uma rede local (como 192.168.0.0/24); nenhuma receita abre portas para a internet"
                    )
                })
            }
            "caminho" => {
                let t = texto.trim();
                if t.starts_with('/') && !t.contains('\n') {
                    Ok(Valor::Texto(t.into()))
                } else {
                    Err(format!(
                        "{n} precisa ser um caminho completo, começando com /"
                    ))
                }
            }
            // Texto livre: sem quebra de linha nem byte nulo, porque o valor
            // vira variável de ambiente e linha de arquivo de configuração.
            _ => {
                if texto.contains('\n') || texto.contains('\0') {
                    Err(format!("{n} não pode ter quebra de linha"))
                } else {
                    Ok(Valor::Texto(texto))
                }
            }
        }
    }
}

/// Um registro de teste do `receita.yaml`: em que distro e versão, onde (`vm`,
/// `conteiner` ou `maquina`) e o resultado.
#[derive(Debug, Clone)]
pub struct Teste {
    pub distro: String,
    pub versao: String,
    pub onde: String,
    pub resultado: String,
}

/// Uma receita lida e conferida. `familias` guarda o nível de teste por família,
/// e `pasta` é onde estão os scripts.
#[derive(Debug, Clone)]
pub struct Receita {
    pub id: String,
    pub pasta: PathBuf,
    pub nome: String,
    pub descricao: String,
    pub risco: String,
    pub precisa_root: bool,
    pub familias: Vec<(String, String)>,
    pub parametros: Vec<Parametro>,
    pub testes: Vec<Teste>,
}

impl Receita {
    /// O nível da receita numa família. Família que não aparece no YAML é "planejada".
    pub fn nivel(&self, familia: &str) -> &str {
        self.familias
            .iter()
            .find(|(f, _)| f == familia)
            .map(|(_, n)| n.as_str())
            .unwrap_or("planejada")
    }

    /// Se o `bora` aceita aplicar a receita nesta família.
    pub fn aplicavel(&self, familia: &str) -> bool {
        NIVEIS_APLICAVEIS.contains(&self.nivel(familia))
    }

    /// O nome do script da família, se existir, ou o comum.
    pub fn nome_do_script(pasta: &Path, script: &str, familia: &str) -> String {
        let especifico = format!("{script}.{familia}.sh");
        if pasta.join(&especifico).exists() {
            especifico
        } else {
            format!("{script}.sh")
        }
    }

    /// Acha um parâmetro pelo nome.
    pub fn parametro(&self, nome: &str) -> Option<&Parametro> {
        self.parametros.iter().find(|p| p.nome == nome)
    }

    /// O teste que passou nessa distro e versão, preferindo o de uma máquina
    /// virtual ou de verdade ao de contêiner, qualquer que seja a ordem no
    /// registro.
    pub fn testada_em(&self, distro: &str, base: &str) -> Option<&Teste> {
        let passou = |t: &&Teste| t.distro == distro && t.versao == base && t.resultado == "ok";
        self.testes
            .iter()
            .filter(passou)
            .find(|t| t.onde != "conteiner")
            .or_else(|| self.testes.iter().find(passou))
    }

    /// O texto de uma seção `## Título` do LEIAME, até a próxima seção.
    /// O `--passo-a-passo` usa isso para explicar a receita antes de aplicar.
    pub fn secao_leiame(&self, titulo: &str) -> String {
        let texto = fs::read_to_string(self.pasta.join("LEIAME.md")).unwrap_or_default();
        let cabecalho = format!("## {titulo}");
        let mut dentro = false;
        let mut linhas = Vec::new();
        for l in texto.lines() {
            if l.starts_with("## ") {
                if dentro {
                    break;
                }
                dentro = l.trim_end() == cabecalho;
                continue;
            }
            if dentro {
                linhas.push(l);
            }
        }
        linhas.join("\n").trim().to_string()
    }
}

/// Uma pergunta de rolê. O `id` é usado em `quando:` e em `{id}` nos parâmetros.
#[derive(Debug, Clone)]
pub struct Pergunta {
    pub id: String,
    pub texto: String,
    pub padrao: Option<String>,
    /// Quando não está vazia, a resposta precisa ser uma destas opções.
    pub opcoes: Vec<String>,
    pub rotulos: Vec<(String, String)>,
}

impl Pergunta {
    /// A explicação de uma opção, ou texto vazio se não houver.
    pub fn rotulo(&self, opcao: &str) -> &str {
        self.rotulos
            .iter()
            .find(|(k, _)| k == opcao)
            .map(|(_, v)| v.as_str())
            .unwrap_or("")
    }
}

/// Uma receita dentro de um rolê, com os parâmetros que o rolê fixa.
#[derive(Debug, Clone)]
pub struct ItemRole {
    pub id: String,
    pub parametros: Vec<(String, Value)>,
    /// A receita só entra no plano quando cada pergunta tem a resposta dada aqui.
    pub quando: Vec<(String, String)>,
}

impl ItemRole {
    /// Se a receita entra no plano, dadas as respostas.
    pub fn entra(&self, respostas: &std::collections::BTreeMap<String, String>) -> bool {
        self.quando
            .iter()
            .all(|(pergunta, valor)| respostas.get(pergunta) == Some(valor))
    }
}

/// Um rolê lido e conferido. `ram_gb` e `disco_livre_gb` vêm de `hardware_minimo`.
#[derive(Debug, Clone)]
pub struct Role {
    pub id: String,
    pub nome: String,
    pub descricao: String,
    pub status: String,
    pub ram_gb: Option<f64>,
    pub disco_livre_gb: Option<f64>,
    pub familias: Vec<String>,
    pub perguntas: Vec<Pergunta>,
    pub receitas: Vec<ItemRole>,
    pub pronto_quando: String,
    pub como_desfazer: String,
}

/// Ajudante para ler um mapa YAML acumulando erros com a origem (o arquivo)
/// na frente, em vez de parar no primeiro.
struct Leitor<'a> {
    mapa: &'a Mapping,
    origem: String,
    erros: Vec<String>,
}

impl<'a> Leitor<'a> {
    fn valor(&self, campo: &str) -> Option<&'a Value> {
        self.mapa.get(campo)
    }

    fn texto(&mut self, campo: &str, obrigatorio: bool) -> Option<String> {
        match self.valor(campo) {
            Some(Value::String(s)) => Some(s.clone()),
            None if !obrigatorio => None,
            None => {
                self.erros
                    .push(format!("{}: falta o campo {campo}", self.origem));
                None
            }
            Some(_) => {
                self.erros.push(format!(
                    "{}: o campo {campo} precisa ser um texto",
                    self.origem
                ));
                None
            }
        }
    }

    fn erro(&mut self, msg: impl fmt::Display) {
        self.erros.push(format!("{}: {msg}", self.origem));
    }
}

/// Lê um arquivo YAML que precisa ser um mapa.
fn ler_yaml(arquivo: &Path, origem: &str) -> Result<Mapping, String> {
    let texto = fs::read_to_string(arquivo).map_err(|e| format!("{origem}: {e}"))?;
    match serde_norway::from_str::<Value>(&texto) {
        Ok(Value::Mapping(m)) => Ok(m),
        Ok(_) => Err(format!("{origem}: o arquivo precisa ser um mapa")),
        Err(e) => Err(format!("{origem}: YAML inválido: {e}")),
    }
}

/// As entradas de um mapa YAML com a chave como texto.
fn chaves_texto(m: &Mapping) -> Vec<(String, &Value)> {
    m.iter()
        .filter_map(|(k, v)| texto_de(k).map(|k| (k, v)))
        .collect()
}

/// Lê e confere uma receita. Devolve todos os erros de uma vez, cada um com o
/// caminho do `receita.yaml` na frente.
pub fn ler_receita(pasta: &Path, raiz_receitas: &Path) -> Result<Receita, Vec<String>> {
    let relativo = pasta
        .strip_prefix(raiz_receitas)
        .unwrap_or(pasta)
        .to_string_lossy()
        .to_string();
    let origem = format!("receitas/{relativo}/receita.yaml");
    let mapa = ler_yaml(&pasta.join("receita.yaml"), &origem).map_err(|e| vec![e])?;
    let mut l = Leitor {
        mapa: &mapa,
        origem: origem.clone(),
        erros: vec![],
    };

    let id = l.texto("id", true).unwrap_or_default();
    if !id.is_empty() && id != relativo {
        l.erro(format!("o id {id} não bate com a pasta {relativo}"));
    }
    if !id.is_empty() && !ID_RECEITA.is_match(&id) {
        l.erro("o id precisa ser area/nome, em minúsculas e sem acento");
    }
    let nome = l.texto("nome", true).unwrap_or_default();
    let descricao = l.texto("descricao", true).unwrap_or_default();
    let risco = l.texto("risco", true).unwrap_or_default();
    if !risco.is_empty() && !RISCOS.contains(&risco.as_str()) {
        l.erro(format!("risco precisa ser {}", RISCOS.join(", ")));
    }
    let precisa_root = match l.valor("precisa_root") {
        Some(Value::Bool(b)) => *b,
        _ => {
            l.erro("precisa_root precisa ser true ou false");
            true
        }
    };
    let mut familias = Vec::new();
    match l.valor("familias") {
        Some(Value::Mapping(m)) => {
            for (fam, nivel) in chaves_texto(m) {
                let nivel = texto_de(nivel).unwrap_or_default();
                if !FAMILIAS.contains(&fam.as_str()) {
                    l.erro(format!("família desconhecida: {fam}"));
                }
                if !NIVEIS.contains(&nivel.as_str()) {
                    l.erro(format!("nível desconhecido para {fam}: {nivel}"));
                }
                familias.push((fam, nivel));
            }
        }
        _ => l.erro("falta o mapa familias"),
    }
    let mut parametros = Vec::new();
    match l.valor("parametros") {
        None | Some(Value::Null) => {}
        Some(Value::Mapping(m)) => {
            for (pnome, pdados) in chaves_texto(m) {
                if !ID_PARAM.is_match(&pnome) {
                    l.erro(format!("nome de parâmetro inválido: {pnome}"));
                    continue;
                }
                let Value::Mapping(pd) = pdados else {
                    l.erro(format!("o parâmetro {pnome} precisa ser um mapa"));
                    continue;
                };
                let tipo = pd.get("tipo").and_then(texto_de).unwrap_or_default();
                if !TIPOS.contains(&tipo.as_str()) {
                    l.erro(format!("o parâmetro {pnome} tem tipo desconhecido: {tipo}"));
                    continue;
                }
                let mut p = Parametro::novo(&pnome, &tipo);
                p.padrao = pd.get("padrao").cloned().filter(|v| !v.is_null());
                if let Some(Value::Sequence(s)) = pd.get("opcoes") {
                    p.opcoes = s.iter().filter_map(texto_de).collect();
                }
                if let Some(Value::Mapping(r)) = pd.get("rotulos") {
                    for (k, v) in chaves_texto(r) {
                        if !p.opcoes.contains(&k) {
                            l.erro(format!("rótulo para uma opção que não existe: {pnome}.{k}"));
                        }
                        p.rotulos.push((k, texto_de(v).unwrap_or_default()));
                    }
                }
                p.pergunta = pd.get("pergunta").and_then(texto_de).unwrap_or_default();
                p.descricao = pd.get("descricao").and_then(texto_de).unwrap_or_default();
                if (tipo == "escolha" || tipo == "lista") && p.opcoes.is_empty() {
                    l.erro(format!("o parâmetro {pnome} é uma escolha sem opções"));
                }
                if p.padrao.is_some()
                    && let Err(e) = p.converter(p.padrao.as_ref())
                {
                    l.erro(format!("padrão inválido: {e}"));
                }
                parametros.push(p);
            }
        }
        Some(_) => l.erro("parametros precisa ser um mapa"),
    }
    let mut testes = Vec::new();
    match l.valor("testes") {
        None | Some(Value::Null) => {}
        Some(Value::Sequence(s)) => {
            for t in s {
                let Value::Mapping(t) = t else {
                    l.erro("cada teste precisa ser um mapa");
                    continue;
                };
                let campo = |c: &str| t.get(c).and_then(texto_de);
                match (
                    campo("distro"),
                    campo("versao"),
                    campo("data"),
                    campo("resultado"),
                ) {
                    (Some(distro), Some(versao), Some(_), Some(resultado)) => {
                        let onde = campo("onde").unwrap_or_else(|| "vm".into());
                        if !["vm", "conteiner", "maquina"].contains(&onde.as_str()) {
                            l.erro("onde precisa ser vm, conteiner ou maquina");
                        }
                        testes.push(Teste {
                            distro,
                            versao,
                            onde,
                            resultado,
                        });
                    }
                    _ => l.erro("cada teste precisa de distro, versao, data e resultado"),
                }
            }
        }
        Some(_) => l.erro("testes precisa ser uma lista"),
    }

    // Cada um dos quatro scripts precisa existir, na versão comum (`aplicar.sh`)
    // ou numa versão por família (`aplicar.fedora.sh`), e ser executável.
    for script in SCRIPTS {
        let comum = pasta.join(format!("{script}.sh"));
        let mut arquivos = vec![];
        if comum.exists() {
            arquivos.push(comum.clone());
        }
        for fam in FAMILIAS {
            let p = pasta.join(format!("{script}.{fam}.sh"));
            if p.exists() {
                arquivos.push(p);
            }
        }
        if arquivos.is_empty() {
            l.erro(format!("falta o {script}.sh"));
        }
        for a in arquivos {
            let executavel = fs::metadata(&a)
                .map(|m| m.permissions().mode() & 0o111 != 0)
                .unwrap_or(false);
            if !executavel {
                l.erro(format!(
                    "{} precisa ser executável (chmod +x)",
                    a.file_name().unwrap().to_string_lossy()
                ));
            }
        }
    }

    if !l.erros.is_empty() {
        return Err(l.erros);
    }
    Ok(Receita {
        id,
        pasta: pasta.to_path_buf(),
        nome,
        descricao,
        risco,
        precisa_root,
        familias,
        parametros,
        testes,
    })
}

/// Lê e confere um rolê. Precisa da lista de receitas para conferir se os
/// parâmetros que o rolê fixa existem mesmo na receita.
pub fn ler_role(arquivo: &Path, receitas: &[Receita]) -> Result<Role, Vec<String>> {
    let nome_arquivo = arquivo
        .file_name()
        .unwrap_or_default()
        .to_string_lossy()
        .to_string();
    let origem = format!("objetivos/{nome_arquivo}");
    let mapa = ler_yaml(arquivo, &origem).map_err(|e| vec![e])?;
    let mut l = Leitor {
        mapa: &mapa,
        origem,
        erros: vec![],
    };

    let id = l.texto("id", true).unwrap_or_default();
    let esperado = nome_arquivo.trim_end_matches(".yaml");
    if !id.is_empty() && id != esperado {
        l.erro(format!("o id {id} não bate com o nome do arquivo"));
    }
    if !id.is_empty() && !ID_ROLE.is_match(&id) {
        l.erro("o id precisa ser em minúsculas, sem acento");
    }
    let nome = l.texto("nome", true).unwrap_or_default();
    let descricao = l.texto("descricao", true).unwrap_or_default();
    match l.valor("para_quem") {
        Some(Value::Sequence(s)) => {
            for p in s.iter().filter_map(texto_de) {
                if !PUBLICOS.contains(&p.as_str()) {
                    l.erro(format!("público desconhecido: {p}"));
                }
            }
        }
        _ => l.erro("falta a lista para_quem"),
    }
    let status = l.texto("status", true).unwrap_or_default();
    if !status.is_empty() && !STATUS_ROLE.contains(&status.as_str()) {
        l.erro(format!("status precisa ser {}", STATUS_ROLE.join(", ")));
    }
    let (mut ram_gb, mut disco_livre_gb) = (None, None);
    if let Some(Value::Mapping(h)) = l.valor("hardware_minimo") {
        ram_gb = h.get("ram_gb").and_then(Value::as_f64);
        disco_livre_gb = h.get("disco_livre_gb").and_then(Value::as_f64);
    }
    let mut familias = Vec::new();
    match l.valor("familias") {
        Some(Value::Sequence(s)) => {
            for f in s.iter().filter_map(texto_de) {
                if !FAMILIAS.contains(&f.as_str()) {
                    l.erro(format!("família desconhecida: {f}"));
                }
                familias.push(f);
            }
        }
        _ => l.erro("falta a lista familias"),
    }
    let mut perguntas = Vec::new();
    if let Some(Value::Sequence(s)) = l.valor("perguntas") {
        for p in s {
            let (Some(id), Some(texto)) = (
                p.get("id").and_then(texto_de),
                p.get("texto").and_then(texto_de),
            ) else {
                l.erro("cada pergunta precisa de id e texto");
                continue;
            };
            let padrao = p.get("padrao").and_then(texto_de);
            let opcoes: Vec<String> = match p.get("opcoes") {
                Some(Value::Sequence(o)) => o.iter().filter_map(texto_de).collect(),
                _ => vec![],
            };
            let rotulos = match p.get("rotulos") {
                Some(Value::Mapping(m)) => chaves_texto(m)
                    .into_iter()
                    .map(|(k, v)| (k, texto_de(v).unwrap_or_default()))
                    .collect(),
                _ => vec![],
            };
            if !opcoes.is_empty()
                && let Some(d) = &padrao
                && !opcoes.contains(d)
            {
                l.erro(format!(
                    "o padrão da pergunta {id} precisa ser uma das opções: {}",
                    opcoes.join(", ")
                ));
            }
            perguntas.push(Pergunta {
                id,
                texto,
                padrao,
                opcoes,
                rotulos,
            });
        }
    }
    // Cada item: `id` da receita, `quando` (condição) e, no resto das chaves,
    // os parâmetros que o rolê fixa, que podem usar `{pergunta}`.
    let mut itens = Vec::new();
    match l.valor("receitas") {
        Some(Value::Sequence(s)) => {
            for item in s {
                let Some(Value::Mapping(m)) = Some(item) else {
                    l.erro("cada receita precisa de id");
                    continue;
                };
                let Some(rid) = m.get("id").and_then(texto_de) else {
                    l.erro("cada receita precisa de id");
                    continue;
                };
                let mut parametros = Vec::new();
                let mut quando = Vec::new();
                match m.get("quando") {
                    None => {}
                    Some(Value::Mapping(q)) => {
                        for (pid, valor) in chaves_texto(q) {
                            let valor = texto_de(valor).unwrap_or_default();
                            match perguntas.iter().find(|p| p.id == pid) {
                                None => l.erro(format!(
                                    "{rid}.quando usa {pid}, que não é uma pergunta do rolê"
                                )),
                                Some(p) if !p.opcoes.is_empty() && !p.opcoes.contains(&valor) => l
                                    .erro(format!(
                                        "{rid}.quando: {valor} não é uma opção da pergunta {pid}"
                                    )),
                                Some(_) => {}
                            }
                            quando.push((pid, valor));
                        }
                    }
                    Some(_) => l.erro(format!(
                        "{rid}.quando precisa ser um mapa de pergunta: resposta"
                    )),
                }
                for (chave, valor) in chaves_texto(m) {
                    if chave == "id" || chave == "quando" {
                        continue;
                    }
                    let texto = texto_de(valor).unwrap_or_default();
                    for c in REFERENCIA.captures_iter(&texto) {
                        if !perguntas.iter().any(|p| p.id == c[1]) {
                            l.erro(format!(
                                "{rid}.{chave} usa {{{}}}, que não é uma pergunta do rolê",
                                &c[1]
                            ));
                        }
                    }
                    if let Some(rec) = receitas.iter().find(|r| r.id == rid)
                        && rec.parametro(&chave).is_none()
                    {
                        l.erro(format!("a receita {rid} não tem o parâmetro {chave}"));
                    }
                    parametros.push((chave, valor.clone()));
                }
                itens.push(ItemRole {
                    id: rid,
                    parametros,
                    quando,
                });
            }
        }
        _ => l.erro("falta a lista receitas"),
    }
    let pronto_quando = l.texto("pronto_quando", true).unwrap_or_default();
    let como_desfazer = l.texto("como_desfazer", true).unwrap_or_default();
    if !l.erros.is_empty() {
        return Err(l.erros);
    }
    Ok(Role {
        id,
        nome,
        descricao,
        status,
        ram_gb,
        disco_livre_gb,
        familias,
        perguntas,
        receitas: itens,
        pronto_quando,
        como_desfazer,
    })
}

/// O catálogo inteiro: de onde veio, as receitas, os rolês e os erros de leitura.
pub struct Catalogo {
    pub raiz: PathBuf,
    pub receitas: Vec<Receita>,
    pub roles: Vec<Role>,
    pub erros: Vec<String>,
}

/// O conteúdo de uma pasta em ordem alfabética, para a ordem do catálogo não
/// depender do sistema de arquivos.
fn listar(pasta: &Path) -> Vec<PathBuf> {
    let mut v: Vec<PathBuf> = fs::read_dir(pasta)
        .map(|r| r.flatten().map(|e| e.path()).collect())
        .unwrap_or_default();
    v.sort();
    v
}

impl Catalogo {
    /// Lê todas as receitas (`receitas/*/*/receita.yaml`) e depois os rolês
    /// (`objetivos/*.yaml`). Nunca falha: o que der errado vai para `erros`.
    pub fn carregar(raiz: &Path) -> Catalogo {
        let mut c = Catalogo {
            raiz: raiz.to_path_buf(),
            receitas: vec![],
            roles: vec![],
            erros: vec![],
        };
        let pasta_receitas = raiz.join("receitas");
        for area in listar(&pasta_receitas).into_iter().filter(|p| p.is_dir()) {
            for pasta in listar(&area)
                .into_iter()
                .filter(|p| p.join("receita.yaml").exists())
            {
                match ler_receita(&pasta, &pasta_receitas) {
                    Ok(r) => c.receitas.push(r),
                    Err(e) => c.erros.extend(e),
                }
            }
        }
        for arquivo in listar(&raiz.join("objetivos")) {
            if arquivo.extension().and_then(|e| e.to_str()) != Some("yaml") {
                continue;
            }
            match ler_role(&arquivo, &c.receitas) {
                Ok(r) => c.roles.push(r),
                Err(e) => c.erros.extend(e),
            }
        }
        c
    }

    /// Os rolês cujo status não bate com a regra de objetivos/README.md: um
    /// rolê é `testado` quando cada receita dele passou numa máquina virtual
    /// (ou de verdade) no Ubuntu 24.04 e no Debian 13. Só o `bora conferir`
    /// olha isto, para ninguém esquecer de trocar o status.
    pub fn status_fora_da_regra(&self) -> Vec<String> {
        const BASES: &[(&str, &str)] = &[("ubuntu", "24.04"), ("debian", "13")];
        let mut problemas = Vec::new();
        for role in &self.roles {
            if role.status == "planejado" {
                continue;
            }
            // Uma receita pode aparecer mais de uma vez no rolê, com outro "quando".
            let mut faltam: Vec<String> = Vec::new();
            for falta in role
                .receitas
                .iter()
                .filter_map(|item| self.receita(&item.id))
                .flat_map(|r| {
                    BASES.iter().filter_map(move |(distro, versao)| {
                        match r.testada_em(distro, versao) {
                            Some(t) if t.onde != "conteiner" => None,
                            _ => Some(format!("{} em {distro} {versao}", r.id)),
                        }
                    })
                })
            {
                if !faltam.contains(&falta) {
                    faltam.push(falta);
                }
            }
            if role.status == "rascunho" && faltam.is_empty() {
                problemas.push(format!(
                    "o rolê {} já passou nas máquinas virtuais no Ubuntu 24.04 e no Debian 13; troque o status para testado",
                    role.id
                ));
            }
            if role.status == "testado" && !faltam.is_empty() {
                problemas.push(format!(
                    "o rolê {} está como testado, mas falta o teste numa máquina virtual de: {}",
                    role.id,
                    faltam.join(", ")
                ));
            }
        }
        problemas
    }

    /// O `receitas/comum.sh`, com as funções que todos os scripts usam.
    pub fn lib(&self) -> PathBuf {
        self.raiz.join("receitas").join("comum.sh")
    }

    /// Acha uma receita pelo id (`area/nome`).
    pub fn receita(&self, id: &str) -> Option<&Receita> {
        self.receitas.iter().find(|r| r.id == id)
    }

    /// Acha um rolê pelo id.
    pub fn role(&self, id: &str) -> Option<&Role> {
        self.roles.iter().find(|r| r.id == id)
    }

    /// Se o rolê cabe nesta máquina, e o motivo quando não cabe.
    pub fn disponibilidade(&self, role: &Role, d: &Diag) -> Result<(), String> {
        let fam = d.distro.familia.clone().unwrap_or_default();
        if !role.familias.contains(&fam) {
            return Err(format!("ainda não funciona na família {fam}"));
        }
        // Folga de 10% na RAM: uma máquina "de 4 GB" mostra uns 3,8 GB livres
        // para o sistema, e não seria justo recusar por isso.
        if let (Some(min), Some(ram)) = (role.ram_gb, d.hardware.ram_gb)
            && ram < min * 0.9
        {
            return Err(format!("precisa de pelo menos {min} GB de RAM"));
        }
        if let (Some(min), Some(disco)) = (role.disco_livre_gb, d.hardware.disco_livre_gb)
            && disco < min
        {
            return Err(format!("precisa de pelo menos {min} GB livres no disco"));
        }
        let faltando: Vec<&str> = role
            .receitas
            .iter()
            .filter(|i| self.receita(&i.id).is_none())
            .map(|i| i.id.as_str())
            .collect();
        if !faltando.is_empty() {
            return Err(format!(
                "em construção: faltam as receitas {}",
                faltando.join(", ")
            ));
        }
        for item in &role.receitas {
            if !self.receita(&item.id).unwrap().aplicavel(&fam) {
                return Err(format!(
                    "a receita {} ainda não funciona na família {fam}",
                    item.id
                ));
            }
        }
        Ok(())
    }
}

#[cfg(test)]
mod testes {
    use super::*;

    fn raiz() -> PathBuf {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
    }

    // O catálogo do repositório lê sem nenhum erro.
    #[test]
    fn catalogo_real_sem_erros() {
        let c = Catalogo::carregar(&raiz());
        assert_eq!(c.erros, Vec::<String>::new());
        assert!(c.receitas.len() >= 3);
    }

    // O status de cada rolê (rascunho, testado) bate com os testes registrados.
    #[test]
    fn status_dos_roles_segue_a_regra() {
        let c = Catalogo::carregar(&raiz());
        assert_eq!(c.status_fora_da_regra(), Vec::<String>::new());
    }

    // Com teste em contêiner e em VM na mesma versão, vale o da VM.
    #[test]
    fn testada_em_prefere_a_maquina_virtual() {
        let c = Catalogo::carregar(&raiz());
        let mut r = c.receita("sistema/zram").unwrap().clone();
        let teste = |onde: &str| Teste {
            distro: "ubuntu".into(),
            versao: "26.04".into(),
            onde: onde.into(),
            resultado: "ok".into(),
        };
        r.testes = vec![teste("conteiner"), teste("vm")];
        assert_eq!(r.testada_em("ubuntu", "26.04").unwrap().onde, "vm");
        r.testes = vec![teste("conteiner")];
        assert_eq!(r.testada_em("ubuntu", "26.04").unwrap().onde, "conteiner");
        assert!(r.testada_em("debian", "13").is_none());
    }

    // Todo LEIAME tem as seis seções, e nenhuma vazia.
    #[test]
    fn leiame_com_todas_as_secoes() {
        let c = Catalogo::carregar(&raiz());
        for r in &c.receitas {
            for s in SECOES_LEIAME {
                assert!(
                    !r.secao_leiame(s).is_empty(),
                    "{}/LEIAME.md não tem a seção {s}",
                    r.id
                );
            }
        }
    }

    // Todo script executável começa com o shebang do bash e liga o modo estrito
    // (`set -euo pipefail`) nas primeiras linhas.
    #[test]
    fn scripts_seguem_o_contrato() {
        let c = Catalogo::carregar(&raiz());
        for r in &c.receitas {
            for a in listar(&r.pasta) {
                if a.extension().and_then(|e| e.to_str()) != Some("sh") {
                    continue;
                }
                let executavel = fs::metadata(&a).unwrap().permissions().mode() & 0o111 != 0;
                if !executavel {
                    continue; // arquivos de funções, lidos com source
                }
                let texto = fs::read_to_string(&a).unwrap();
                assert!(
                    texto.starts_with("#!/usr/bin/env bash\n"),
                    "{}",
                    a.display()
                );
                assert!(
                    texto
                        .lines()
                        .skip(1)
                        .take(3)
                        .any(|l| l == "set -euo pipefail"),
                    "{}",
                    a.display()
                );
            }
        }
    }

    // Nenhum arquivo de receita tem `curl ... | sh` nem `wget ... | bash`.
    #[test]
    fn receitas_nao_baixam_e_executam() {
        let proibido = Regex::new(r"(curl|wget)[^|\n]*\|\s*(sudo\s+)?(ba)?sh").unwrap();
        let c = Catalogo::carregar(&raiz());
        for r in &c.receitas {
            for a in listar(&r.pasta) {
                let texto = fs::read_to_string(&a).unwrap_or_default();
                assert!(!proibido.is_match(&texto), "{}", a.display());
            }
        }
    }

    // Redes locais passam e saem normalizadas; internet, CGNAT, rede de
    // documentação e lixo são recusados.
    #[test]
    fn cidr() {
        let p = Parametro::novo("rede", "cidr");
        let conv = |s: &str| p.converter(Some(&Value::String(s.into())));
        assert_eq!(
            conv("192.168.1.10/24"),
            Ok(Valor::Texto("192.168.1.0/24".into()))
        );
        assert_eq!(conv("auto"), Ok(Valor::Texto("auto".into())));
        assert_eq!(conv("10.0.0.0/8"), Ok(Valor::Texto("10.0.0.0/8".into())));
        assert_eq!(
            conv("fd12:3456::1/64"),
            Ok(Valor::Texto("fd12:3456::/64".into()))
        );
        for ruim in [
            "8.8.8.0/24",
            "0.0.0.0/0",
            "100.64.0.0/10",
            "192.0.2.0/24",
            "abc",
            "10.0.0.0/7",
            "10.0.0.1",
        ] {
            assert!(conv(ruim).is_err(), "{ruim}");
        }
    }

    // As conversões dos outros tipos, com os casos que devem falhar.
    #[test]
    fn booleano_escolha_caminho() {
        let b = Parametro::novo("x", "booleano");
        assert_eq!(
            b.converter(Some(&Value::String("sim".into()))),
            Ok(Valor::Booleano(true))
        );
        assert_eq!(
            b.converter(Some(&Value::Bool(false))),
            Ok(Valor::Booleano(false))
        );
        assert!(b.converter(Some(&Value::String("talvez".into()))).is_err());
        let mut e = Parametro::novo("x", "escolha");
        e.opcoes = vec!["a".into(), "b".into()];
        assert!(e.converter(Some(&Value::String("b".into()))).is_ok());
        assert!(e.converter(Some(&Value::String("c".into()))).is_err());
        let mut v = Parametro::novo("x", "lista");
        v.opcoes = vec!["a".into(), "b".into(), "c".into()];
        assert_eq!(
            v.converter(Some(&Value::String("C, a,,a b".into()))),
            Ok(Valor::Texto("c,a,b".into()))
        );
        assert!(v.converter(Some(&Value::String("a,d".into()))).is_err());
        assert!(v.converter(Some(&Value::String(" , ".into()))).is_err());
        assert!(
            Parametro::novo("x", "caminho")
                .converter(Some(&Value::String("rel".into())))
                .is_err()
        );
        assert!(
            Parametro::novo("x", "texto")
                .converter(Some(&Value::String("a\nb".into())))
                .is_err()
        );
        assert!(Parametro::novo("x", "texto").converter(None).is_err());
    }
}
