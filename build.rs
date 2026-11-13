// Script de compilação do cargo: roda antes de compilar o `bora`.
//
// O `src/fonte.rs` embute as pastas `receitas/` e `objetivos/` no binário com o
// `include_dir!`. Sem as linhas abaixo, o cargo não perceberia que um script ou
// um YAML mudou, e o binário sairia com o catálogo velho.
fn main() {
    println!("cargo:rerun-if-changed=receitas");
    println!("cargo:rerun-if-changed=objetivos");
}
