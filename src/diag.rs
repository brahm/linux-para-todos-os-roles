//! Diagnóstico da máquina: distro, família, hardware e o que já está instalado.

use serde::Serialize;
use std::collections::BTreeMap;
use std::fs;
use std::path::Path;
use std::process::Command;

/// Distros que o projeto deixa de fora de propósito, com o motivo.
const FORA_DO_ESCOPO: &[(&str, &str)] = &[
    ("mx", "o MX Linux não usa systemd por padrão"),
    ("slackware", "o Slackware não usa systemd"),
    ("gentoo", "o Gentoo não usa systemd por padrão"),
    ("void", "o Void não usa systemd"),
    ("alpine", "o Alpine não usa systemd"),
    ("devuan", "o Devuan não usa systemd"),
    ("antix", "o antiX não usa systemd"),
    ("artix", "o Artix não usa systemd"),
    ("nixos", "o NixOS tem configuração declarativa própria"),
    ("steamos", "o SteamOS foi feito para ser console"),
];

/// Identificadores do os-release que já levam direto à família.
const FAMILIA_POR_ID: &[(&str, &str)] = &[
    ("ubuntu", "ubuntu"),
    ("linuxmint", "ubuntu"),
    ("pop", "ubuntu"),
    ("zorin", "ubuntu"),
    ("elementary", "ubuntu"),
    ("neon", "ubuntu"),
    ("debian", "debian"),
    ("fedora", "fedora"),
    ("nobara", "fedora"),
    ("arch", "arch"),
    ("cachyos", "arch"),
    ("endeavouros", "arch"),
    ("manjaro", "arch"),
    ("garuda", "arch"),
    ("bazzite", "fedora-imutavel"),
    ("bluefin", "fedora-imutavel"),
    ("aurora", "fedora-imutavel"),
    ("opensuse-tumbleweed", "opensuse"),
    ("opensuse-leap", "opensuse"),
    ("opensuse-slowroll", "opensuse"),
];

const DERIVADAS_CONHECIDAS: &[&str] = &[
    "linuxmint",
    "pop",
    "zorin",
    "elementary",
    "neon",
    "nobara",
    "cachyos",
    "endeavouros",
    "manjaro",
    "garuda",
    "bazzite",
    "bluefin",
    "aurora",
];

const CODINOMES_UBUNTU: &[(&str, &str)] = &[
    ("focal", "20.04"),
    ("jammy", "22.04"),
    ("noble", "24.04"),
    ("resolute", "26.04"),
];

const BASES_SUPORTADAS: &[(&str, &[&str])] =
    &[("ubuntu", &["24.04", "26.04"]), ("debian", &["13"])];

const VARIANTES_IMUTAVEIS: &[&str] = &[
    "silverblue",
    "kinoite",
    "sericea",
    "onyx",
    "cosmic-atomic",
    "iot",
    "coreos",
];

fn procurar<'a>(tabela: &'a [(&str, &str)], chave: &str) -> Option<&'a str> {
    tabela.iter().find(|(k, _)| *k == chave).map(|(_, v)| *v)
}

/// Lê o os-release (ou o caminho dado) num mapa.
pub fn ler_os_release(caminho: Option<&Path>) -> BTreeMap<String, String> {
    let candidatos: Vec<&Path> = match caminho {
        Some(c) => vec![c],
        None => vec![
            Path::new("/etc/os-release"),
            Path::new("/usr/lib/os-release"),
        ],
    };
    for c in candidatos {
        let Ok(texto) = fs::read_to_string(c) else {
            continue;
        };
        let mut dados = BTreeMap::new();
        for linha in texto.lines() {
            let linha = linha.trim();
            if linha.is_empty() || linha.starts_with('#') {
                continue;
            }
            let Some((k, v)) = linha.split_once('=') else {
                continue;
            };
            let mut v = v.trim();
            if v.len() >= 2
                && (v.starts_with('"') && v.ends_with('"')
                    || v.starts_with('\'') && v.ends_with('\''))
            {
                v = &v[1..v.len() - 1];
            }
            dados.insert(k.trim().to_string(), v.to_string());
        }
        return dados;
    }
    BTreeMap::new()
}

