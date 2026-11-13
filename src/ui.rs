//! Saída no terminal e perguntas simples.
//!
//! Tudo o que o `bora` mostra ou pergunta passa por aqui: cores, títulos, avisos,
//! menus numerados e perguntas de sim ou não. Não tem biblioteca de interface:
//! é `print!` e `read_line`, para funcionar em qualquer terminal, até por SSH.

use std::io::{self, BufRead, IsTerminal, Write};

/// O que pode interromper um comando: uma mensagem de erro ou a pessoa desistindo.
#[derive(Debug)]
pub enum Erro {
    /// Erro que ainda precisa ser mostrado na tela.
    Msg(String),
    /// Erro já mostrado; só sai com este código.
    Codigo(i32),
    /// A pessoa apertou Ctrl+D ou a entrada acabou: sai sem mudar nada.
    Cancelado,
}

// As conversões abaixo deixam usar `?` com textos e erros de E/S direto
// nas funções que devolvem `R<T>`.
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

/// O `Result` de quase todo o `bora`.
pub type R<T> = Result<T, Erro>;

/// Só usa cor quando a saída é um terminal de verdade. Respeita `NO_COLOR`
/// (no-color.org) e `TERM=dumb`, e não suja arquivo nem pipe com códigos ANSI.
fn com_cor() -> bool {
    io::stdout().is_terminal()
        && std::env::var_os("NO_COLOR").is_none()
        && std::env::var("TERM").map(|t| t != "dumb").unwrap_or(true)
}

/// Pinta o texto com um código ANSI ("1" negrito, "2" apagado, "3x" cores).
fn cor(codigo: &str, texto: &str) -> String {
    if com_cor() {
        format!("\x1b[{codigo}m{texto}\x1b[0m")
    } else {
        texto.to_string()
    }
}

// Atalhos de cor. O texto volta sem mudança quando não há cor.
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

/// Título de seção, com uma linha em branco antes.
pub fn titulo(t: &str) {
    println!();
    println!("{}", negrito(t));
}

/// Linha de sucesso, com ✓ verde.
pub fn ok(t: &str) {
    println!("{}{t}", verde("✓ "));
}

/// Linha de aviso, com ! amarelo. Não para nada.
pub fn aviso(t: &str) {
    println!("{}{t}", amarelo("! "));
}

/// Linha de erro, com ✗ vermelho. Vai para a saída de erro.
pub fn erro(t: &str) {
    eprintln!("{}{t}", vermelho("✗ "));
}

/// Linha de informação, recuada, sem marca.
pub fn info(t: &str) {
    println!("  {t}");
}

/// Mostra o prompt e lê uma linha. Fim da entrada (Ctrl+D) vira `Cancelado`,
/// para o `bora` não ficar perguntando em loop para um terminal que fechou.
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

/// Pergunta de texto livre. Enter vazio fica com o padrão, mostrado entre colchetes.
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

/// Pergunta de sim ou não. A letra maiúscula em `[S/n]` é o padrão do Enter.
/// Aceita português e inglês, porque o dedo às vezes digita `y` no automático.
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
    /// Cria uma opção. Aceita `&str` ou `String` para não encher o código de `.into()`.
    pub fn new(rotulo: impl Into<String>, detalhe: impl Into<String>, disponivel: bool) -> Self {
        Opcao {
            rotulo: rotulo.into(),
            detalhe: detalhe.into(),
            disponivel,
        }
    }
}

/// Imprime as opções numeradas a partir de 1. As indisponíveis saem apagadas,
/// com o motivo entre parênteses.
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

/// Mostra opções numeradas e devolve o índice escolhido (a partir de 0).
/// Repete a pergunta até vir um número válido de uma opção disponível.
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

/// Escolha múltipla: aceita números separados por espaço ou vírgula.
/// Devolve os índices escolhidos, em ordem e sem repetição. Vazio quando a
/// pessoa só aperta Enter.
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
