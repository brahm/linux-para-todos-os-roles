//! O plano: a lista de receitas, com parâmetros, que o bora aplica em ordem.
//!
//! Um plano é um arquivo YAML que qualquer pessoa ou agente de IA consegue
//! escrever e revisar:
//!
//! ```yaml
//! bora: 1
//! objetivo: pronto-para-estudar     # opcional; vazio para receitas avulsas
//! familia: ubuntu
//! passos:
//!   - receita: base/atualizar
//!   - receita: seguranca/firewall
//!     parametros:
//!       perfil: desktop
//! ```

use crate::catalogo::{self as cat, Catalogo, Receita, Role, Valor, texto_de};
use crate::diag::Diag;
use serde_norway::{Mapping, Value};
use std::collections::BTreeMap;
use std::fs;
use std::path::Path;

pub const FORMATO: u64 = 1;

#[derive(Debug, Clone)]
pub struct Passo {
    pub receita: Receita,
    pub parametros: Vec<(String, Valor)>,
}

#[derive(Debug, Clone)]
pub struct PlanoValidado {
    pub objetivo: Option<String>,
    pub familia: String,
    pub passos: Vec<Passo>,
    pub avisos: Vec<String>,
}

fn s(t: &str) -> Value {
    Value::String(t.to_string())
}

fn cabecalho(objetivo: Option<&str>, familia: &str, passos: Vec<Value>) -> Value {
    let mut m = Mapping::new();
    m.insert(s("bora"), Value::Number(FORMATO.into()));
    m.insert(
        s("criado_em"),
        s(&chrono::Local::now().format("%Y-%m-%dT%H:%M:%S").to_string()),
    );
    m.insert(s("objetivo"), objetivo.map(s).unwrap_or(Value::Null));
    m.insert(s("familia"), s(familia));
    m.insert(s("passos"), Value::Sequence(passos));
    Value::Mapping(m)
}

fn passo(id: &str, parametros: Mapping) -> Value {
    let mut p = Mapping::new();
    p.insert(s("receita"), s(id));
    if !parametros.is_empty() {
        p.insert(s("parametros"), Value::Mapping(parametros));
    }
    Value::Mapping(p)
}

/// Plano a partir de um rolê e das respostas às perguntas dele.
pub fn montar_de_role(
    role: &Role,
    respostas: &BTreeMap<String, String>,
    familia: &str,
) -> Result<Value, String> {
    let mut completas = BTreeMap::new();
    for p in &role.perguntas {
        match respostas
            .get(&p.id)
            .filter(|r| !r.is_empty())
            .or(p.padrao.as_ref())
        {
            Some(r) if !p.opcoes.is_empty() && !p.opcoes.contains(r) => {
                return Err(format!(
                    "a resposta para {} precisa ser uma destas opções: {}",
                    p.id,
                    p.opcoes.join(", ")
                ));
            }
            Some(r) => {
                completas.insert(p.id.clone(), r.clone());
            }
            None => {
                return Err(format!(
                    "falta a resposta para a pergunta {}: {}",
                    p.id, p.texto
                ));
            }
        }
    }
    let mut passos = Vec::new();
    for item in role.receitas.iter().filter(|i| i.entra(&completas)) {
        let mut params = Mapping::new();
        for (k, v) in &item.parametros {
            let v = match v {
                Value::String(t) => {
                    let mut falta = None;
                    let novo =
                        cat::REFERENCIA.replace_all(t, |c: &regex::Captures| {
                            match completas.get(&c[1]) {
                                Some(r) => r.clone(),
                                None => {
                                    falta = Some(c[1].to_string());
                                    String::new()
                                }
                            }
                        });
                    if let Some(f) = falta {
                        return Err(format!("falta a resposta para {{{f}}}"));
                    }
                    Value::String(novo.into_owned())
                }
                outro => outro.clone(),
            };
            params.insert(s(k), v);
        }
        passos.push(passo(&item.id, params));
    }
    Ok(cabecalho(Some(&role.id), familia, passos))
}