/// Família, base (a versão da distro de origem) e, se não for suportada, o motivo.
pub fn descobrir_familia(
    osr: &BTreeMap<String, String>,
    ostree: bool,
) -> (Option<String>, Option<String>, Option<String>) {
    let campo = |k: &str| osr.get(k).cloned().unwrap_or_default();
    let ident = campo("ID").to_lowercase();
    let parecidas_texto = campo("ID_LIKE").to_lowercase();
    let parecidas: Vec<&str> = parecidas_texto.split_whitespace().collect();
    let variante = campo("VARIANT_ID").to_lowercase();
    let versao = campo("VERSION_ID");

    if let Some(motivo) = procurar(FORA_DO_ESCOPO, &ident) {
        return (None, None, Some(motivo.to_string()));
    }
    if procurar(FAMILIA_POR_ID, &ident).is_none() {
        for p in &parecidas {
            if let Some(motivo) = procurar(FORA_DO_ESCOPO, p) {
                return (None, None, Some(motivo.to_string()));
            }
        }
    }

    let mut familia = procurar(FAMILIA_POR_ID, &ident).map(str::to_string);
    if familia.is_none() {
        let tem = |x: &str| parecidas.contains(&x);
        familia = if ident.starts_with("opensuse") || tem("suse") {
            Some("opensuse")
        } else if tem("ubuntu") {
            Some("ubuntu")
        } else if tem("debian") {
            Some("debian")
        } else if tem("arch") {
            Some("arch")
        } else if tem("fedora") {
            Some("fedora")
        } else {
            None
        }
        .map(str::to_string);
    }
    let Some(mut familia) = familia else {
        let nome = osr
            .get("PRETTY_NAME")
            .cloned()
            .filter(|s| !s.is_empty())
            .unwrap_or_else(|| {
                if ident.is_empty() {
                    "desconhecida".into()
                } else {
                    ident.clone()
                }
            });
        return (
            None,
            None,
            Some(format!(
                "a distro {nome} não pertence a nenhuma família que o bora conhece"
            )),
        );
    };

    if familia == "fedora" && (ostree || VARIANTES_IMUTAVEIS.contains(&variante.as_str())) {
        familia = "fedora-imutavel".into();
    }

    let mut base = versao.clone();
    if familia == "ubuntu" {
        let codinome = campo("UBUNTU_CODENAME").to_lowercase();
        if (ident != "ubuntu" || base.is_empty())
            && let Some(v) = procurar(CODINOMES_UBUNTU, &codinome)
        {
            base = v.to_string();
        }
    } else if familia == "debian" {
        if ident == "debian" && versao.is_empty() {
            return (
                None,
                None,
                Some("o Debian testing e o sid não são suportados; use o Debian estável".into()),
            );
        }
        if ident != "debian" {
            let mut codinome = campo("DEBIAN_CODENAME");
            if codinome.is_empty() {
                codinome = campo("VERSION_CODENAME");
            }
            match codinome.to_lowercase().as_str() {
                "trixie" => base = "13".into(),
                "bookworm" => base = "12".into(),
                _ => {}
            }
        }
    }
    (Some(familia), Some(base), None)
}

pub fn tem_systemd() -> bool {
    Path::new("/run/systemd/system").is_dir()
        || fs::read_to_string("/proc/1/comm")
            .map(|s| s.trim() == "systemd")
            .unwrap_or(false)
}

