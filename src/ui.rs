//! Saída no terminal e perguntas simples.

use std::io::{self, BufRead, IsTerminal, Write};

/// O que pode interromper um comando: uma mensagem de erro ou a pessoa desistindo.
#[derive(Debug)]
pub enum Erro {
    Msg(String),
    /// Erro já mostrado; só sai com este código.
    Codigo(i32),
    Cancelado,
}

impl From<String> for Erro {
    fn from(s: String) -> Self {
        Erro::Msg(s)
    }
}

impl From<&str> for Erro {
    fn from(s: &str) -> Self {
        Erro::Msg(s.to_string())
    }
}

impl From<io::Error> for Erro {
    fn from(e: io::Error) -> Self {
        Erro::Msg(e.to_string())
    }
}

pub type R<T> = Result<T, Erro>;

fn com_cor() -> bool {
    io::stdout().is_terminal()
        && std::env::var_os("NO_COLOR").is_none()
        && std::env::var("TERM").map(|t| t != "dumb").unwrap_or(true)
}

fn cor(codigo: &str, texto: &str) -> String {
    if com_cor() {
        format!("\x1b[{codigo}m{texto}\x1b[0m")
    } else {
        texto.to_string()
    }
}

pub fn negrito(t: &str) -> String {
    cor("1", t)
}
pub fn verde(t: &str) -> String {
    cor("32", t)
}
pub fn amarelo(t: &str) -> String {
    cor("33", t)
}
pub fn vermelho(t: &str) -> String {
    cor("31", t)
}
pub fn apagado(t: &str) -> String {
    cor("2", t)
}

pub fn titulo(t: &str) {
    println!();
    println!("{}", negrito(t));
}

pub fn ok(t: &str) {
    println!("{}{t}", verde("✓ "));
}

pub fn aviso(t: &str) {
    println!("{}{t}", amarelo("! "));
}

pub fn erro(t: &str) {
    eprintln!("{}{t}", vermelho("✗ "));
}

pub fn info(t: &str) {
    println!("  {t}");
}

fn ler(prompt: &str) -> R<String> {
    print!("{prompt}");
    io::stdout().flush().ok();
    let mut linha = String::new();
    match io::stdin().lock().read_line(&mut linha) {
        Ok(0) => Err(Erro::Cancelado),
        Ok(_) => Ok(linha.trim_end_matches(['\n', '\r']).to_string()),
        Err(_) => Err(Erro::Cancelado),
    }
}

pub fn perguntar(texto: &str, padrao: Option<&str>) -> R<String> {
    let sufixo = match padrao {
        Some(p) if !p.is_empty() => format!(" [{p}]"),
        _ => String::new(),
    };
    let resposta = ler(&format!("{texto}{sufixo}: "))?;
    let resposta = resposta.trim();
    if resposta.is_empty() {
        Ok(padrao.unwrap_or("").to_string())
    } else {
        Ok(resposta.to_string())
    }
}

pub fn confirmar(texto: &str, padrao: bool) -> R<bool> {
    let opcoes = if padrao { "S/n" } else { "s/N" };
    loop {
        let r = ler(&format!("{texto} [{opcoes}] "))?.trim().to_lowercase();
        match r.as_str() {
            "" => return Ok(padrao),
            "s" | "sim" | "y" | "yes" => return Ok(true),
            "n" | "não" | "nao" | "no" => return Ok(false),
            _ => println!("Responda s para sim ou n para não."),
        }
    }
}

/// Uma opção de menu: rótulo, detalhe e se está disponível.
pub struct Opcao {
    pub rotulo: String,
    pub detalhe: String,
    pub disponivel: bool,
}

impl Opcao {
    pub fn new(rotulo: impl Into<String>, detalhe: impl Into<String>, disponivel: bool) -> Self {
        Opcao {
            rotulo: rotulo.into(),
            detalhe: detalhe.into(),
            disponivel,
        }
    }
}

fn mostrar_opcoes(texto: &str, opcoes: &[Opcao]) {
    println!("{texto}");
    for (i, o) in opcoes.iter().enumerate() {
        let mut linha = format!("  {:>2}. {}", i + 1, o.rotulo);
        if !o.detalhe.is_empty() {
            if o.disponivel {
                linha.push_str(&apagado(&format!("  {}", o.detalhe)));
            } else {
                linha.push_str(&apagado(&format!("  ({})", o.detalhe)));
            }
        }
        if o.disponivel {
            println!("{linha}");
        } else {
            println!("{}", apagado(&linha));
        }
    }
}

/// Mostra opções numeradas e devolve o índice escolhido.
pub fn escolher(texto: &str, opcoes: &[Opcao], padrao: Option<usize>) -> R<usize> {
    mostrar_opcoes(texto, opcoes);
    loop {
        let dica = padrao.map(|p| format!(" [{}]", p + 1)).unwrap_or_default();
        let bruto = ler(&format!("Número{dica}: "))?;
        let bruto = bruto.trim();
        if bruto.is_empty()
            && let Some(p) = padrao
        {
            return Ok(p);
        }
        match bruto.parse::<usize>() {
            Ok(n) if n >= 1 && n <= opcoes.len() => {
                if opcoes[n - 1].disponivel {
                    return Ok(n - 1);
                }
                println!("Essa opção não está disponível nesta máquina.");
            }
            _ => println!("Digite um número de 1 a {}.", opcoes.len()),
        }
    }
}

/// Devolve os índices escolhidos, em ordem. Vazio quando a pessoa só aperta Enter.
pub fn escolher_varios(texto: &str, opcoes: &[Opcao]) -> R<Vec<usize>> {
    mostrar_opcoes(texto, opcoes);
    loop {
        let bruto = ler("Números separados por espaço (Enter para voltar): ")?.replace(',', " ");
        let partes: Vec<&str> = bruto.split_whitespace().collect();
        if partes.is_empty() {
            return Ok(vec![]);
        }
        let mut indices = Vec::new();
        let mut valido = true;
        for p in partes {
            match p.parse::<usize>() {
                Ok(n) if n >= 1 && n <= opcoes.len() && opcoes[n - 1].disponivel => {
                    indices.push(n - 1)
                }
                _ => valido = false,
            }
        }
        if valido {
            indices.sort_unstable();
            indices.dedup();
            return Ok(indices);
        }
        println!("Algum número não existe ou não está disponível nesta máquina.");
    }
}
