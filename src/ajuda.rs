//! A pergunta pronta: um texto para colar em qualquer chat de IA, sem dados sensíveis.
//!
//! O `bora ajuda` junta o diagnóstico da máquina, o último erro (se houver) e a
//! dúvida da pessoa, e pede à IA respostas que sigam as regras do projeto. Antes
//! de mostrar qualquer coisa, `limpar` tira IPs, MACs, nomes de usuário, nome do
//! computador e coisas com cara de senha ou token.

use crate::diag::Diag;
use regex::{Captures, Regex};
use serde::{Deserialize, Serialize};
use std::fs;
use std::net::IpAddr;
use std::os::unix::fs::PermissionsExt;
use std::path::PathBuf;
use std::sync::LazyLock;

/// Onde fica o último erro: `/var/lib/bora/ultimo-erro.json`.
fn arquivo_erro() -> PathBuf {
    crate::executor::dir_estado().join("ultimo-erro.json")
}

// Os padrões compilam uma vez só, na primeira vez que são usados.
static IPV4: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(?:\d{1,3}\.){3}\d{1,3}\b").unwrap());
// Candidatos a IPv6 (com pelo menos dois ":"); só vira IP o que o parser aceita.
static IPV6: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"[0-9a-fA-F]{0,4}(?::[0-9a-fA-F]{0,4}){2,7}").unwrap());
// Endereço físico de placa de rede (aa:bb:cc:dd:ee:ff).
static MAC: LazyLock<Regex> =
    LazyLock::new(|| Regex::new(r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b").unwrap());
// Tokens com formato conhecido: OpenAI e parecidos (sk-), GitHub (ghp_ e
// irmãos), Slack (xox), chave de acesso da AWS (AKIA) e JWT (eyJ...).
static SEGREDO: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)\b(sk-[a-z0-9_-]{16,}|gh[pousr]_[a-z0-9]{20,}|xox[abpr]-[a-z0-9-]{10,}|AKIA[0-9A-Z]{16}|eyJ[a-z0-9_-]{10,}\.[a-z0-9_-]{10,}\.[a-z0-9_-]{10,})",
    )
    .unwrap()
});
// Qualquer "senha=...", "token: ..." e afins: troca só o valor, mantém o nome.
static ATRIBUICAO: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(?i)\b(senha|password|passwd|token|secret|segredo|api[_-]?key|chave)(\s*[:=]\s*)(\S+)",
    )
    .unwrap()
});

/// Decide o que fazer com algo que parece IP. Loopback (127.0.0.1) fica, porque
/// não identifica ninguém e ajuda a entender o erro. Rede local vira `IP-LOCAL`
/// (inclui o 100.64.0.0/10 do CGNAT e da Tailscale) e o resto vira `IP-PUBLICO`.
fn trocar_ip(c: &Captures) -> String {
    let texto = &c[0];
    // Trechos curtos como "d::f" também são IPv6 válidos, mas quase sempre são outra coisa.
    if texto.contains(':') && texto.len() < 7 {
        return texto.to_string();
    }
    match texto.parse::<IpAddr>() {
        Ok(ip) if ip.is_loopback() || ip.is_unspecified() => texto.to_string(),
        Ok(IpAddr::V4(v))
            if v.is_private()
                || v.is_link_local()
                || (v.octets()[0] == 100 && v.octets()[1] & 0xc0 == 64) =>
        {
            "IP-LOCAL".into()
        }
        Ok(IpAddr::V6(v))
            if (v.segments()[0] & 0xfe00) == 0xfc00 || (v.segments()[0] & 0xffc0) == 0xfe80 =>
        {
            "IP-LOCAL".into()
        }
        Ok(_) => "IP-PUBLICO".into(),
        Err(_) => texto.to_string(),
    }
}

