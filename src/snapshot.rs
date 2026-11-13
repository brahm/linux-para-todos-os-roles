//! Snapshot do sistema antes de aplicar um plano.

use std::fs;
use std::os::unix::process::ExitStatusExt;
use std::path::Path;
use std::process::Command;

/// Qual ferramenta de snapshot está pronta para uso.
pub fn ferramenta() -> Option<&'static str> {
    if crate::diag::comando_existe("timeshift")
        && let Ok(t) = fs::read_to_string("/etc/timeshift/timeshift.json")
        && let Ok(v) = serde_json::from_str::<serde_json::Value>(&t)
        && v.get("backup_device_uuid")
            .and_then(|u| u.as_str())
            .is_some_and(|u| !u.is_empty())
    {
        return Some("timeshift");
    }
    if crate::diag::comando_existe("snapper") && Path::new("/etc/snapper/configs/root").exists() {
        return Some("snapper");
    }
    if Path::new("/run/ostree-booted").exists() {
        return Some("ostree");
    }
    None
}

/// Cria o snapshot e devolve um nome para mostrar, ou a mensagem de erro.
pub fn criar(descricao: &str) -> Result<String, String> {
    let saida = match ferramenta() {
        Some("timeshift") => {
            let rodar = || {
                Command::new("timeshift")
                    .args(["--create", "--scripted", "--comments", descricao])
                    .output()
            };
            // Até a versão 26.11.0, o Timeshift às vezes cai com segfault logo
            // no começo, antes de copiar qualquer coisa (issue #16). A causa é
            // uma corrida entre duas threads dele, corrigida em linuxmint/timeshift#552.
            // Enquanto as distros trazem versões antigas, uma segunda tentativa resolve.
            match rodar() {
                Ok(s) if s.status.signal().is_some() => rodar(),
                outro => outro,
            }
        }
        Some("snapper") => Command::new("snapper")
            .args([
                "-c",
                "root",
                "create",
                "--print-number",
                "--cleanup-algorithm",
                "number",
                "--description",
                descricao,
            ])
            .output(),
        _ => return Err("nenhuma ferramenta de snapshot configurada".into()),
    }
    .map_err(|e| e.to_string())?;
    let texto = String::from_utf8_lossy(&saida.stdout).to_string();
    if !saida.status.success() {
        let erro = String::from_utf8_lossy(&saida.stderr).to_string();
        let tudo = if erro.trim().is_empty() { texto } else { erro };
        return Err(tudo
            .trim()
            .chars()
            .rev()
            .take(800)
            .collect::<String>()
            .chars()
            .rev()
            .collect());
    }
    match ferramenta() {
        Some("snapper") => Ok(format!("snapper #{}", texto.trim())),
        _ => {
            // O Timeshift sai com código 0 mesmo quando não consegue criar o snapshot.
            if !texto.contains("saved successfully") {
                return Err(texto
                    .trim()
                    .lines()
                    .last()
                    .unwrap_or("o Timeshift não criou o snapshot")
                    .to_string());
            }
            Ok(format!(
                "timeshift, {}",
                chrono::Local::now().format("%Y-%m-%d %H:%M")
            ))
        }
    }
}

pub fn como_restaurar() -> Option<&'static str> {
    match ferramenta() {
        Some("timeshift") => Some("sudo timeshift --restore (ou o aplicativo Timeshift)"),
        Some("snapper") => Some("sudo snapper -c root undochange NÚMERO..0"),
        _ => None,
    }
}
