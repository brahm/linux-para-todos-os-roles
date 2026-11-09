//! Modelos de IA locais: quais cabem nesta máquina e qual o bora sugere.
//!
//! A lista mora em `receitas/ia/ollama/modelos.yaml`, junto com a receita que
//! baixa o modelo. A conta é de propósito simples, para qualquer pessoa
//! conferir: o modelo ocupa na memória o tamanho do download, mais 15% e mais
//! 1,5 GB para o contexto da conversa. Na placa de vídeo, ele precisa caber
//! inteiro na memória dela. Sem placa, ele usa a RAM, deixando 3 GB para o
//! sistema e o editor, e a velocidade depende de quantos parâmetros ele usa a
//! cada palavra.

use crate::diag::Diag;
use serde::{Deserialize, Serialize};
use std::fs;
use std::path::{Path, PathBuf};

/// O que sobra da RAM para o modelo, depois do sistema, do editor e do navegador.
const RESERVA_DO_SISTEMA_GB: f64 = 3.0;
/// Espaço livre no disco além do modelo.
const FOLGA_NO_DISCO_GB: f64 = 5.0;

#[derive(Debug, Clone, Deserialize, Serialize)]
#[serde(deny_unknown_fields)]
pub struct Modelo {
    pub ollama: String,
    pub nome: String,
    pub tamanho_gb: f64,
    pub ativos_b: f64,
    pub agente: bool,
    pub nota: String,
}

#[derive(Debug, Clone, Deserialize)]
#[serde(deny_unknown_fields)]
pub struct Lista {
    pub verificado_em: String,
    pub modelos: Vec<Modelo>,
}

impl Modelo {
    /// Memória que o modelo ocupa rodando, com o contexto de uma conversa.
    pub fn memoria_gb(&self) -> f64 {
        ((self.tamanho_gb * 1.15 + 1.5) * 10.0).round() / 10.0
    }
}

/// Onde e como o modelo roda nesta máquina.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize)]
#[serde(rename_all = "kebab-case")]
pub enum Lugar {
    /// Cabe inteiro na placa de vídeo: rápido.
    Placa,
    /// Na RAM, com poucos parâmetros por palavra: anda bem.
    CpuBom,
    /// Na RAM, devagar, mas dá para usar.
    CpuDevagar,
    /// Cabe na RAM, mas lento demais para um agente.
    CpuLento,
    NaoCabe,
    FaltaDisco,
}

impl Lugar {
    pub fn roda_bem(self) -> bool {
        matches!(self, Lugar::Placa | Lugar::CpuBom)
    }

    pub fn usavel(self) -> bool {
        matches!(self, Lugar::Placa | Lugar::CpuBom | Lugar::CpuDevagar)
    }

    pub fn descricao(self) -> &'static str {
        match self {
            Lugar::Placa => "cabe na placa de vídeo: rápido",
            Lugar::CpuBom => "roda na memória, sem placa de vídeo: anda bem",
            Lugar::CpuDevagar => "roda na memória, sem placa de vídeo: devagar",
            Lugar::CpuLento => "cabe na memória, mas fica lento demais",
            Lugar::NaoCabe => "não cabe na memória",
            Lugar::FaltaDisco => "falta espaço no disco",
        }
    }
}

pub fn caminho(raiz: &Path) -> PathBuf {
    raiz.join("receitas/ia/ollama/modelos.yaml")
}

pub fn carregar(raiz: &Path) -> Result<Lista, String> {
    let p = caminho(raiz);
    let texto = fs::read_to_string(&p)
        .map_err(|e| format!("não consegui ler a lista de modelos {}: {e}", p.display()))?;
    let lista: Lista = serde_norway::from_str(&texto)
        .map_err(|e| format!("a lista de modelos {} tem um erro: {e}", p.display()))?;
    conferir(&lista).map_err(|e| format!("{}: {e}", p.display()))?;
    Ok(lista)
}

static NOME_OLLAMA: std::sync::LazyLock<regex::Regex> = std::sync::LazyLock::new(|| {
    regex::Regex::new(r"^[a-z0-9][a-z0-9._-]*(/[a-z0-9][a-z0-9._-]*)?(:[A-Za-z0-9._-]+)?$").unwrap()
});

/// Um nome de modelo que dá para passar ao "ollama pull" sem surpresa.
pub fn nome_valido(nome: &str) -> bool {
    nome.len() <= 120 && NOME_OLLAMA.is_match(nome)
}

fn conferir(l: &Lista) -> Result<(), String> {
    if l.modelos.is_empty() {
        return Err("a lista de modelos está vazia".into());
    }
    let mut vistos: Vec<&str> = Vec::new();
    for m in &l.modelos {
        if !nome_valido(&m.ollama) {
            return Err(format!("nome de modelo inválido: {}", m.ollama));
        }
        if vistos.contains(&m.ollama.as_str()) {
            return Err(format!("o modelo {} aparece duas vezes", m.ollama));
        }
        vistos.push(&m.ollama);
        if m.tamanho_gb <= 0.0 || m.ativos_b <= 0.0 {
            return Err(format!(
                "{}: tamanho_gb e ativos_b precisam ser maiores que zero",
                m.ollama
            ));
        }
        if m.nome.trim().is_empty() || m.nota.trim().is_empty() {
            return Err(format!("{}: falta o nome ou a nota", m.ollama));
        }
    }
    Ok(())
}