/// Os nomes de usuário que podem aparecer no texto: as contas de gente do
/// `/etc/passwd` (UID de 1000 a 65533) e quem está rodando o `bora`.
/// Nomes com menos de 3 letras ficam de fora, senão "a" viraria USUARIO em todo canto.
/// Os mais longos vêm primeiro, para "ana" não estragar "mariana" antes da hora.
fn usuarios() -> Vec<String> {
    let mut nomes = Vec::new();
    if let Ok(t) = fs::read_to_string("/etc/passwd") {
        for l in t.lines() {
            let p: Vec<&str> = l.split(':').collect();
            if p.len() > 2 {
                let uid: u32 = p[2].parse().unwrap_or(0);
                if (1000..65534).contains(&uid) && p[0].len() >= 3 {
                    nomes.push(p[0].to_string());
                }
            }
        }
    }
    for var in ["SUDO_USER", "USER", "LOGNAME"] {
        if let Ok(v) = std::env::var(var)
            && v != "root"
            && v.len() >= 3
            && !nomes.contains(&v)
        {
            nomes.push(v);
        }
    }
    nomes.sort_by_key(|n| std::cmp::Reverse(n.len()));
    nomes
}

/// Remove do texto o que identifica a pessoa ou a máquina.
pub fn limpar(texto: &str) -> String {
    let mut t = SEGREDO.replace_all(texto, "SEGREDO-REMOVIDO").into_owned();
    t = ATRIBUICAO
        .replace_all(&t, |c: &Captures| format!("{}{}REMOVIDO", &c[1], &c[2]))
        .into_owned();
    t = MAC.replace_all(&t, "MAC").into_owned();
    t = IPV4.replace_all(&t, trocar_ip).into_owned();
    t = IPV6.replace_all(&t, trocar_ip).into_owned();
    if let Ok(host) = fs::read_to_string("/proc/sys/kernel/hostname") {
        let host = host.trim();
        if host.len() >= 3 && host != "localhost" {
            t = t.replace(host, "COMPUTADOR");
        }
    }
    for nome in usuarios() {
        let re = Regex::new(&format!(r"(^|[^\w-]){}($|[^\w-])", regex::escape(&nome))).unwrap();
        // Duas passadas, para nomes colados um no outro por um separador só.
        for _ in 0..2 {
            t = re.replace_all(&t, "${1}USUARIO${2}").into_owned();
        }
    }
    t
}

/// O que o `executor` guarda quando uma receita falha: qual execução, qual
/// rolê e receita, com que parâmetros, em que etapa (`aplicar`, `testar`...) e
/// as últimas linhas da saída, já limpas.
#[derive(Serialize, Deserialize)]
pub struct UltimoErro {
    pub execucao: String,
    pub objetivo: Option<String>,
    pub receita: String,
    pub parametros: Vec<(String, String)>,
    pub etapa: String,
    pub saida: String,
}

/// Guarda o último erro, já limpo, para o bora ajuda ler sem precisar de root.
pub fn guardar_erro(erro: UltimoErro) {
    let caminho = arquivo_erro();
    if let Some(p) = caminho.parent() {
        let _ = fs::create_dir_all(p);
    }
    if let Ok(texto) = serde_json::to_string_pretty(&erro)
        && fs::write(&caminho, texto).is_ok()
    {
        let _ = fs::set_permissions(&caminho, fs::Permissions::from_mode(0o644));
    }
}

/// Lê o último erro guardado, se houver.
pub fn ler_ultimo_erro() -> Option<UltimoErro> {
    serde_json::from_str(&fs::read_to_string(arquivo_erro()).ok()?).ok()
}

