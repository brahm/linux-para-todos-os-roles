"""Converte texto em caminhos SVG com modelagem HarfBuzz (kerning correto) e contornos do fontTools."""
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

_cache = {}

def _load(font_path):
    if font_path not in _cache:
        data = open(font_path, 'rb').read()
        face = hb.Face(data); font = hb.Font(face)
        font.scale = (face.upem, face.upem)
        tt = TTFont(font_path)
        _cache[font_path] = (face, font, tt, tt.getGlyphSet(), tt.getGlyphOrder())
    return _cache[font_path]

def ntos(v):
    s = f"{v:.2f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def shape(font_path, text, size, x=0.0, y=0.0, tracking=0.0, features=None):
    """Retorna (d, largura, metricas). Origem (x, y) é a linha de base do início do texto.
    tracking em unidades de 'em' (0.01 = 1% do corpo)."""
    face, font, tt, gs, order = _load(font_path)
    upem = face.upem; s = size / upem
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(font, buf, features or {"kern": True, "liga": True})
    pen = SVGPathPen(gs, ntos=ntos)
    cursor = 0.0
    xmin = xmax = None
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        name = order[info.codepoint]
        gx = x + (cursor + pos.x_offset) * s
        gy = y - pos.y_offset * s
        tpen = TransformPen(pen, (s, 0, 0, -s, gx, gy))
        gs[name].draw(tpen)
        bp = BoundsPen(gs); gs[name].draw(bp)
        if bp.bounds:
            bx0, by0, bx1, by1 = bp.bounds
            lo, hi = gx + bx0*s, gx + bx1*s
            xmin = lo if xmin is None else min(xmin, lo)
            xmax = hi if xmax is None else max(xmax, hi)
        cursor += pos.x_advance + tracking * upem
    width = cursor * s
    os2 = tt['OS/2']
    metrics = dict(cap=os2.sCapHeight * s, xh=os2.sxHeight * s, asc=tt['hhea'].ascent * s, desc=tt['hhea'].descent * s,
                   ink_left=xmin, ink_right=xmax)
    return pen.getCommands(), width, metrics

if __name__ == '__main__':
    d, w, m = shape('/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf', 'Linux para todos os rolês', 48)
    print(w, m, len(d))