#[derive(Debug, Clone, Serialize)]
pub struct Distro {
    pub id: String,
    pub nome: String,
    pub versao: String,
    pub familia: Option<String>,
    pub base: Option<String>,
    pub derivada: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct Sistema {
    pub arquitetura: String,
    pub kernel: String,
    pub systemd: bool,
    pub uefi: bool,
    pub virtualizacao: Option<String>,
    pub sistema_de_arquivos_raiz: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Processador {
    pub modelo: Option<String>,
    pub nucleos: usize,
}

#[derive(Debug, Clone, Serialize)]
pub struct Hardware {
    pub processador: Processador,
    pub ram_gb: Option<f64>,
    pub disco_livre_gb: Option<f64>,
    pub video: Vec<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Rede {
    pub rota_padrao: bool,
}

#[derive(Debug, Clone, Serialize)]
pub struct JaTem {
    pub snapshot: Option<String>,
    pub firewall: Option<String>,
}

#[derive(Debug, Clone, Serialize)]
pub struct Diag {
    pub distro: Distro,
    pub sistema: Sistema,
    pub hardware: Hardware,
    pub rede: Rede,
    pub ja_tem: JaTem,
    pub suportada: bool,
    pub problemas: Vec<String>,
    pub avisos: Vec<String>,
}

fn arred(x: f64) -> f64 {
    (x * 10.0).round() / 10.0
}

fn memoria_gb() -> Option<f64> {
    let texto = fs::read_to_string("/proc/meminfo").ok()?;
    let linha = texto.lines().find(|l| l.starts_with("MemTotal:"))?;
    let kb: f64 = linha.split_whitespace().nth(1)?.parse().ok()?;
    Some(arred(kb / 1024.0 / 1024.0))
}

pub fn disco_livre_gb(caminho: &str) -> Option<f64> {
    let c = std::ffi::CString::new(caminho).ok()?;
    let mut st: libc::statvfs = unsafe { std::mem::zeroed() };
    // SAFETY: c é uma string C válida e st é um buffer do tamanho certo.
    if unsafe { libc::statvfs(c.as_ptr(), &mut st) } != 0 {
        return None;
    }
    Some(arred(
        st.f_bavail as f64 * st.f_frsize as f64 / 1024f64.powi(3),
    ))
}

fn sistema_de_arquivos_raiz() -> Option<String> {
    let texto = fs::read_to_string("/proc/mounts").ok()?;
    texto
        .lines()
        .filter_map(|l| {
            let p: Vec<&str> = l.split_whitespace().collect();
            (p.len() >= 3 && p[1] == "/").then(|| p[2].to_string())
        })
        .next_back()
}

fn processador() -> Processador {
    let modelo = fs::read_to_string("/proc/cpuinfo").ok().and_then(|t| {
        t.lines()
            .find(|l| {
                let l = l.to_lowercase();
                l.starts_with("model name") || l.starts_with("hardware")
            })
            .and_then(|l| l.split_once(':').map(|(_, v)| v.trim().to_string()))
    });
    let nucleos = std::thread::available_parallelism()
        .map(|n| n.get())
        .unwrap_or(1);
    Processador { modelo, nucleos }
}

pub fn comando_existe(nome: &str) -> bool {
    std::env::var_os("PATH")
        .map(|p| std::env::split_paths(&p).any(|d| d.join(nome).is_file()))
        .unwrap_or(false)
        || ["/usr/sbin", "/sbin", "/usr/bin", "/bin"]
            .iter()
            .any(|d| Path::new(d).join(nome).is_file())
}

fn placas_de_video() -> Vec<String> {
    let mut placas = Vec::new();
    if comando_existe("lspci")
        && let Ok(saida) = Command::new("lspci").output()
    {
        for l in String::from_utf8_lossy(&saida.stdout).lines() {
            if l.contains("VGA compatible")
                || l.contains("3D controller")
                || l.contains("Display controller")
            {
                placas.push(
                    l.split_once(": ")
                        .map(|(_, v)| v)
                        .unwrap_or(l)
                        .trim()
                        .to_string(),
                );
            }
        }
    }
    if placas.is_empty()
        && let Ok(entradas) = fs::read_dir("/sys/class/drm")
    {
        let mut nomes: Vec<_> = entradas.flatten().map(|e| e.path()).collect();
        nomes.sort();
        for p in nomes {
            let Some(n) = p.file_name().and_then(|n| n.to_str()) else {
                continue;
            };
            if !n.starts_with("card") || n.contains('-') {
                continue;
            }
            let Ok(codigo) = fs::read_to_string(p.join("device/vendor")) else {
                continue;
            };
            let nome = match codigo.trim() {
                "0x10de" => "NVIDIA",
                "0x1002" => "AMD",
                "0x8086" => "Intel",
                "0x1af4" | "0x15ad" | "0x1234" | "0x80ee" => "virtual",
                outro => outro,
            }
            .to_string();
            if !placas.contains(&nome) {
                placas.push(nome);
            }
        }
    }
    placas
}

fn virtualizacao() -> Option<String> {
    if comando_existe("systemd-detect-virt")
        && let Ok(s) = Command::new("systemd-detect-virt").output()
    {
        let v = String::from_utf8_lossy(&s.stdout).trim().to_string();
        if !v.is_empty() && v != "none" {
            return Some(v);
        }
        if s.status.success() || v == "none" {
            return None;
        }
    }
    Path::new("/.dockerenv")
        .exists()
        .then(|| "docker".to_string())
}

fn tem_rota_padrao() -> bool {
    fs::read_to_string("/proc/net/route")
        .map(|t| {
            t.lines()
                .skip(1)
                .any(|l| l.split_whitespace().nth(1) == Some("00000000"))
        })
        .unwrap_or(false)
}

fn firewall() -> Option<String> {
    if comando_existe("ufw") {
        Some("ufw".into())
    } else if comando_existe("firewall-cmd") {
        Some("firewalld".into())
    } else {
        None
    }
}

fn kernel() -> String {
    fs::read_to_string("/proc/sys/kernel/osrelease")
        .map(|s| s.trim().to_string())
        .unwrap_or_default()
}

/// Junta o diagnóstico completo.
pub fn coletar(os_release: Option<&Path>) -> Diag {
    let osr = ler_os_release(os_release);
    let (familia, base, motivo) = descobrir_familia(&osr, Path::new("/run/ostree-booted").exists());
    let maquina = std::env::consts::ARCH.to_string();
    let systemd = tem_systemd();
    let mut problemas = Vec::new();
    let mut avisos = Vec::new();

    if let Some(m) = motivo {
        problemas.push(m);
    }
    if maquina != "x86_64" && maquina != "aarch64" {
        problemas.push(format!(
            "a arquitetura {maquina} não é suportada; o bora precisa de 64 bits (x86_64 ou aarch64)"
        ));
    }
    if !systemd {
        if std::env::var("BORA_PERMITIR_SEM_SYSTEMD").as_deref() == Ok("1") {
            avisos.push("sem systemd, permitido só para testes em contêiner".into());
        } else {
            problemas.push(
                "o systemd não é o processo de inicialização; o bora só funciona com systemd"
                    .into(),
            );
        }
    }

    let ident = osr.get("ID").cloned().unwrap_or_default().to_lowercase();
    if let (Some(f), Some(b)) = (&familia, &base)
        && let Some((_, testadas)) = BASES_SUPORTADAS.iter().find(|(k, _)| k == f)
        && !testadas.contains(&b.as_str())
    {
        let b = if b.is_empty() { "desconhecida" } else { b };
        avisos.push(format!(
            "a versão {b} da base {f} ainda não foi testada; as testadas são {}",
            testadas.join(", ")
        ));
    }
    let conhecida = procurar(FAMILIA_POR_ID, &ident).is_some();
    if let Some(f) = &familia
        && !conhecida
        && !ident.is_empty()
    {
        let nome = osr.get("NAME").cloned().unwrap_or_else(|| ident.clone());
        avisos.push(format!(
            "{nome} é uma derivada que o bora não conhece; ela usa as receitas da família {f}"
        ));
    }
    let nome = osr
        .get("PRETTY_NAME")
        .or_else(|| osr.get("NAME"))
        .cloned()
        .unwrap_or_else(|| ident.clone());

    Diag {
        distro: Distro {
            derivada: DERIVADAS_CONHECIDAS.contains(&ident.as_str())
                || (familia.is_some() && !conhecida),
            id: ident,
            nome,
            versao: osr.get("VERSION_ID").cloned().unwrap_or_default(),
            familia,
            base,
        },
        sistema: Sistema {
            arquitetura: maquina,
            kernel: kernel(),
            systemd,
            uefi: Path::new("/sys/firmware/efi").is_dir(),
            virtualizacao: virtualizacao(),
            sistema_de_arquivos_raiz: sistema_de_arquivos_raiz(),
        },
        hardware: Hardware {
            processador: processador(),
            ram_gb: memoria_gb(),
            disco_livre_gb: disco_livre_gb("/"),
            video: placas_de_video(),
        },
        rede: Rede {
            rota_padrao: tem_rota_padrao(),
        },
        ja_tem: JaTem {
            snapshot: crate::snapshot::ferramenta().map(str::to_string),
            firewall: firewall(),
        },
        suportada: problemas.is_empty(),
        problemas,
        avisos,
    }
}

fn num(x: Option<f64>) -> String {
    match x {
        Some(v) if v.fract() == 0.0 => format!("{v:.0}"),
        Some(v) => format!("{v}"),
        None => "?".into(),
    }
}

/// Uma linha para o topo do menu.
pub fn resumo(d: &Diag) -> String {
    let mut partes = vec![d.distro.nome.clone()];
    if let Some(f) = &d.distro.familia {
        partes.push(format!("família {f}"));
    }
    if d.hardware.ram_gb.is_some() {
        partes.push(format!("{} GB de RAM", num(d.hardware.ram_gb)));
    }
    if d.hardware.disco_livre_gb.is_some() {
        partes.push(format!("{} GB livres", num(d.hardware.disco_livre_gb)));
    }
    partes.join(", ")
}

/// O diagnóstico completo, para ler no terminal.
pub fn formatar(d: &Diag) -> String {
    let sim = |v: bool| if v { "sim" } else { "não" };
    let dist = &d.distro;
    let base = match &dist.base {
        Some(b) if !b.is_empty() => format!(", base {b}"),
        _ => String::new(),
    };
    let mut linhas = vec![
        "Distro".to_string(),
        format!("  {}", dist.nome),
        format!(
            "  família: {}{base}",
            dist.familia.as_deref().unwrap_or("nenhuma")
        ),
        String::new(),
        "Sistema".into(),
        format!(
            "  arquitetura: {}, kernel {}",
            d.sistema.arquitetura, d.sistema.kernel
        ),
        format!(
            "  systemd: {}, UEFI: {}",
            sim(d.sistema.systemd),
            sim(d.sistema.uefi)
        ),
        format!(
            "  máquina virtual: {}",
            d.sistema.virtualizacao.as_deref().unwrap_or("não")
        ),
        format!(
            "  sistema de arquivos da raiz: {}",
            d.sistema
                .sistema_de_arquivos_raiz
                .as_deref()
                .unwrap_or("desconhecido")
        ),
        String::new(),
        "Hardware".into(),
        format!(
            "  processador: {} ({} núcleos)",
            d.hardware
                .processador
                .modelo
                .as_deref()
                .unwrap_or("desconhecido"),
            d.hardware.processador.nucleos
        ),
        format!("  memória: {} GB", num(d.hardware.ram_gb)),
        format!(
            "  disco livre na raiz: {} GB",
            num(d.hardware.disco_livre_gb)
        ),
        format!(
            "  vídeo: {}",
            if d.hardware.video.is_empty() {
                "não identificado".into()
            } else {
                d.hardware.video.join(", ")
            }
        ),
        String::new(),
        "Já tem".into(),
        format!(
            "  snapshot do sistema: {}",
            d.ja_tem.snapshot.as_deref().unwrap_or("não configurado")
        ),
        format!(
            "  firewall: {}",
            d.ja_tem.firewall.as_deref().unwrap_or("não instalado")
        ),
        format!(
            "  rede: {}",
            if d.rede.rota_padrao {
                "conectada"
            } else {
                "sem rota para a internet"
            }
        ),
    ];
    if !d.problemas.is_empty() {
        linhas.push(String::new());
        linhas.push("Não dá para usar o bora aqui:".into());
        linhas.extend(d.problemas.iter().map(|p| format!("  - {p}")));
    }
    if !d.avisos.is_empty() {
        linhas.push(String::new());
        linhas.push("Avisos:".into());
        linhas.extend(d.avisos.iter().map(|a| format!("  - {a}")));
    }
    linhas.join("\n")
}

#[cfg(test)]
mod testes {
    use super::*;
    use std::path::PathBuf;

    fn fixo(nome: &str) -> BTreeMap<String, String> {
        let p = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("testes/os-release")
            .join(nome);
        ler_os_release(Some(&p))
    }

    #[test]
    fn familias() {
        let casos = [
            ("ubuntu-26.04", "ubuntu", "26.04"),
            ("ubuntu-24.04", "ubuntu", "24.04"),
            ("ubuntu-25.10", "ubuntu", "25.10"),
            ("linuxmint-22.2", "ubuntu", "24.04"),
            ("pop-24.04", "ubuntu", "24.04"),
            ("zorin-18", "ubuntu", "24.04"),
            ("elementary-8", "ubuntu", "24.04"),
            ("debian-13", "debian", "13"),
            ("kali", "debian", "2026.3"),
            ("fedora-43", "fedora", "43"),
            ("nobara-43", "fedora", "43"),
            ("silverblue-43", "fedora-imutavel", "43"),
            ("bazzite", "fedora-imutavel", "43"),
            ("cachyos", "arch", ""),
            ("manjaro", "arch", ""),
            ("opensuse-tumbleweed", "opensuse", "20261101"),
        ];
        for (nome, familia, base) in casos {
            let (f, b, motivo) = descobrir_familia(&fixo(nome), false);
            assert_eq!(motivo, None, "{nome}");
            assert_eq!(
                (f.as_deref(), b.as_deref()),
                (Some(familia), Some(base)),
                "{nome}"
            );
        }
    }

    #[test]
    fn fora_do_escopo() {
        for (nome, trecho) in [
            ("mx-25", "systemd"),
            ("alpine", "systemd"),
            ("nixos", "declarativa"),
            ("debian-sid", "estável"),
        ] {
            let (f, _, motivo) = descobrir_familia(&fixo(nome), false);
            assert_eq!(f, None, "{nome}");
            assert!(motivo.unwrap().contains(trecho), "{nome}");
        }
    }

    #[test]
    fn fedora_com_ostree_vira_imutavel() {
        assert_eq!(
            descobrir_familia(&fixo("fedora-43"), true).0.as_deref(),
            Some("fedora-imutavel")
        );
    }

    #[test]
    fn desconhecida() {
        let mut osr = BTreeMap::new();
        osr.insert("ID".to_string(), "inventada".to_string());
        osr.insert("PRETTY_NAME".to_string(), "Inventada 1".to_string());
        let (f, _, motivo) = descobrir_familia(&osr, false);
        assert_eq!(f, None);
        assert!(motivo.unwrap().contains("Inventada 1"));
    }

    #[test]
    fn coletar_e_formatar() {
        let p = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("testes/os-release/kali");
        let d = coletar(Some(&p));
        assert_eq!(d.distro.familia.as_deref(), Some("debian"));
        assert!(d.avisos.iter().any(|a| a.contains("derivada")));
        assert!(d.avisos.iter().any(|a| a.contains("não foi testada")));
        assert!(formatar(&d).contains("Distro"));
    }
}
