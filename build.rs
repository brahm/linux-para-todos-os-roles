// Recompila quando o catálogo embutido muda.
fn main() {
    println!("cargo:rerun-if-changed=receitas");
    println!("cargo:rerun-if-changed=objetivos");
}
