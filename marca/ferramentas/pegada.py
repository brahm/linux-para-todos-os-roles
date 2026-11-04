#!/usr/bin/env python3
"""Geometria da pegada de pinguim (três dedos com membrana) como um único caminho SVG.

Tudo é gerado por código para que o mesmo desenho sirva ao ícone colorido,
ao ícone simbólico e ao logotipo, em qualquer escala e rotação.
"""
import math

def rot(v, ang):
    c, s = math.cos(ang), math.sin(ang)
    return (v[0]*c - v[1]*s, v[0]*s + v[1]*c)

def add(a, b): return (a[0]+b[0], a[1]+b[1])
def mul(a, k): return (a[0]*k, a[1]*k)
def sub(a, b): return (a[0]-b[0], a[1]-b[1])
def norm(a):
    d = math.hypot(*a); return (a[0]/d, a[1]/d)

# Segmentos: ('L', p) linha até p; ('A', r, sweep, p) arco de raio r até p; ('C', c1, c2, p) cúbica.
# Cada primitiva é uma lista [p0, seg, seg, ...] fechada.

def hull_two_circles(a, ra, b, rb):
    """Contorno (cápsula afunilada) que envolve dois círculos."""
    d = math.dist(a, b)
    u = norm(sub(b, a))
    alpha = math.acos(max(-1.0, min(1.0, (ra - rb) / d)))
    p1 = add(a, mul(rot(u, alpha), ra))
    q1 = add(b, mul(rot(u, alpha), rb))
    q2 = add(b, mul(rot(u, -alpha), rb))
    p2 = add(a, mul(rot(u, -alpha), ra))
    # Percurso com ângulo decrescente (sweep=0): p1 -> q1, volta de B pelo lado oposto a A,
    # q2 -> p2, volta de A pelo lado oposto a B.
    large_b = 1 if 2*alpha > math.pi else 0
    large_a = 1 if (2*math.pi - 2*alpha) > math.pi else 0
    return [p1, ('L', q1), ('A', rb, large_b, 0, q2), ('L', p2), ('A', ra, large_a, 0, p1)]

def circle(c, r):
    p0 = add(c, (r, 0)); p1 = add(c, (-r, 0))
    return [p0, ('A', r, 0, 0, p1), ('A', r, 0, 0, p0)]

def web(c, t1, t2, dip):
    """Membrana entre dois dedos: polígono do centro c até os pontos t1 e t2, com borda externa côncava."""
    mid = mul(add(t1, t2), 0.5)
    ctrl = add(mid, mul(norm(sub(c, mid)), dip))
    # cúbica aproximando uma quadrática com controle ctrl
    c1 = add(t1, mul(sub(ctrl, t1), 2/3)); c2 = add(t2, mul(sub(ctrl, t2), 2/3))
    return [c, ('L', t1), ('C', c1, c2, t2), ('L', c)]

def sample(prim, n=24):
    """Pontos aproximados do contorno (para orientação)."""
    pts = [prim[0]]; cur = prim[0]
    for seg in prim[1:]:
        if seg[0] == 'L':
            pts.append(seg[1]); cur = seg[1]
        elif seg[0] == 'C':
            _, c1, c2, p = seg
            for i in range(1, n+1):
                t = i/n
                x = (1-t)**3*cur[0] + 3*(1-t)**2*t*c1[0] + 3*(1-t)*t*t*c2[0] + t**3*p[0]
                y = (1-t)**3*cur[1] + 3*(1-t)**2*t*c1[1] + 3*(1-t)*t*t*c2[1] + t**3*p[1]
                pts.append((x, y))
            cur = p
        elif seg[0] == 'A':
            _, r, large, sweep, p = seg
            # centro do arco
            mx, my = (cur[0]+p[0])/2, (cur[1]+p[1])/2
            dx, dy = (p[0]-cur[0])/2, (p[1]-cur[1])/2
            h2 = r*r - dx*dx - dy*dy
            h = math.sqrt(max(0.0, h2))
            L = math.hypot(dx, dy) or 1e-9
            sgn = 1 if (large != sweep) else -1
            cx, cy = mx - sgn*h*dy/L, my + sgn*h*dx/L
            # ângulos
            a0 = math.atan2(cur[1]-cy, cur[0]-cx); a1 = math.atan2(p[1]-cy, p[0]-cx)
            da = a1 - a0
            if sweep == 1 and da < 0: da += 2*math.pi
            if sweep == 0 and da > 0: da -= 2*math.pi
            for i in range(1, n+1):
                t = a0 + da*i/n
                pts.append((cx + r*math.cos(t), cy + r*math.sin(t)))
            cur = p
    return pts