/// Monta o texto da pergunta pronta: apresentação do projeto, a máquina, o
/// último erro, a dúvida (limpa) e as regras que a resposta precisa seguir.
pub fn montar(d: &Diag, pergunta: Option<&str>) -> String {
    let dist = &d.distro;
    let fam = dist.familia.as_deref();
    let base = match &dist.base {
        Some(b) if !b.is_empty() && *b != dist.versao => format!(", base {b}"),
        _ => String::new(),
    };
    let num = |x: Option<f64>| x.map(|v| format!("{v}")).unwrap_or_else(|| "?".into());
    let mut l = vec![
        "Estou configurando um computador com Linux usando o bora, do projeto Linux para todos os rolês".to_string(),
        "(https://github.com/brahm/linux-para-todos-os-roles). O bora aplica receitas testadas que sabem".into(),
        "verificar, aplicar, testar e desfazer cada mudança.".into(),
        String::new(),
        "Meu computador:".into(),
        format!("- distro: {} (família {}{base})", dist.nome, fam.unwrap_or("não suportada")),
        format!(
            "- {} GB de RAM, {} GB livres na raiz ({})",
            num(d.hardware.ram_gb),
            num(d.hardware.disco_livre_gb),
            d.sistema.sistema_de_arquivos_raiz.as_deref().unwrap_or("?")
        ),
        format!(
            "- disco do sistema: {}; zram: {}",
            match d.hardware.disco_do_sistema.as_deref() {
                Some("ssd") => "SSD",
                Some("hdd") => "disco rígido",
                _ => "não identificado",
            },
            d.ja_tem.zram_gb.map(|g| format!("ligado, {g} GB")).unwrap_or_else(|| "desligado".into())
        ),
        format!(
            "- vídeo: {}",
            if d.hardware.video.is_empty() { "não identificado".into() } else { d.hardware.video.join(", ") }
        ),
        format!("- máquina virtual: {}", d.sistema.virtualizacao.as_deref().unwrap_or("não")),
        format!(
            "- snapshot do sistema: {}; firewall: {}",
            d.ja_tem.snapshot.as_deref().unwrap_or("não configurado"),
            d.ja_tem.firewall.as_deref().unwrap_or("nenhum")
        ),
    ];
    if let Some(e) = ler_ultimo_erro() {
        l.push(String::new());
        l.push("O que deu errado:".into());
        let dentro = e
            .objetivo
            .as_ref()
            .map(|o| format!(", dentro do rolê {o}"))
            .unwrap_or_default();
        l.push(format!(
            "- receita {}, na etapa {}{dentro}",
            e.receita, e.etapa
        ));
        if !e.parametros.is_empty() {
            let p: Vec<String> = e
                .parametros
                .iter()
                .map(|(k, v)| format!("{k}={v}"))
                .collect();
            l.push(format!("- parâmetros: {}", p.join(", ")));
        }
        l.push("- as últimas linhas da saída:".into());
        l.push(String::new());
        l.push("```".into());
        l.push(e.saida);
        l.push("```".into());
    }
    if let Some(p) = pergunta {
        l.push(String::new());
        l.push("Minha dúvida:".into());
        l.push(limpar(p));
    }
    l.extend([
        String::new(),
        "Por favor:".into(),
        "- responda em português do Brasil, explicando o porquê de cada passo;".into(),
        format!(
            "- use só comandos para a família {} e pacotes dos repositórios oficiais ou Flatpak;",
            fam.unwrap_or("da minha distro")
        ),
        "- não sugira desligar o firewall, abrir portas para a internet nem rodar scripts baixados com curl | sh;".into(),
        "- diga como conferir que funcionou e como voltar atrás.".into(),
    ]);
    l.join("\n")
}

#[cfg(test)]
mod testes {
    use super::*;

    // Confere que nada sensível vaza e que o loopback continua no texto.
    #[test]
    fn limpa_dados_sensiveis() {
        let texto = "conectado de 189.10.20.30 e 192.168.0.5, mac aa:bb:cc:dd:ee:ff, token=abc123 \
                     chave sk-abcdefghijklmnopqrstuvwxyz ghp_abcdefghijklmnopqrstuvwxyz0123 em 127.0.0.1 \
                     e fd12:3456:789a::1";
        let limpo = limpar(texto);
        for vazado in [
            "189.10.20.30",
            "192.168.0.5",
            "aa:bb:cc",
            "abc123",
            "sk-abc",
            "ghp_",
            "fd12:3456",
        ] {
            assert!(!limpo.contains(vazado), "{vazado} vazou: {limpo}");
        }
        for ficou in ["IP-PUBLICO", "IP-LOCAL", "MAC", "127.0.0.1"] {
            assert!(limpo.contains(ficou), "{ficou}: {limpo}");
        }
    }
}
