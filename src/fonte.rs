//! De onde vem o catálogo: de dentro do próprio binário ou de uma pasta.
//!
//! O binário publicado leva as receitas e os rolês embutidos, então basta um
//! arquivo para usar o bora. Quem está desenvolvendo aponta `BORA_RAIZ` para a
//! pasta do repositório e testa as mudanças sem recompilar.

use include_dir::{Dir, DirEntry, include_dir};
use std::fs;
use std::io;
use std::os::unix::fs::{DirBuilderExt, PermissionsExt};
use std::path::{Path, PathBuf};

static RECEITAS: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/receitas");
static OBJETIVOS: Dir<'_> = include_dir!("$CARGO_MANIFEST_DIR/objetivos");

/// A pasta do catálogo. Quando é uma cópia temporária do que vem embutido,
/// ela é apagada ao sair.
pub struct Fonte {
    pub raiz: PathBuf,
    temporaria: bool,
}

impl Drop for Fonte {
    fn drop(&mut self) {
        if self.temporaria && self.raiz.starts_with(std::env::temp_dir()) {
            let _ = fs::remove_dir_all(&self.raiz);
        }
    }
}

fn extrair(dir: &Dir, destino: &Path) -> io::Result<()> {
    for entrada in dir.entries() {
        let caminho = destino.join(entrada.path().file_name().unwrap_or_default());
        match entrada {
            DirEntry::Dir(d) => {
                fs::DirBuilder::new().mode(0o700).create(&caminho)?;
                extrair(d, &caminho)?;
            }
            DirEntry::File(f) => {
                fs::write(&caminho, f.contents())?;
                // Os scripts são os .sh que não são arquivos de funções.
                let nome = caminho.file_name().unwrap_or_default().to_string_lossy();
                let executavel = nome.ends_with(".sh") && f.contents().starts_with(b"#!");
                fs::set_permissions(
                    &caminho,
                    fs::Permissions::from_mode(if executavel { 0o755 } else { 0o644 }),
                )?;
            }
        }
    }
    Ok(())
}

pub fn abrir() -> io::Result<Fonte> {
    if let Some(raiz) = std::env::var_os("BORA_RAIZ") {
        return Ok(Fonte {
            raiz: PathBuf::from(raiz),
            temporaria: false,
        });
    }
    // Pasta nova, com nome aleatório e só para o dono: o bora roda como root,
    // e ninguém pode ter preparado essa pasta antes dele.
    let base = std::env::temp_dir();
    let mut tentativa = 0;
    let raiz = loop {
        let mut aleatorio = [0u8; 8];
        fs::File::open("/dev/urandom")
            .and_then(|mut f| io::Read::read_exact(&mut f, &mut aleatorio))?;
        let nome: String = aleatorio.iter().map(|b| format!("{b:02x}")).collect();
        let raiz = base.join(format!("bora-catalogo-{nome}"));
        match fs::DirBuilder::new().mode(0o700).create(&raiz) {
            Ok(()) => break raiz,
            Err(e) if e.kind() == io::ErrorKind::AlreadyExists && tentativa < 5 => tentativa += 1,
            Err(e) => return Err(e),
        }
    };
    let fonte = Fonte {
        raiz: raiz.clone(),
        temporaria: true,
    };
    for (nome, dir) in [("receitas", &RECEITAS), ("objetivos", &OBJETIVOS)] {
        let destino = raiz.join(nome);
        fs::DirBuilder::new().mode(0o700).create(&destino)?;
        extrair(dir, &destino)?;
    }
    Ok(fonte)
}