def signed_area(pts):
    s = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]; x1, y1 = pts[(i+1) % len(pts)]
        s += x0*y1 - x1*y0
    return s/2

def reverse(prim):
    """Inverte o sentido de uma primitiva."""
    pts = [prim[0]] + [seg[-1] for seg in prim[1:]]
    segs = prim[1:]
    out = [pts[-1]]
    for i in range(len(segs)-1, -1, -1):
        seg = segs[i]; start = pts[i]
        if seg[0] == 'L': out.append(('L', start))
        elif seg[0] == 'C': out.append(('C', seg[2], seg[1], start))
        elif seg[0] == 'A': out.append(('A', seg[1], seg[2], 1-seg[3], start))
    return out

def orient(prim, positive=True):
    a = signed_area(sample(prim))
    if (a > 0) != positive:
        return reverse(prim)
    return prim

def footprint(params=None):
    """Primitivas da pegada apontando para cima, em espaço unitário (y para baixo)."""
    P = dict(
        palm=(0.0, 1.5), palm_r=9.5,
        toe_angles=(-47, 0, 47), toe_len=(17.0, 19.0, 17.0), toe_base_r=6.2, toe_tip_r=(4.6, 5.0, 4.6),
        heel=(0.0, 12.0), heel_r=5.5,
        web_frac=0.82, web_dip=3.5,
    )
    if params: P.update(params)
    c = P['palm']
    prims = []
    tips = []
    dirs = []
    for ang, L, rt in zip(P['toe_angles'], P['toe_len'], P['toe_tip_r']):
        d = rot((0, -1), math.radians(ang))
        tip = add(c, mul(d, L))
        tips.append(tip); dirs.append(d)
        prims.append(hull_two_circles(c, P['toe_base_r'], tip, rt))
    prims.append(hull_two_circles(c, P['palm_r'], P['heel'], P['heel_r']))
    # membranas
    for i in range(len(tips)-1):
        f = P['web_frac']
        t1 = add(c, mul(dirs[i], P['toe_len'][i]*f))
        t2 = add(c, mul(dirs[i+1], P['toe_len'][i+1]*f))
        prims.append(web(c, t1, t2, P['web_dip']))
    return [orient(p) for p in prims]

def transform(prims, scale=1.0, angle_deg=0.0, translate=(0, 0)):
    ang = math.radians(angle_deg)
    def T(p):
        q = rot(mul(p, scale), ang)
        return (q[0]+translate[0], q[1]+translate[1])
    out = []
    for prim in prims:
        np_ = [T(prim[0])]
        for seg in prim[1:]:
            if seg[0] == 'L': np_.append(('L', T(seg[1])))
            elif seg[0] == 'C': np_.append(('C', T(seg[1]), T(seg[2]), T(seg[3])))
            elif seg[0] == 'A': np_.append(('A', seg[1]*scale, seg[2], seg[3], T(seg[4])))
        out.append(np_)
    return out

def fmt(v, nd=2):
    s = f"{v:.{nd}f}".rstrip('0').rstrip('.')
    return '0' if s in ('-0', '') else s

def to_path(prims, nd=2):
    parts = []
    for prim in prims:
        x, y = prim[0]
        s = f"M{fmt(x,nd)} {fmt(y,nd)}"
        for seg in prim[1:]:
            if seg[0] == 'L':
                s += f"L{fmt(seg[1][0],nd)} {fmt(seg[1][1],nd)}"
            elif seg[0] == 'C':
                s += "C" + " ".join(f"{fmt(p[0],nd)} {fmt(p[1],nd)}" for p in seg[1:])
            elif seg[0] == 'A':
                _, r, large, sweep, p = seg
                s += f"A{fmt(r,nd)} {fmt(r,nd)} 0 {large} {sweep} {fmt(p[0],nd)} {fmt(p[1],nd)}"
        s += "Z"
        parts.append(s)
    return "".join(parts)

def footprint_path(scale=1.0, angle_deg=0.0, translate=(0, 0), params=None, nd=2):
    return to_path(transform(footprint(params), scale, angle_deg, translate), nd)

def bbox(prims):
    pts = [p for prim in prims for p in sample(prim, 32)]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)

if __name__ == '__main__':
    fp = footprint()
    print(bbox(fp))
    d = footprint_path(1.0, 0, (64, 64))
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128"><rect width="128" height="128" fill="#ff7800"/><path d="{d}" fill="#fff"/></svg>'
    open('build_test_pegada.svg', 'w').write(svg)
    print(len(d))