/// A memória e o disco que contam para a conta.
#[derive(Debug, Clone, Copy, Default, Serialize)]
pub struct Maquina {
    pub ram_gb: Option<f64>,
    pub vram_gb: Option<f64>,
    pub disco_livre_gb: Option<f64>,
}

impl Maquina {
    pub fn de(d: &Diag) -> Self {
        Maquina {
            ram_gb: d.hardware.ram_gb,
            vram_gb: d.hardware.vram_gb,
            disco_livre_gb: d.hardware.disco_livre_gb,
        }
    }
}

pub fn avaliar(m: &Modelo, maq: &Maquina) -> Lugar {
    let precisa = m.memoria_gb();
    if let Some(livre) = maq.disco_livre_gb
        && livre < m.tamanho_gb + FOLGA_NO_DISCO_GB
    {
        return Lugar::FaltaDisco;
    }
    if maq.vram_gb.is_some_and(|v| precisa <= v) {
        return Lugar::Placa;
    }
    let ram = maq.ram_gb.unwrap_or(0.0) - RESERVA_DO_SISTEMA_GB;
    if precisa > ram {
        return Lugar::NaoCabe;
    }
    if m.ativos_b <= 6.0 {
        Lugar::CpuBom
    } else if m.ativos_b <= 10.0 {
        Lugar::CpuDevagar
    } else {
        Lugar::CpuLento
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct Sugestao {
    pub modelo: Option<Modelo>,
    pub lugar: Option<Lugar>,
    /// Uma frase sobre a escolha, para mostrar à pessoa.
    pub motivo: String,
}

/// O último modelo da lista (o mais capaz) que roda bem; senão, o mais capaz
/// que dá para usar. Um agente vem antes de um modelo só de conversa.
pub fn sugerir(l: &Lista, maq: &Maquina) -> Sugestao {
    let avaliados: Vec<(&Modelo, Lugar)> = l.modelos.iter().map(|m| (m, avaliar(m, maq))).collect();
    let achar = |f: &dyn Fn(&Modelo, Lugar) -> bool| {
        avaliados
            .iter()
            .rev()
            .find(|(m, lugar)| f(m, *lugar))
            .copied()
    };
    let escolha = achar(&|m, lugar| m.agente && lugar.roda_bem())
        .map(|e| (e, ""))
        .or_else(|| {
            achar(&|m, lugar| m.agente && lugar.usavel()).map(|e| {
                (
                    e,
                    " Sem placa de vídeo, ele responde devagar: dá para usar, com paciência.",
                )
            })
        })
        .or_else(|| {
            achar(&|_, lugar| lugar.usavel()).map(|e| {
                (
                    e,
                    " Nenhum modelo bom para agentes cabe aqui; este serve para conversar e tirar dúvidas, e o agente fica melhor com um modelo na nuvem.",
                )
            })
        });
    match escolha {
        Some(((m, lugar), ressalva)) => Sugestao {
            modelo: Some(m.clone()),
            lugar: Some(lugar),
            motivo: format!(
                "{} ({}, {} GB): {}.{ressalva}",
                m.nome,
                m.ollama,
                num(m.tamanho_gb),
                lugar.descricao()
            ),
        },
        None => Sugestao {
            modelo: None,
            lugar: None,
            motivo: if avaliados.iter().all(|(_, l)| *l == Lugar::FaltaDisco) {
                "nenhum modelo da lista, porque falta espaço no disco".into()
            } else {
                "nenhum modelo da lista, porque esta máquina tem pouca memória para rodar um modelo local; use um modelo na nuvem".into()
            },
        },
    }
}

pub fn num(x: f64) -> String {
    if x.fract() == 0.0 {
        format!("{x:.0}")
    } else {
        format!("{x}").replace('.', ",")
    }
}

/// A tabela do "bora modelos".
pub fn formatar(l: &Lista, maq: &Maquina, video: &[String]) -> String {
    let mut linhas = Vec::new();
    let ram = maq.ram_gb.map(num).unwrap_or_else(|| "?".into());
    let placa = match maq.vram_gb {
        Some(v) => format!("placa de vídeo com {} GB", num(v)),
        None => "sem placa de vídeo medida".into(),
    };
    let disco = maq.disco_livre_gb.map(num).unwrap_or_else(|| "?".into());
    linhas.push(format!(
        "Esta máquina: {ram} GB de RAM, {placa}, {disco} GB livres no disco."
    ));
    if maq.vram_gb.is_none() && video.iter().any(|v| v.contains("NVIDIA")) {
        linhas.push(
            "A placa NVIDIA está sem o driver (falta o nvidia-smi). Com o driver instalado, o bora mede a placa e o Ollama passa a usá-la."
                .into(),
        );
    }
    linhas.push(String::new());
    for m in &l.modelos {
        let lugar = avaliar(m, maq);
        let marca = if lugar.roda_bem() {
            "●"
        } else if lugar.usavel() {
            "◐"
        } else {
            "○"
        };
        linhas.push(format!(
            "  {marca} {:<22} {:>5} GB  {}{}",
            m.ollama,
            num(m.tamanho_gb),
            lugar.descricao(),
            if m.agente {
                ""
            } else {
                " (não serve para agente)"
            }
        ));
        linhas.push(format!("      {}", m.nota));
    }
    linhas.push(String::new());
    let s = sugerir(l, maq);
    linhas.push(format!("Sugestão do bora: {}", s.motivo));
    if let Some(m) = &s.modelo {
        linhas.push(format!("  No Ollama: ollama pull {}", m.ollama));
        linhas.push(format!(
            "  No LM Studio: procure \"{}\" na aba Discover",
            m.nome
        ));
    }
    linhas.push(format!(
        "Lista conferida em {}. A conta: o modelo ocupa o tamanho dele, mais 15% e mais 1,5 GB para a conversa; sem placa de vídeo, ficam 3 GB da RAM para o sistema.",
        l.verificado_em
    ));
    linhas.join("\n")
}

#[cfg(test)]
mod testes {
    use super::*;

    fn lista() -> Lista {
        carregar(Path::new(env!("CARGO_MANIFEST_DIR"))).expect("a lista de modelos do repositório")
    }

    fn maquina(ram: f64, vram: Option<f64>) -> Maquina {
        Maquina {
            ram_gb: Some(ram),
            vram_gb: vram,
            disco_livre_gb: Some(200.0),
        }
    }

    fn sugerido(ram: f64, vram: Option<f64>) -> Option<String> {
        sugerir(&lista(), &maquina(ram, vram))
            .modelo
            .map(|m| m.ollama)
    }

    #[test]
    fn a_lista_do_repositorio_e_valida() {
        let l = lista();
        assert!(l.modelos.iter().any(|m| m.agente));
    }

    #[test]
    fn sugestoes_por_maquina() {
        // Notebook velho: não cabe nada útil.
        assert_eq!(sugerido(2.0, None), None);
        // 8 GB sem placa: só um modelo de conversa.
        assert_eq!(sugerido(8.0, None).as_deref(), Some("qwen3:4b"));
        // 16 GB sem placa: um agente pequeno, devagar.
        assert_eq!(sugerido(16.0, None).as_deref(), Some("mimo-v2.6:9b-q4_K_M"));
        // 24 GB sem placa: o gpt-oss, que usa poucos parâmetros por vez.
        assert_eq!(sugerido(24.0, None).as_deref(), Some("gpt-oss:20b"));
        // 32 GB sem placa: o Qwen3 Coder, e não o 27B denso, que seria lento.
        assert_eq!(sugerido(32.0, None).as_deref(), Some("qwen3-coder:30b"));
        // Placa de 8 GB: o Ornith 9B cabe nela inteiro; o MiMo, não.
        assert_eq!(
            sugerido(16.0, Some(8.0)).as_deref(),
            Some("ornith:9b-q4_K_M")
        );
        // Placa de 24 GB: o 27B denso cabe na placa e fica rápido.
        assert_eq!(
            sugerido(32.0, Some(24.0)).as_deref(),
            Some("qwen3.8:27b-q4_K_M")
        );
        // Muita memória: o maior.
        assert_eq!(sugerido(128.0, None).as_deref(), Some("gpt-oss:120b"));
    }

    #[test]
    fn disco_cheio() {
        let maq = Maquina {
            ram_gb: Some(64.0),
            vram_gb: None,
            disco_livre_gb: Some(3.0),
        };
        let s = sugerir(&lista(), &maq);
        assert!(s.modelo.is_none());
        assert!(s.motivo.contains("disco"));
    }

    #[test]
    fn nomes() {
        assert!(nome_valido("qwen3:4b"));
        assert!(nome_valido("mimo-v2.6:9b-q4_K_M"));
        assert!(!nome_valido("hf.co/usuario/modelo:Q4_K_M"));
        assert!(nome_valido("usuario/modelo:latest"));
        assert!(!nome_valido("qwen3; rm -rf /"));
        assert!(!nome_valido("-qwen"));
        assert!(!nome_valido(""));
    }

    #[test]
    fn tabela() {
        let t = formatar(&lista(), &maquina(16.0, None), &["NVIDIA".into()]);
        assert!(t.contains("Sugestão do bora"));
        assert!(t.contains("sem o driver"));
        assert!(t.contains("ollama pull"));
    }
}
