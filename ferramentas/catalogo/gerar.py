# Gera as páginas do catálogo do site (docs/catalogo/) a partir de dados.py e dos receita.yaml.
# Uso, na raiz do repositório: python3 ferramentas/catalogo/gerar.py
# Precisa do PyYAML (pacote python3-yaml).
import os
from comum import pagina, DOCS
from dados import ROLES, PRONTAS, RECEITAS
from receitas import PAGINAS
from roles import pagina_role, pagina_catalogo

saida = DOCS + "catalogo/"
os.makedirs(saida + "receitas", exist_ok=True)
os.makedirs(saida + "roles", exist_ok=True)

def escrever(rel, html):
    open(saida + rel, "w", encoding="utf-8").write(html)
    print("escrito", rel)

escrever("index.html", pagina(raiz="../", caminho="catalogo/", titulo="Rolês e receitas",
    descricao="Os rolês da primeira versão e as receitas do bora, cada um com o passo a passo, o que faz, o que não faz e os porquês.",
    corpo=pagina_catalogo(), ativo="inicio"))
for rid in PRONTAS:
    nome = RECEITAS[rid][0]
    rel = "receitas/" + rid.replace("/", "-") + ".html"
    escrever(rel, pagina(raiz="../../", caminho="catalogo/" + rel, titulo=nome,
        descricao=f"{nome}, receita do bora: {RECEITAS[rid][3]} O passo a passo, o que faz, o que não faz e os porquês.",
        corpo=PAGINAS[rid]()))
for r in ROLES:
    rel = f"roles/{r['id']}.html"
    escrever(rel, pagina(raiz="../../", caminho="catalogo/" + rel, titulo=r["nome"],
        descricao=f"{r['nome']}, rolê do Linux para todos os rolês: {r['resumo']}",
        corpo=pagina_role(r)))