/// Plano com receitas avulsas, na ordem dada.
pub fn montar_de_receitas(
    ids: &[String],
    familia: &str,
    parametros: &BTreeMap<String, Mapping>,
) -> Value {
    let passos = ids
        .iter()
        .map(|id| passo(id, parametros.get(id).cloned().unwrap_or_default()))
        .collect();
    cabecalho(None, familia, passos)
}

/// Junta parâmetros num passo de um plano já montado.
pub fn acrescentar_parametros(plano: &mut Value, receita: &str, extra: &Mapping) {
    let Some(Value::Sequence(passos)) = plano.get_mut("passos") else {
        return;
    };
    for p in passos {
        if p.get("receita").and_then(texto_de).as_deref() != Some(receita) {
            continue;
        }
        let Value::Mapping(pm) = p else { continue };
        let params = pm
            .entry(s("parametros"))
            .or_insert_with(|| Value::Mapping(Mapping::new()));
        if let Value::Mapping(pp) = params {
            for (k, v) in extra {
                pp.insert(k.clone(), v.clone());
            }
        }
    }
}

pub fn ler(caminho: &Path) -> Result<Value, String> {
    let texto = fs::read_to_string(caminho)
        .map_err(|e| format!("não consegui ler {}: {e}", caminho.display()))?;
    serde_norway::from_str(&texto).map_err(|e| format!("o plano não é um YAML válido: {e}"))
}

pub fn para_texto(plano: &Value) -> String {
    serde_norway::to_string(plano).unwrap_or_default()
}

pub fn salvar(plano: &Value, caminho: &Path) -> std::io::Result<()> {
    let c = caminho.display();
    let texto = format!(
        "# Plano do bora. Revise antes de aplicar.\n# Para conferir: bora validar {c}\n# Para aplicar:  sudo bora aplicar {c}\n{}",
        para_texto(plano)
    );
    fs::write(caminho, texto)
}

/// A receita que baixa um modelo local, com o parâmetro modelo.
pub const RECEITA_COM_MODELO: &str = "ia/ollama";

/// Troca "sugerido" pelo modelo que cabe nesta máquina, para o plano mostrar
/// exatamente o que vai ser baixado antes de a pessoa aceitar.
fn resolver_modelo(
    params: &mut [(String, Valor)],
    catalogo: &Catalogo,
    d: &Diag,
    avisos: &mut Vec<String>,
    erros: &mut Vec<String>,
    n: usize,
) {
    let Some((_, Valor::Texto(valor))) = params.iter_mut().find(|(k, _)| k == "modelo") else {
        return;
    };
    let lista = match crate::modelos::carregar(&catalogo.raiz) {
        Ok(l) => l,
        Err(e) => {
            erros.push(format!("passo {n} ({RECEITA_COM_MODELO}): {e}"));
            return;
        }
    };
    let maq = crate::modelos::Maquina::de(d);
    match valor.as_str() {
        "nenhum" => {}
        "sugerido" => {
            let s = crate::modelos::sugerir(&lista, &maq);
            match s.modelo {
                Some(m) => {
                    avisos.push(format!(
                        "{RECEITA_COM_MODELO}: o modelo que o bora escolheu para esta máquina é {}",
                        s.motivo
                    ));
                    *valor = m.ollama;
                }
                None => {
                    avisos.push(format!(
                        "{RECEITA_COM_MODELO}: o Ollama vai ser instalado sem modelo: {}",
                        s.motivo
                    ));
                    *valor = "nenhum".into();
                }
            }
        }
        nome if !crate::modelos::nome_valido(nome) => erros.push(format!(
            "passo {n} ({RECEITA_COM_MODELO}): {nome} não é um nome de modelo do Ollama; use sugerido, nenhum ou um nome como qwen3:4b"
        )),
        nome => {
            if let Some(m) = lista.modelos.iter().find(|m| m.ollama == nome) {
                let lugar = crate::modelos::avaliar(m, &maq);
                if !lugar.usavel() {
                    avisos.push(format!(
                        "{RECEITA_COM_MODELO}: o modelo {nome} {} nesta máquina; veja bora modelos",
                        match lugar {
                            crate::modelos::Lugar::CpuLento => "fica lento demais",
                            crate::modelos::Lugar::FaltaDisco => "não tem espaço no disco",
                            _ => "não cabe na memória",
                        }
                    ));
                }
            }
        }
    }
}

