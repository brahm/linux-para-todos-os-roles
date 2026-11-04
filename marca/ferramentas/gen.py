#!/usr/bin/env python3
"""Gera os SVGs da marca (ícone colorido, ícone simbólico e logotipos).

Uso: python3 gen.py [pasta-de-saida]
Depende de: fontTools, uharfbuzz e da fonte Inter (arquivos .otf).
"""
import math, os, sys
from pegada import footprint, transform, to_path, bbox
from texto import shape

OUT = sys.argv[1] if len(sys.argv) > 1 else 'marca'
FONTS = os.environ.get('INTER_DIR', '/usr/share/fonts/opentype/inter')
F_BOLD = os.path.join(FONTS, 'InterDisplay-Bold.otf')
F_SEMI = os.path.join(FONTS, 'InterDisplay-SemiBold.otf')
APP_ID = os.environ.get('APP_ID', 'br.com.brahm.Bora')

# Paleta GNOME (https://developer.gnome.org/hig/reference/palette.html)
ORANGE2, ORANGE3, ORANGE4, ORANGE5 = '#ffa348', '#ff7800', '#e66100', '#c64600'
LIGHT1, LIGHT2, DARK3, DARK4, SYMB = '#ffffff', '#f6f5f4', '#3d3846', '#241f31', '#2e3436'

HEAD = '<?xml version="1.0" encoding="UTF-8"?>\n'

def write(name, content):
    path = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w').write(content)
    print('escrito', path)

def f(v):
    s = f"{v:.2f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

