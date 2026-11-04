"""Exporta PNGs a partir dos SVGs (usa o Chromium do Playwright via render.js)."""
import os, re, subprocess, sys
B = sys.argv[1] if len(sys.argv) > 1 else 'marca'
R = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'render.js')
ID = os.environ.get('APP_ID', 'br.com.brahm.Bora')
os.makedirs(f'{B}/png', exist_ok=True)
def size_of(svg):
    s = open(svg).read()
    w = float(re.search(r'<svg[^>]*\swidth="([\d.]+)"', s).group(1)); h = float(re.search(r'<svg[^>]*\sheight="([\d.]+)"', s).group(1))
    return w, h
def render(svg, out, w, h=None):
    subprocess.run(['node', R, svg, out, str(int(round(w))), str(int(round(h if h else w)))], check=True)
    print('png', out)
icon = f'{B}/icones/hicolor/scalable/apps/{ID}.svg'
for s in (512, 256, 128, 64, 48, 32):
    render(icon, f'{B}/png/icone-{s}.png', s)
symb = f'{B}/icones/hicolor/symbolic/apps/{ID}-symbolic.svg'
for s in (16, 64):
    render(symb, f'{B}/png/icone-simbolico-{s}.png', s)
for name, width in [('logotipo-horizontal', 1600), ('logotipo-horizontal-escuro', 1600), ('logotipo-vertical', 800), ('logotipo-vertical-escuro', 800), ('bora-horizontal', 800), ('bora-horizontal-escuro', 800)]:
    svg = f'{B}/logotipo/{name}.svg'; w, h = size_of(svg)
    render(svg, f'{B}/png/{name}.png', width, width * h / w)