/// Grava no plano o modelo que o bora escolheu no lugar de "sugerido", para o
/// arquivo salvo dizer exatamente o que vai ser baixado.
pub fn fixar_modelo(plano: &mut Value, v: &PlanoValidado) {
    let Some(modelo) = v
        .passos
        .iter()
        .find(|p| p.receita.id == RECEITA_COM_MODELO)
        .and_then(|p| p.parametros.iter().find(|(k, _)| k == "modelo"))
        .map(|(_, valor)| valor.to_string())
    else {
        return;
    };
    let Some(Value::Sequence(passos)) = plano.get_mut("passos") else {
        return;
    };
    for passo in passos.iter_mut() {
        let Value::Mapping(m) = passo else { continue };
        if m.get("receita").and_then(texto_de).as_deref() != Some(RECEITA_COM_MODELO) {
            continue;
        }
        let params = m
            .entry(s("parametros"))
            .or_insert_with(|| Value::Mapping(Mapping::new()));
        if !matches!(params, Value::Mapping(_)) {
            *params = Value::Mapping(Mapping::new());
        }
        if let Value::Mapping(p) = params {
            p.insert(s("modelo"), s(&modelo));
        }
    }
}

/// Confere o plano contra o catálogo e a máquina. Devolve o plano validado ou a lista de erros.
pub fn validar(plano: &Value, catalogo: &Catalogo, d: &Diag) -> Result<PlanoValidado, Vec<String>> {
    let mut erros = Vec::new();
    let mut avisos = Vec::new();
    let Value::Mapping(m) = plano else {
        return Err(vec!["o plano precisa ser um mapa YAML".into()]);
    };
    for (k, _) in m {
        let k = texto_de(k).unwrap_or_default();
        if !["bora", "criado_em", "objetivo", "familia", "passos"].contains(&k.as_str()) {
            erros.push(format!("campo desconhecido no plano: {k}"));
        }
    }
    if m.get("bora").and_then(Value::as_u64) != Some(FORMATO) {
        erros.push(format!("o plano precisa começar com 'bora: {FORMATO}'"));
    }
    let familia_maquina = d.distro.familia.clone().unwrap_or_default();
    let familia = m
        .get("familia")
        .and_then(texto_de)
        .unwrap_or_else(|| familia_maquina.clone());
    if !familia_maquina.is_empty() && familia != familia_maquina {
        erros.push(format!(
            "o plano foi feito para a família {familia}, e esta máquina é da família {familia_maquina}"
        ));
    }
    let objetivo = m.get("objetivo").and_then(texto_de);
    if let Some(o) = &objetivo
        && catalogo.role(o).is_none()
    {
        erros.push(format!("rolê desconhecido: {o}"));
    }
    let crus = match m.get("passos") {
        Some(Value::Sequence(s)) if !s.is_empty() => s.clone(),
        _ => {
            erros.push("o plano precisa de uma lista de passos".into());
            vec![]
        }
    };

    let mut passos = Vec::new();
    let mut vistos: Vec<String> = Vec::new();
    let (distro, base) = (&d.distro.id, d.distro.base.clone().unwrap_or_default());
    for (i, item) in crus.iter().enumerate() {
        let n = i + 1;
        let Value::Mapping(item) = item else {
            erros.push(format!("passo {n}: precisa do campo receita"));
            continue;
        };
        for (k, _) in item {
            let k = texto_de(k).unwrap_or_default();
            if k != "receita" && k != "parametros" {
                erros.push(format!("passo {n}: campo desconhecido: {k}"));
            }
        }
        let Some(id) = item.get("receita").and_then(texto_de) else {
            erros.push(format!("passo {n}: precisa do campo receita"));
            continue;
        };
        let Some(rec) = catalogo.receita(&id) else {
            erros.push(format!(
                "passo {n}: a receita {id} não existe no catálogo; o bora só aplica receitas do catálogo"
            ));
            continue;
        };
        if vistos.contains(&id) {
            erros.push(format!("passo {n}: a receita {id} aparece mais de uma vez"));
        }
        vistos.push(id.clone());

        match rec.nivel(&familia) {
            "planejada" => erros.push(format!("passo {n}: a receita {id} ainda não foi escrita para a família {familia}")),
            "nao-se-aplica" => erros.push(format!("passo {n}: a receita {id} não se aplica à família {familia}")),
            "comunidade" => avisos.push(format!("{id}: receita da comunidade na família {familia}, sem garantia do projeto")),
            "herdada" => avisos.push(format!(
                "{id}: a família {familia} usa a receita de outra família e ainda não foi testada nela"
            )),
            _ if d.distro.derivada => avisos.push(format!(
                "{id}: {} é derivada; a receita foi testada na distro de origem",
                d.distro.nome
            )),
            _ => match rec.testada_em(distro, &base) {
                None => avisos.push(format!(
                    "{id}: testada na família {familia}, mas ainda não em {}",
                    d.distro.nome
                )),
                Some(t) if t.onde == "conteiner" => avisos.push(format!(
                    "{id}: testada em contêiner, mas ainda não numa máquina virtual com {}",
                    d.distro.nome
                )),
                _ => {}
            },
        }

        let crus_params = match item.get("parametros") {
            None | Some(Value::Null) => Mapping::new(),
            Some(Value::Mapping(p)) => p.clone(),
            Some(_) => {
                erros.push(format!("passo {n}: parametros precisa ser um mapa"));
                Mapping::new()
            }
        };
        for (k, _) in &crus_params {
            let k = texto_de(k).unwrap_or_default();
            if rec.parametro(&k).is_none() {
                erros.push(format!("passo {n}: a receita {id} não tem o parâmetro {k}"));
            }
        }
        let mut params = Vec::new();
        for p in &rec.parametros {
            let valor = crus_params.get(p.nome.as_str()).or(p.padrao.as_ref());
            match p.converter(valor) {
                Ok(v) => params.push((p.nome.clone(), v)),
                Err(e) => erros.push(format!("passo {n} ({id}): {e}")),
            }
        }
        if id == RECEITA_COM_MODELO {
            resolver_modelo(&mut params, catalogo, d, &mut avisos, &mut erros, n);
        }
        if id == "ia/lm-studio"
            && let Ok(l) = crate::modelos::carregar(&catalogo.raiz)
        {
            let s = crate::modelos::sugerir(&l, &crate::modelos::Maquina::de(d));
            avisos.push(match s.modelo {
                Some(m) => format!(
                    "ia/lm-studio: no LM Studio, você baixa o modelo na aba Discover; para esta máquina, procure \"{}\" ({} GB, {})",
                    m.nome,
                    crate::modelos::num(m.tamanho_gb),
                    s.lugar.map(|l| l.descricao()).unwrap_or_default()
                ),
                None => format!("ia/lm-studio: {}", s.motivo),
            });
        }
        passos.push(Passo {
            receita: rec.clone(),
            parametros: params,
        });
    }

    if !erros.is_empty() {
        return Err(erros);
    }
    Ok(PlanoValidado {
        objetivo,
        familia,
        passos,
        avisos,
    })
}