# ---------- Trilha de pegadas ----------
def bezier_pt(p0, p1, p2, t):
    return ((1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t*t*p2[0],
            (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t*t*p2[1])

def bezier_tan(p0, p1, p2, t):
    dx = 2*(1-t)*(p1[0]-p0[0]) + 2*t*(p2[0]-p1[0])
    dy = 2*(1-t)*(p1[1]-p0[1]) + 2*t*(p2[1]-p1[1])
    d = math.hypot(dx, dy); return (dx/d, dy/d)

def trail():
    """Duas pegadas (pé esquerdo e pé direito) em diagonal, centralizadas no tile de 104 px."""
    prims = transform(footprint(), 1.0, 30, (44, 82)) + transform(footprint(), 1.0, 40, (84, 46))
    x0, y0, x1, y1 = bbox(prims)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return transform(prims, 1.0, 0, (64 - cx, 64 - cy))

def mark_prims():
    """Marca do logotipo: uma pegada só, levemente inclinada."""
    return transform(footprint(), 1.0, 20, (0, 0))

def fit(prims, x, y, h):
    """Redimensiona as primitivas para altura h, com o canto superior esquerdo em (x, y). Retorna (prims, largura)."""
    x0, y0, x1, y1 = bbox(prims)
    s = h / (y1 - y0)
    out = transform(prims, s, 0, (x - x0*s, y - y0*s))
    return out, (x1 - x0) * s

# ---------- Ícone do aplicativo ----------
def svg_icon(face=ORANGE3, side=ORANGE5, ink=LIGHT1):
    d = to_path(trail())
    return f'''{HEAD}<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">
  <title>Bora</title>
  <rect x="12" y="16" width="104" height="104" rx="18" fill="{side}"/>
  <rect x="12" y="12" width="104" height="104" rx="18" fill="{face}"/>
  <path d="{d}" fill="{ink}"/>
</svg>
'''

def svg_symbolic(fill=SYMB):
    fp = footprint()
    x0, y0, x1, y1 = bbox(fp)
    s = 14.0 / (y1 - y0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    d = to_path(transform(fp, s, 0, (8 - cx*s, 8 - cy*s)))
    return f'''{HEAD}<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16">
  <path d="{d}" fill="{fill}"/>
</svg>
'''

# ---------- Logotipos ----------
def wordmark_runs(runs, size, x, y, font=F_BOLD, tracking=-0.01):
    """runs: lista de (texto, cor). Retorna (elementos svg, largura total, métricas)."""
    els = []; cur = x; m = None
    for i, (text, color) in enumerate(runs):
        d, w, m = shape(font, text, size, cur, y, tracking=tracking)
        els.append(f'<path fill="{color}" d="{d}"/>')
        cur += w
    return els, cur - x, m

def svg_logo_horizontal(ink=DARK4, accent=ORANGE4, mark=ORANGE3, pad=12, mono=False):
    size = 48
    els_text, tw, m = wordmark_runs([('Linux para todos os ', ink), ('rolês', accent)], size, 0, 0)
    # caixa do texto: do topo do acento (asc) até o descendente
    top = -m['cap'] * 1.22            # acento do ê fica acima da altura das maiúsculas
    bottom = -m['desc'] * 0.45        # a palavra não tem descendentes profundos; usa parte do descendente
    text_h = bottom - top
    mark_h = text_h * 1.28
    prims, mw = fit(mark_prims(), 0, 0, mark_h)
    gap = 16
    # posiciona o texto à direita da marca; alinha o centro vertical do texto ao da marca
    tx = mw + gap
    ty = mark_h/2 - (top + bottom)/2
    els_text, tw, m = wordmark_runs([('Linux para todos os ', ink), ('rolês', accent)], size, tx, ty)
    W = tx + tw + 0; H = mark_h
    d = to_path(prims)
    if mono:
        els_text = [e.replace(f'fill="{ink}"', 'fill="currentColor"').replace(f'fill="{accent}"', 'fill="currentColor"') for e in els_text]
        mark = 'currentColor'
    vb = f'{f(-pad)} {f(-pad)} {f(W + 2*pad)} {f(H + 2*pad)}'
    return f'''{HEAD}<svg xmlns="http://www.w3.org/2000/svg" width="{f(W + 2*pad)}" height="{f(H + 2*pad)}" viewBox="{vb}">
  <title>Linux para todos os rolês</title>
  <path fill="{mark}" d="{d}"/>
  {chr(10).join('  ' + e for e in els_text)}
</svg>
'''

def svg_logo_vertical(ink=DARK4, accent=ORANGE4, mark=ORANGE3, pad=16, mono=False):
    size = 44
    line_gap = size * 1.12
    l1, w1, m = wordmark_runs([('Linux para', ink)], size, 0, 0)
    l2, w2, _ = wordmark_runs([('todos os ', ink), ('rolês', accent)], size, 0, 0)
    W = max(w1, w2)
    mark_h = 92
    prims, mw = fit(mark_prims(), 0, 0, mark_h)
    # centraliza a marca
    prims = transform(prims, 1, 0, ((W - mw)/2, 0))
    y1 = mark_h + 20 + m['cap']
    y2 = y1 + line_gap
    l1, _, _ = wordmark_runs([('Linux para', ink)], size, (W - w1)/2, y1)
    l2, _, _ = wordmark_runs([('todos os ', ink), ('rolês', accent)], size, (W - w2)/2, y2)
    H = y2 - m['desc'] * 0.45
    els = l1 + l2
    if mono:
        els = [e.replace(f'fill="{ink}"', 'fill="currentColor"').replace(f'fill="{accent}"', 'fill="currentColor"') for e in els]
        mark = 'currentColor'
    d = to_path(prims)
    vb = f'{f(-pad)} {f(-pad)} {f(W + 2*pad)} {f(H + 2*pad)}'
    return f'''{HEAD}<svg xmlns="http://www.w3.org/2000/svg" width="{f(W + 2*pad)}" height="{f(H + 2*pad)}" viewBox="{vb}">
  <title>Linux para todos os rolês</title>
  <path fill="{mark}" d="{d}"/>
  {chr(10).join('  ' + e for e in els)}
</svg>
'''

def svg_logo_bora(ink=DARK4, pad=12, mono=False, face=ORANGE3, side=ORANGE5):
    size = 56
    els, tw, m = wordmark_runs([('bora', ink)], size, 0, 0, tracking=-0.015)
    icon_h = size * 1.15
    s = icon_h / 108           # o tile ocupa de y=12 a y=120 (108 px) no ícone
    gap = 14
    # ícone: tile + trilha
    prims = transform(trail(), s, 0, (-12*s, -12*s))
    d = to_path(prims)
    tx = 104*s + gap
    ty = icon_h/2 + m['xh']/2     # alinha o centro do x-height ao centro do ícone
    els, tw, m = wordmark_runs([('bora', ink)], size, tx, ty, tracking=-0.015)
    W = tx + tw; H = icon_h
    if mono:
        els = [e.replace(f'fill="{ink}"', 'fill="currentColor"') for e in els]
    vb = f'{f(-pad)} {f(-pad)} {f(W + 2*pad)} {f(H + 2*pad)}'
    return f'''{HEAD}<svg xmlns="http://www.w3.org/2000/svg" width="{f(W + 2*pad)}" height="{f(H + 2*pad)}" viewBox="{vb}">
  <title>bora</title>
  <rect x="0" y="{f(4*s)}" width="{f(104*s)}" height="{f(104*s)}" rx="{f(18*s)}" fill="{side}"/>
  <rect x="0" y="0" width="{f(104*s)}" height="{f(104*s)}" rx="{f(18*s)}" fill="{face}"/>
  <path fill="{LIGHT1}" d="{d}"/>
  {chr(10).join('  ' + e for e in els)}
</svg>
'''

if __name__ == '__main__':
    write(f'icones/hicolor/scalable/apps/{APP_ID}.svg', svg_icon())
    write(f'icones/hicolor/symbolic/apps/{APP_ID}-symbolic.svg', svg_symbolic())
    write('logotipo/logotipo-horizontal.svg', svg_logo_horizontal())
    write('logotipo/logotipo-horizontal-escuro.svg', svg_logo_horizontal(ink=LIGHT1, accent=ORANGE2, mark=ORANGE3))
    write('logotipo/logotipo-horizontal-mono.svg', svg_logo_horizontal(mono=True))
    write('logotipo/logotipo-vertical.svg', svg_logo_vertical())
    write('logotipo/logotipo-vertical-escuro.svg', svg_logo_vertical(ink=LIGHT1, accent=ORANGE2, mark=ORANGE3))
    write('logotipo/logotipo-vertical-mono.svg', svg_logo_vertical(mono=True))
    write('logotipo/bora-horizontal.svg', svg_logo_bora())
    write('logotipo/bora-horizontal-escuro.svg', svg_logo_bora(ink=LIGHT1))
    print('trilha do ícone:', [round(v, 1) for v in bbox(trail())])