#[cfg(test)]
mod testes {
    use super::*;
    use crate::diag;
    use std::path::PathBuf;

    fn base() -> (Catalogo, Diag) {
        let raiz = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        (
            Catalogo::carregar(&raiz),
            diag::coletar(Some(&raiz.join("testes/os-release/ubuntu-26.04"))),
        )
    }

    fn yaml(t: &str) -> Value {
        serde_norway::from_str(t).unwrap()
    }

    #[test]
    fn modelo_sugerido_vira_o_da_maquina() {
        let (c, mut d) = base();
        d.hardware.ram_gb = Some(32.0);
        d.hardware.vram_gb = None;
        d.hardware.disco_livre_gb = Some(200.0);
        let mut cru = montar_de_receitas(&["ia/ollama".into()], "ubuntu", &BTreeMap::new());
        let v = validar(&cru, &c, &d).unwrap();
        assert_eq!(
            v.passos[0].parametros,
            vec![("modelo".to_string(), Valor::Texto("qwen3-coder:30b".into()))]
        );
        assert!(v.avisos.iter().any(|a| a.contains("Qwen3 Coder 30B")));
        fixar_modelo(&mut cru, &v);
        assert!(para_texto(&cru).contains("modelo: qwen3-coder:30b"));

        // Numa máquina pequena demais, o Ollama entra sem modelo.
        d.hardware.ram_gb = Some(2.0);
        let v = validar(&cru_com_modelo("sugerido"), &c, &d).unwrap();
        assert_eq!(v.passos[0].parametros[0].1, Valor::Texto("nenhum".into()));

        // Um nome que não é de modelo não entra no plano.
        assert!(validar(&cru_com_modelo("qwen3; rm -rf /"), &c, &d).is_err());
        // Um modelo fora da lista entra como está.
        let v = validar(&cru_com_modelo("qwen3:0.6b"), &c, &d).unwrap();
        assert_eq!(
            v.passos[0].parametros[0].1,
            Valor::Texto("qwen3:0.6b".into())
        );
    }

    fn cru_com_modelo(modelo: &str) -> Value {
        let mut m = Mapping::new();
        m.insert(s("modelo"), s(modelo));
        let mut extra = BTreeMap::new();
        extra.insert("ia/ollama".to_string(), m);
        montar_de_receitas(&["ia/ollama".into()], "ubuntu", &extra)
    }

    #[test]
    fn plano_valido() {
        let (c, d) = base();
        let mut extra = BTreeMap::new();
        let mut m = Mapping::new();
        m.insert(s("perfil"), s("servidor-lan"));
        extra.insert("seguranca/firewall".to_string(), m);
        let cru = montar_de_receitas(
            &["base/atualizar".into(), "seguranca/firewall".into()],
            "ubuntu",
            &extra,
        );
        let v = validar(&cru, &c, &d).unwrap();
        assert_eq!(
            v.passos[1].parametros,
            vec![
                ("perfil".to_string(), Valor::Texto("servidor-lan".into())),
                ("rede_local".to_string(), Valor::Texto("auto".into()))
            ]
        );
        // Ida e volta pelo texto.
        let lido: Value = serde_norway::from_str(&para_texto(&cru)).unwrap();
        assert!(validar(&lido, &c, &d).is_ok());
    }

    #[test]
    fn erros() {
        let (c, d) = base();
        let casos = [
            (
                "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: nao/existe\n",
                "não existe no catálogo",
            ),
            (
                "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: seguranca/firewall\n    parametros: {porta: 80}\n",
                "não tem o parâmetro",
            ),
            (
                "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: seguranca/firewall\n    parametros: {rede_local: 8.8.8.0/24}\n",
                "rede local",
            ),
            (
                "bora: 1\nfamilia: fedora\npassos:\n  - receita: base/atualizar\n",
                "família fedora",
            ),
            (
                "bora: 2\nfamilia: ubuntu\npassos:\n  - receita: base/atualizar\n",
                "bora: 1",
            ),
            ("bora: 1\nfamilia: ubuntu\npassos: []\n", "lista de passos"),
            (
                "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: base/atualizar\n  - receita: base/atualizar\n",
                "mais de uma vez",
            ),
            (
                "bora: 1\nfamilia: ubuntu\ncomando: rm -rf /\npassos:\n  - receita: base/atualizar\n",
                "campo desconhecido",
            ),
            (
                "bora: 1\nfamilia: ubuntu\npassos:\n  - receita: base/atualizar\n    script: echo oi\n",
                "campo desconhecido",
            ),
        ];
        for (texto, trecho) in casos {
            let erros = validar(&yaml(texto), &c, &d).unwrap_err();
            assert!(
                erros.iter().any(|e| e.contains(trecho)),
                "{trecho}: {erros:?}"
            );
        }
    }

    #[test]
    fn receita_planejada_na_familia_da_maquina() {
        let raiz = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        let c = Catalogo::carregar(&raiz);
        let d = diag::coletar(Some(&raiz.join("testes/os-release/fedora-43")));
        let erros = validar(
            &yaml("bora: 1\npassos:\n  - receita: seguranca/firewall\n"),
            &c,
            &d,
        )
        .unwrap_err();
        assert!(
            erros
                .iter()
                .any(|e| e.contains("ainda não foi escrita para a família fedora")),
            "{erros:?}"
        );
    }
}
