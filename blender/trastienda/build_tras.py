# Kit de trastienda v78 · Blender → glTF (skill blender-arte-bodega). Reemplaza en el simulador racks, bandejas y líneas de pallets de la trastienda
# (antes cajas del código). Lee el mismo plano que el simulador (tras_map.json = TRAS_MAP_DEF). Coordenadas: X=x, Y=−z, Z=y.
# Medidas: montante 80×70 mm perforado, viga caja 100×50 mm, pallet 1,2×1,0 m (tablas 100×22, tacos 100×100×78). Alturas de rack como el simulador (3,0 m; niveles 1,25/2,4) [SUPUESTO por fotos].
import bpy, bmesh, json, os, math, random, re
from mathutils import Vector
D = os.path.dirname(os.path.abspath(__file__)); TX = os.path.join(D, 'tex'); OUT = os.path.join(D, 'tras_v78.glb')
rnd = random.Random(78)
for o in list(bpy.data.objects): bpy.data.objects.remove(o, do_unlink=True)
for m in list(bpy.data.meshes): bpy.data.meshes.remove(m)
for m in list(bpy.data.materials): bpy.data.materials.remove(m)
MAP = json.load(open(os.path.join(D, 'tras_map.json'), encoding='utf-8'))
# v80 (bug «rackinsertoenpilar»): pilares de trastienda (plano_final2, x, z, ancho, largo); racks y líneas de pallets se recortan para no entrar en ellos
PILARES = [[-47.8, 18.25, 0.6, 0.6], [-47.8, 26.07, 0.6, 0.6], [-47.8, 33.75, 0.6, 0.6], [-47.8, 41.33, 0.6, 0.6], [-47.8, 48.95, 0.6, 0.6], [-47.8, 56.95, 0.6, 0.6], [-31, 26.07, 0.6, 0.6], [-31, 41.33, 0.6, 0.6], [-31, 56.95, 0.6, 0.6], [-13.55, 41.33, 0.6, 0.6], [-58.65, 18.25, 0.6, 0.6], [-58.65, 26.07, 0.6, 0.6], [-58.65, 48.95, 0.6, 0.6], [-58.65, 41.33, 0.6, 0.6], [-58.65, 60.94, 0.6, 0.6], [-47.8, 2.35, 0.6, 0.6], [-13.55, 10.47, 0.6, 0.6], [-47.8, 10.47, 0.6, 0.6], [-58.65, 10.47, 0.6, 0.6], [-13.55, 26.07, 0.6, 0.6], [-13.55, 56.95, 0.6, 0.6], [-31, 10.47, 0.6, 0.6], [-13.55, 73.35, 0.6, 0.6], [-31, 73.35, 0.6, 0.6], [-47.8, 73.35, 0.6, 0.6], [-13.55, 2.35, 0.84, 0.7], [-31, 2.35, 0.84, 0.7], [-58.65, 2.35, 0.85, 0.7], [-58.65, 33.75, 0.6, 0.6], [-58.65, 65, 0.6, 0.6], [-58.66, 79.4, 0.43, 0.4], [-74.1, 79.4, 0.6, 0.6], [-58.65, 56.95, 0.6, 0.6], [-74.4, 82.6, 0.4, 0.4], [-58.5, 82.6, 0.4, 0.4]]
def despeja(o, h=.06):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z'])
    for (px, pz, w, l) in PILARES:
        a0, a1, b0, b1 = px - w / 2 - h, px + w / 2 + h, pz - l / 2 - h, pz + l / 2 + h
        if a1 <= x0 or a0 >= x1 or b1 <= z0 or b0 >= z1: continue
        cand = [(min(x1 - a1, x1 - x0), 'x0'), (a0 - x0, 'x1')] if (x1 - x0) > (z1 - z0) else [(z1 - b1, 'z0'), (b0 - z0, 'z1')]
        _, lado = max(cand)
        if lado == 'x0': x0 = a1
        elif lado == 'x1': x1 = a0
        elif lado == 'z0': z0 = b1
        else: z1 = b0
    o['x'], o['z'] = [x0, x1], [z0, z1]
for o in MAP:
    if o['tipo'] in ('rack', 'pallets', 'cajas'): despeja(o)
def img(n):
    for ext in ('.webp', '.png'):
        p = os.path.join(TX, n + ext)
        if os.path.exists(p): return bpy.data.images.load(p, check_existing=True)
    return None
def mk(name, color=(1, 1, 1), rough=.5, metal=0., diff=None, nrm=None, nstr=1., alpha=None, atex=False):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if diff:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img(diff)
        mul = nt.nodes.new('ShaderNodeMixRGB'); mul.blend_type = 'MULTIPLY'; mul.inputs[0].default_value = 1; mul.inputs[1].default_value = (*color, 1)
        nt.links.new(t.outputs['Color'], mul.inputs[2]); nt.links.new(mul.outputs[0], b.inputs['Base Color'])
        if atex:   # alfa desde la textura (rejilla, sombras)
            nt.links.new(t.outputs['Alpha'], b.inputs['Alpha'])
            try: m.surface_render_method = 'BLENDED'
            except Exception: m.blend_method = 'BLEND'
    if nrm:
        t = nt.nodes.new('ShaderNodeTexImage'); t.image = img(nrm); t.image.colorspace_settings.name = 'Non-Color'
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = nstr; nt.links.new(t.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    if alpha is not None:
        b.inputs['Alpha'].default_value = alpha
        try: m.surface_render_method = 'BLENDED'
        except Exception: m.blend_method = 'BLEND'
    return m
M = dict(
  mont_w=mk('tras_montante_blanco', (.93, .93, .91), .45, .0, 'montante_diff', 'montante_norm', .6),
  mont_c=mk('tras_montante_crema', (.90, .87, .79), .45, .0, 'montante_diff', 'montante_norm', .6),
  mont_b=mk('tras_montante_azul', (.10, .20, .52), .42, .0, 'montante_diff', 'montante_norm', .6),
  br_w=mk('tras_celosia_blanca', (.93, .93, .91), .45), br_c=mk('tras_celosia_crema', (.90, .87, .79), .45), br_b=mk('tras_celosia_azul', (.10, .20, .52), .42),
  viga=mk('tras_viga_naranja', (.86, .32, .06), .42), viga_w=mk('tras_viga_crema', (.78, .70, .55), .45),
  galv=mk('tras_galvanizado', (.62, .63, .62), .38, 1.), deck=mk('tras_cubierta_aglomerado', (.78, .70, .58), .8),
  carton=mk('tras_carton', (.84, .79, .72), .85, 0, 'carton_atlas_diff', 'carton_atlas_norm', .5),
  pino=mk('tras_pallet_pino', (1, 1, 1), .82, 0, 'pino_diff', 'pino_norm', .7),
  pl_azul=mk('tras_pallet_plastico_azul', (.12, .30, .66), .5, 0, 'plastico_diff', 'plastico_norm', .5),
  pl_rojo=mk('tras_pallet_plastico_rojo', (.62, .10, .11), .5, 0, 'plastico_diff', 'plastico_norm', .5),
  film=mk('tras_film', (.95, .96, .97), .08, 0, None, 'film_norm', .45, alpha=.36),
  bandeja=mk('tras_bandeja_rosa', (1, 1, 1), .5, 0, 'bandeja_diff'), carro=mk('tras_carro_gris', (.24, .25, .27), .45, .5),
  rueda=mk('tras_rueda', (.05, .05, .05), .7), cinta=mk('tras_ancla', (.35, .36, .36), .5, 1.))
ROSA = [(.94, .55, .72), (.96, .70, .80), (.92, .50, .68), (.97, .79, .86)]
class MB:   # acumulador de mallas por material
    def __init__(s): s.v = []; s.f = []; s.uv = []; s.col = []
    def box(s, c, sz, rotz=0., uvt=None, col=None):   # c, sz en coords del plano (x,y,z); uvt=(u0,v0,u1,v1) baldosa del atlas
        x, y, z = c; a, b_, d = sz[0] / 2, sz[1] / 2, sz[2] / 2; ca, sa = math.cos(rotz), math.sin(rotz)
        P = [(-a, -b_, -d), (a, -b_, -d), (a, b_, -d), (-a, b_, -d), (-a, -b_, d), (a, -b_, d), (a, b_, d), (-a, b_, d)]
        V = [(x + px * ca - pz * sa, -(z + px * sa + pz * ca), y + py) for px, py, pz in P]
        k = len(s.v); s.v += V; F = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
        u0, v0, u1, v1 = uvt or (0, 0, 1, 1)
        for fi, f in enumerate(F):
            s.f.append(tuple(k + i for i in f))
            if uvt: s.uv.append([(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
            else:   # UV en metros (1 rep/m) según la cara
                pts = [P[i] for i in f]; ax = [0, 0, 2, 0, 2, 0][fi] if fi > 1 else 0
                if fi < 2: uvs = [(p[0] + a, p[2] + d) for p in pts]
                elif fi in (2, 4): uvs = [(p[0] + a, p[1] + b_) for p in pts]
                else: uvs = [(p[2] + d, p[1] + b_) for p in pts]
                s.uv.append(uvs)
            s.col.append(col)
    def quad(s, pts, uvs, col=None):   # pts en coords del plano (x,y,z)
        k = len(s.v); s.v += [(x, -z, y) for x, y, z in pts]; s.f.append(tuple(range(k, k + len(pts)))); s.uv.append(uvs); s.col.append(col)
    def obj(s, name, mat, bevel=0., wn=True, grupo=None):
        if not s.f: return None
        me = bpy.data.meshes.new(name); me.from_pydata(s.v, [], s.f); me.update()
        ul = me.uv_layers.new(name='UVMap'); i = 0
        for p in me.polygons:
            for j, li in enumerate(p.loop_indices): ul.data[li].uv = s.uv[p.index][j]
        if any(c is not None for c in s.col):
            ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
            for p in me.polygons:
                c = s.col[p.index] or (1, 1, 1)
                for li in p.loop_indices: ca.data[li].color = (*c, 1)
        o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); me.materials.append(mat)
        for p in me.polygons: p.use_smooth = True
        if bevel:
            md = o.modifiers.new('Bevel', 'BEVEL'); md.width = bevel; md.segments = 1 if name in ('tras_carton', 'tras_pino', 'tras_bandeja', 'tras_jaba_n', 'tras_jaba_g', 'tras_baranda', 'tras_canal', 'tras_zocalo', 'tras_remate', 'tras_galv', 'tras_pl_azul', 'tras_pl_rojo') else 2; md.limit_method = 'ANGLE'; md.angle_limit = math.radians(30); md.harden_normals = True
        if wn:
            md = o.modifiers.new('WN', 'WEIGHTED_NORMAL'); md.keep_sharp = True
        return o
G = {k: MB() for k in ['mont_w', 'mont_c', 'mont_b', 'br_w', 'br_c', 'br_b', 'viga', 'viga_w', 'galv', 'deck', 'carton', 'pino', 'pl_azul', 'pl_rojo', 'film', 'bandeja', 'carro', 'rueda']}
TILE = [(0, .5, .5, 1), (.5, .5, 1, 1), (0, 0, .5, .5), (.5, 0, 1, .5)]   # 0 kraft cinta, 1 etiqueta, 2 blanca impresa, 3 kraft gastada
def caja(c, sz, rot=0., t=None):
    t = rnd.choices([0, 1, 2, 3], [5, 4, 1.2, 2])[0] if t is None else t
    k = .85 + rnd.random() * .3; G['carton'].box(c, sz, rot, TILE[t], (k, k * (.97 + rnd.random() * .06), k * (.94 + rnd.random() * .08)))
def P(ax, u, y, v, su, sy, sv):   # pieza en ejes del rack (u = largo, v = fondo)
    return ((u, y, v), (su, sy, sv)) if ax else ((v, y, u), (sv, sy, su))
def montante(g, ax, u, v, H, sgn):   # perfil omega 80×70: frente + dos alas (3 cajas) + placa base y anclajes
    for (du, dv, su, sv) in [(0, .033 * sgn, .08, .004), (-.038, 0, .004, .07), (.038, 0, .004, .07)]:
        c, s = P(ax, u + du, H / 2, v + dv, su, H, sv); G[g].box(c, s)
    c, s = P(ax, u, .004, v, .14, .008, .12); G['galv'].box(c, s)
    for k in (-1, 1): c, s = P(ax, u + k * .045, .02, v, .016, .03, .016); G['galv'].box(c, s)
def rack(o, tipo):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); ax = (x1 - x0) > (z1 - z0)
    Lr = (x1 - x0) if ax else (z1 - z0); d = (z1 - z0) if ax else (x1 - x0); mv = (z0 + z1) / 2 if ax else (x0 + x1) / 2; u0 = x0 if ax else z0
    H = 3.0; lv = [1.25, 2.4]; n = max(1, round(Lr / 2.6)); b = Lr / n
    gm = {'w': 'mont_w', 'b': 'mont_b', 'n': 'mont_c'}[tipo]; gb = 'br_' + tipo.replace('n', 'c'); gv = 'viga'   # v80 (bug «racksincolor»): las vigas son naranjas en todos los racks (fotos)
    for i in range(n + 1):
        u = u0 + i * b
        for s in (-1, 1): montante(gm, ax, u, mv + s * (d / 2 - .04), H, -s)
        y = .35   # celosía del bastidor: horizontales y diagonales (tubo 30×30)
        while y < H - .3:
            c, sz = P(ax, u, y, mv, .03, .03, d - .12); G[gb].box(c, sz)
            if y + .6 < H:
                L = math.hypot(.6, d - .12); ang = math.atan2(.6, d - .12) * (1 if round((y - .35) / .6) % 2 == 0 else -1)   # v80: zig-zag
                cx, cy, cz = (u, y + .3, mv) if ax else (mv, y + .3, u)
                # diagonal como caja rotada en el plano vertical del bastidor
                me_c = (cx, cy, cz); G[gb].box(me_c, (.025, .025, L) if ax else (L, .025, .025), 0)
                vv = G[gb].v; k = len(vv) - 8
                for j in range(k, k + 8):   # rotar alrededor del centro en el plano (v,y)
                    X, Y, Z = vv[j]; py = Z - cy
                    if ax: pv = -Y - cz; nv = pv * math.cos(ang) - py * math.sin(ang); ny = pv * math.sin(ang) + py * math.cos(ang); vv[j] = (X, -(cz + nv), cy + ny)
                    else: pv = X - cx; nv = pv * math.cos(ang) - py * math.sin(ang); ny = pv * math.sin(ang) + py * math.cos(ang); vv[j] = (cx + nv, Y, cy + ny)
            y += .6
    for i in range(n):
        c0 = u0 + (i + .5) * b
        for y in lv:
            for s in (-1, 1):
                c, sz = P(ax, c0, y, mv + s * (d / 2 - .04), b - .09, .10, .05); G[gv].box(c, sz)
                for k in (-1, 1): c, sz = P(ax, c0 + k * (b / 2 - .06), y, mv + s * (d / 2 - .04), .025, .14, .055); G['galv'].box(c, sz)   # conector
            c, sz = P(ax, c0, y + .059, mv, b - .1, .018, d - .1); G['deck'].box(c, sz)
        for y0 in [0.] + lv:   # carga
            top = next((v for v in lv if v > y0 + .01), H) - y0 - .15; uu = c0 - b / 2 + .08
            if y0 == 0 and rnd.random() < .45:   # abajo, a veces un pallet con carga
                pallet((c0, mv) if ax else (mv, c0), ax, carga_max=1.0); continue
            while uu < c0 + b / 2 - .3:
                w = .36 + rnd.random() * .34; h = min(.26 + rnd.random() * .42, top); dd = min(d - .12, .45 + rnd.random() * .5)
                if uu + w > c0 + b / 2 - .06: break
                if rnd.random() > .15:
                    yb = y0 + (.069 if y0 else 0) + h / 2; c, sz = P(ax, uu + w / 2, yb, mv + (rnd.random() - .5) * (d - dd - .1), w, h, dd); caja(c, sz, (rnd.random() - .5) * .08)
                    if rnd.random() < .4 and h + .3 < top:
                        h2 = .18 + rnd.random() * .16; c, sz = P(ax, uu + w / 2, yb + h / 2 + h2 / 2, mv + (rnd.random() - .5) * .15, w * .85, h2, dd * .8); caja(c, sz, (rnd.random() - .5) * .25)
                uu += w + .03 + rnd.random() * .05
def pallet(c, ax, carga_max=2.3, wrap=None, plast=None):
    X, Z = c; plast = (rnd.random() < .55) if plast is None else plast
    su, sv = (1.2, 1.0) if ax else (1.0, 1.2)
    def B(du, y, dv, a, h, bb, g): G[g].box((X + du, y, Z + dv), (a, h, bb), 0)
    if plast:
        g = 'pl_azul' if rnd.random() < .65 else 'pl_rojo'; B(0, .135, 0, su, .03, sv, g)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1): B(i * (su / 2 - .07), .065, j * (sv / 2 - .07), .13, .11, .13, g)
        for i in (-1, 0, 1): B(0 if ax else i * (su / 2 - .07), .01, i * (sv / 2 - .07) if ax else 0, su if ax else .13, .02, .13 if ax else sv, g)
        ytop = .15
    else:   # madera: 7 tablas arriba (a lo largo del lado corto), 3 largueros, 9 tacos, 3 tablas abajo
        long_u = ax; Lg, Sh = (su, sv) if ax else (sv, su)
        for k in range(7):
            t = -Lg / 2 + .05 + k * (Lg - .1) / 6
            if ax: B(t, .133, 0, .1, .022, sv, 'pino')
            else: B(0, .133, t, su, .022, .1, 'pino')
        for k in (-1, 0, 1):
            if ax: B(0, .111, k * (sv / 2 - .05), su, .022, .1, 'pino')
            else: B(k * (su / 2 - .05), .111, 0, .1, .022, sv, 'pino')
            for j in (-1, 0, 1):
                if ax: B(j * (su / 2 - .05), .061, k * (sv / 2 - .05), .1, .078, .1, 'pino')
                else: B(k * (su / 2 - .05), .061, j * (sv / 2 - .05), .1, .078, .1, 'pino')
            if ax: B(0, .011, k * (sv / 2 - .05), su, .022, .1, 'pino')
            else: B(k * (su / 2 - .05), .011, 0, .1, .022, sv, 'pino')
        ytop = .144
    top = ytop + .6 + rnd.random() * (carga_max - .6); y = ytop
    tipo = rnd.random()
    while y < top - .15:
        h = .22 + rnd.random() * .38; n = 2 if rnd.random() < .45 else 4
        if y + h > top + .1: break
        for k in range(n):
            if n == 2: du, dv, w, dd = (k - .5) * .58, 0, .56, .96
            else: du, dv, w, dd = ((k % 2) - .5) * .58, (k // 2 - .5) * .48, .55, .46
            if not ax: du, dv, w, dd = dv, du, dd, w
            caja((X + du + (rnd.random() - .5) * .03, y + h / 2, Z + dv + (rnd.random() - .5) * .03), (w, h, dd), (rnd.random() - .5) * .04, 2 if tipo < .12 else None)
        y += h + .004
    if (wrap if wrap is not None else rnd.random() < .8) and y > ytop + .3:
        G['film'].box((X, (y + ytop - .04) / 2 + .02, Z), (su + .03, y - ytop + .02, sv + .03), (rnd.random() - .5) * .02)
def linea(o, wrap=True):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); ax = (x1 - x0) >= (z1 - z0)
    Lr = (x1 - x0) if ax else (z1 - z0); d = (z1 - z0) if ax else (x1 - x0); filas = max(1, int((d + .1) // 1.1))
    for r in range(filas):
        m = (z0 if ax else x0) + (r + .5) * d / filas; u = .05
        while u + 1.2 <= Lr + .05:
            cc = (x0 if ax else z0) + u + .6; pallet((cc, m) if ax else (m, cc), ax, carga_max=2.3 if wrap else 1.6, wrap=wrap and rnd.random() < .85); u += 1.24
def rack_bandejas(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); ax = (x1 - x0) > (z1 - z0)
    Lr = (x1 - x0) if ax else (z1 - z0); d = (z1 - z0) if ax else (x1 - x0); mv = (z0 + z1) / 2 if ax else (x0 + x1) / 2; u0 = x0 if ax else z0
    n = max(1, round(Lr / 2.05)); b = Lr / n; HY = 1.75; HU = 1.95
    for i in range(n + 1):
        for s in (-1, 1): montante('mont_w', ax, u0 + i * b, mv + s * (d / 2 - .04), HU, -s)
        for y in (.22, 1.0): c, sz = P(ax, u0 + i * b, y, mv, .03, .03, d - .1); G['br_w'].box(c, sz)
    for i in range(n):
        c0 = u0 + (i + .5) * b
        for s in (-1, 1): c, sz = P(ax, c0, HY, mv + s * (d / 2 - .04), b - .09, .11, .05); G['viga'].box(c, sz)
        c, sz = P(ax, c0, HY + .065, mv, b - .1, .018, d - .1); G['deck'].box(c, sz)
        uu = c0 - b / 2 + .1
        while uu < c0 + b / 2 - .35:
            w = .38 + rnd.random() * .3; h = .3 + rnd.random() * .3; dd = .42 + rnd.random() * .3
            if rnd.random() > .1: c, sz = P(ax, uu + w / 2, HY + .075 + h / 2, mv + (rnd.random() - .5) * (d - dd - .1), w, h, dd); caja(c, sz)
            uu += w + .05
        for k in (-1, 1):
            for r in (-1, 1):
                su_, sv_ = c0 + k * b / 4, mv + r * d / 4; nb = 10 + rnd.randrange(4); cl = rnd.choice(ROSA)
                c, sz = P(ax, su_, .1, sv_, .7, .035, .48); G['carro'].box(c, sz)
                for a_, e_ in ((-.3, -.2), (.3, -.2), (-.3, .2), (.3, .2)): c, sz = P(ax, su_ + a_, .045, sv_ + e_, .06, .09, .035); G['rueda'].box(c, sz)
                for j in range(nb):
                    c, sz = P(ax, su_ + (rnd.random() - .5) * .015, .12 + j * .095 + .047, sv_, .68, .092, .46)
                    col = rnd.choice(ROSA) if rnd.random() < .25 else cl
                    G['bandeja'].box(c, sz, 0, (0, 0, 1, 1), col)
for o in MAP:
    t = o['tipo']; nm = o.get('nombre', '')
    if t == 'rack' and 'bandejas' in nm.lower(): rack_bandejas(o)
    elif t == 'rack': rack(o, 'w' if 'clara' in nm.lower() else 'b' if 'azul' in nm.lower() else 'n')
    elif t == 'pallets' and not any(k in nm.lower() for k in ('torre', 'vacío', 'vacio')): linea(o, True)
    elif t == 'cajas': linea(o, False)

# =====================================================================
# v79 · segunda parte: cámaras de panel, bandejas portacables con bajada bajo el 2º nivel, objetos y sombras de contacto
# =====================================================================
K = dict(XW=-60.8, XF=-55.85, ZS=.3, ZA=4.7, RZ0=73.6, RX0=-74.65, HT=7.4, HC=3.0)   # medidas leídas del simulador (window.__trasK)
N2 = (-59.2, -46.4, 18.2, 69.0); LOSA_INF = 3.2                                        # 2º nivel: losa a 3,4 m, cara inferior 3,2 m
bajo_losa = lambda x, z: N2[0] <= x <= N2[1] and N2[2] <= z <= N2[3]
M.update(
  panel=mk('tras_panel_camara', (1, 1, 1), .42, .05, 'panel_camara_diff', 'panel_camara_norm', .6),
  techo_cam=mk('tras_techo_camara', (.88, .89, .88), .5, .05, 'panel_camara_diff', 'panel_camara_norm', .4),
  remate=mk('tras_remate_galv', (.70, .72, .72), .35, .9), zocalo=mk('tras_zocalo_galv', (.55, .57, .57), .45, .85),
  baranda=mk('tras_baranda_blanca', (.90, .90, .88), .4, .1), franjas=mk('tras_franjas', (1, 1, 1), .5, 0, 'franjas_diff'),
  malla=mk('tras_bandeja_malla', (1, 1, 1), .4, .3, 'malla_bandeja', atex=True), alambre=mk('tras_bandeja_alambre', (.92, .93, .93), .4, .3),
  canal=mk('tras_canal_soporte', (.86, .87, .86), .45, .4), varilla=mk('tras_varilla', (.55, .57, .58), .4, .9),
  cab_neg=mk('tras_cable_negro', (.03, .03, .03), .55), cab_gris=mk('tras_cable_gris', (.55, .56, .57), .55), cab_verde=mk('tras_cable_verde', (.35, .75, .45), .5),
  cab_azul=mk('tras_cable_azul', (.18, .35, .70), .5), cab_nar=mk('tras_cable_naranjo', (.85, .45, .15), .5),
  jaba_n=mk('tras_jaba_negra', (.05, .05, .055), .55, 0, 'jaba_diff', 'jaba_norm', .6), jaba_g=mk('tras_jaba_gris', (.55, .58, .60), .55, 0, 'jaba_diff', 'jaba_norm', .6),
  bolardo=mk('tras_bolardo_galv', (.66, .68, .68), .35, .9), gas=mk('tras_cañeria_gas', (.92, .74, .05), .4, .1),
  sombra_f=mk('tras_sombra_fuerte', (0, 0, 0), 1, 0, 'sombra_suave', atex=True), sombra_m=mk('tras_sombra_media', (0, 0, 0), 1, 0, 'sombra_suave', atex=True), sombra_l=mk('tras_sombra_leve', (0, 0, 0), 1, 0, 'sombra_suave', atex=True))
for k in ['panel', 'techo_cam', 'remate', 'zocalo', 'baranda', 'franjas', 'malla', 'alambre', 'canal', 'varilla', 'cab_neg', 'cab_gris', 'cab_verde', 'cab_azul', 'cab_nar', 'jaba_n', 'jaba_g', 'bolardo', 'gas', 'sombra_f', 'sombra_m', 'sombra_l']: G[k] = MB()
PUERTAS = [o for o in MAP if o['tipo'] == 'puerta']
def en_puerta(ax, u, c, tol=.25):
    for p in PUERTAS:
        x0, x1 = sorted(p['x']); z0, z1 = sorted(p['z'])
        if ax and abs((z0 + z1) / 2 - c) < tol and x0 - .05 <= u <= x1 + .05: return True
        if not ax and abs((x0 + x1) / 2 - c) < tol and z0 - .05 <= u <= z1 + .05: return True
    return False
def pared(ax, a, b, c, H, sgn, y0=0.):   # cara exterior de un muro de panel (ax: a lo largo de x en z=c; normal = sgn)
    a, b = min(a, b), max(a, b); L = b - a; u0 = a / 1.15
    if ax: pts = [(a, y0, c), (b, y0, c), (b, H, c), (a, H, c)]
    else: pts = [(c, y0, a), (c, y0, b), (c, H, b), (c, H, a)]
    uvs = [(u0, y0 / 3.0), (u0 + L / 1.15, y0 / 3.0), (u0 + L / 1.15, H / 3.0), (u0, H / 3.0)]
    if (ax and sgn < 0) or (not ax and sgn > 0): pts = pts[::-1]; uvs = uvs[::-1]   # que la normal mire hacia afuera
    G['panel'].quad(pts, uvs)
def camara(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); H = K['HC']
    for ax, a, b, c, sg in [(True, x0, x1, z0, -1), (True, x0, x1, z1, 1), (False, z0, z1, x0, -1), (False, z0, z1, x1, 1)]:
        pared(ax, a, b, c, H, sg)
        # zócalo sanitario galvanizado 15 cm (foto del pasillo), cortado en las puertas
        u = a; paso = .1; run = None   # tramos continuos (sin cortar en cada paso) para no multiplicar triángulos
        while u < b - .001:
            v = min(b, u + paso); libre = not en_puerta(ax, (u + v) / 2, c)
            if libre and run is None: run = u
            if (not libre or v >= b - .001) and run is not None:
                e = v if libre else u
                if e - run > .05:
                    m = (run + e) / 2
                    if ax: G['zocalo'].box((m, .075, c + sg * .012), (e - run + .002, .15, .024))
                    else: G['zocalo'].box((c + sg * .012, .075, m), (.024, .15, e - run + .002))
                run = None
            u = v
        # remate superior de chapa (ángulo) y unión con el techo
        if ax: G['remate'].box(((a + b) / 2, H + .02, c + sg * .02), (b - a + .08, .06, .05))
        else: G['remate'].box((c + sg * .02, H + .02, (a + b) / 2), (.05, .06, b - a + .08))
    # techo de panel con juntas
    G['techo_cam'].quad([(x0, H + .05, z0), (x0, H + .05, z1), (x1, H + .05, z1), (x1, H + .05, z0)], [(0, 0), (0, (z1 - z0) / 3), ((x1 - x0) / 1.15, (z1 - z0) / 3), ((x1 - x0) / 1.15, 0)])
    # baranda perimetral (solo donde no está bajo la losa del 2º nivel): tubo blanco, poste con funda de franjas abajo (foto)
    def poste(x, z):
        if bajo_losa(x, z): return
        G['franjas'].box((x, H + .2, z), (.05, .3, .05)); G['baranda'].box((x, H + .75, z), (.042, .8, .042))
    def riel(ax, a, b, c):
        pts = []; n = max(1, int((b - a) / .25))
        segs = []; cur = None
        for i in range(n + 1):
            u = a + (b - a) * i / n; x, z = (u, c) if ax else (c, u); ok = not bajo_losa(x, z)
            if ok and cur is None: cur = u
            if (not ok or i == n) and cur is not None: segs.append((cur, u)); cur = None
        for s0, s1 in segs:
            if s1 - s0 < .3: continue
            for y in (H + 1.1, H + .58):
                if ax: G['baranda'].box(((s0 + s1) / 2, y, c), (s1 - s0, .045, .045))
                else: G['baranda'].box((c, y, (s0 + s1) / 2), (.045, .045, s1 - s0))
    for ax, a, b, c in [(True, x0, x1, z0 + .05), (True, x0, x1, z1 - .05), (False, z0, z1, x0 + .05), (False, z0, z1, x1 - .05)]:
        riel(ax, a, b, c); u = a + .1
        while u <= b - .05: poste(*((u, c) if ax else (c, u))); u += 1.5
        poste(*((b - .05, c) if ax else (c, b - .05)))
def sombra(x0, x1, z0, z1, m, g='sombra_m', y=.004):   # 9 cortes: núcleo oscuro y borde suave de ancho m (oclusión de contacto)
    X = [x0 - m, x1 + m]; Z = [z0 - m, z1 + m]; wx = min(2 * m, (X[1] - X[0]) / 2); wz = min(2 * m, (Z[1] - Z[0]) / 2)
    xs = [X[0], X[0] + wx, X[1] - wx, X[1]]; zs = [Z[0], Z[0] + wz, Z[1] - wz, Z[1]]; us = [0, .5, .5, 1]
    for i in range(3):
        for j in range(3):
            if xs[i + 1] - xs[i] < .001 or zs[j + 1] - zs[j] < .001: continue
            G[g].quad([(xs[i], y, zs[j]), (xs[i], y, zs[j + 1]), (xs[i + 1], y, zs[j + 1]), (xs[i + 1], y, zs[j])], [(us[i], us[j]), (us[i], us[j + 1]), (us[i + 1], us[j + 1]), (us[i + 1], us[j])])
# ---- bandejas portacables: rejilla con bajada moldeada bajo la losa del 2º nivel (fotos «bandeja_cables_bajo_segundo_nivel» y «trastienda») ----
def norm3(v):
    l = math.sqrt(sum(c * c for c in v)) or 1; return tuple(c / l for c in v)
def bandeja(path, w, cables, prof=.1):
    """path: lista de puntos (x, y, z) del fondo de la bandeja en coords del plano"""
    acc = 0.
    for i in range(len(path) - 1):
        p, q = path[i], path[i + 1]; d = norm3((q[0] - p[0], q[1] - p[1], q[2] - p[2])); l = norm3((-d[2], 0, d[0])) if abs(d[0]) + abs(d[2]) > 1e-6 else (1, 0, 0)
        L = math.dist(p, q); ext = .012   # traslape de 12 mm entre tramos (sin costura)
        p2 = tuple(p[k] - d[k] * ext for k in range(3)); q2 = tuple(q[k] + d[k] * ext for k in range(3))
        off = lambda P_, s, h: (P_[0] + l[0] * s, P_[1] + h, P_[2] + l[2] * s)
        u0, u1 = acc / .4, (acc + L) / .4; acc += L
        G['malla'].quad([off(p2, -w / 2, 0), off(q2, -w / 2, 0), off(q2, w / 2, 0), off(p2, w / 2, 0)], [(u0, 0), (u1, 0), (u1, w / .4), (u0, w / .4)])
        for s in (-1, 1):
            G['malla'].quad([off(p2, s * w / 2, 0), off(q2, s * w / 2, 0), off(q2, s * w / 2, prof), off(p2, s * w / 2, prof)], [(u0, 0), (u1, 0), (u1, prof / .4), (u0, prof / .4)])
            for h in (prof, .002):   # alambres de borde más gruesos (arriba) y de fondo
                a_, b_ = off(p2, s * w / 2, h), off(q2, s * w / 2, h); G['alambre'].quad([a_, b_, (b_[0], b_[1] + .008, b_[2]), (a_[0], a_[1] + .008, a_[2])], [(0, 0), (1, 0), (1, 1), (0, 1)])
        for j, (gm, sc) in enumerate(cables):   # mazos de cables dentro
            a_, b_ = off(p2, sc * w / 2, .012 + j * .004), off(q2, sc * w / 2, .012 + j * .004); r = .018 + (j % 3) * .006
            G[gm].quad([(a_[0] - l[0] * r, a_[1], a_[2] - l[2] * r), (b_[0] - l[0] * r, b_[1], b_[2] - l[2] * r), (b_[0] + l[0] * r, b_[1] + r, b_[2] + l[2] * r), (a_[0] + l[0] * r, a_[1] + r, a_[2] + l[2] * r)], [(0, 0), (1, 0), (1, 1), (0, 1)])
def trapecio(x, y, z, ax, span):   # soporte: canal 41×41 bajo las bandejas + 2 varillas roscadas al cielo
    techo = LOSA_INF if bajo_losa(x, z) else K['HT'] - .25
    if ax: G['canal'].box((x, y - .022, z), (.042, .042, span))
    else: G['canal'].box((x, y - .022, z), (span, .042, .042))
    for s in (-1, 1):
        px, pz = (x, z + s * (span / 2 - .03)) if ax else (x + s * (span / 2 - .03), z)
        G['varilla'].box((px, (y + techo) / 2, pz), (.012, techo - y, .012))
def ruta_z(x, z0, z1, yA, yB, zb0=15.4, zb1=18.05, zr0=69.15, zr1=71.6):   # bajada suave antes de la losa y subida después (curva moldeada)
    pts = [(x, yA, z0)]; st = lambda t: t * t * (3 - 2 * t)
    for i in range(13): t = i / 12; pts.append((x, yA + (yB - yA) * st(t), zb0 + (zb1 - zb0) * t))
    for i in range(13): t = i / 12; pts.append((x, yB + (yA - yB) * st(t), zr0 + (zr1 - zr0) * t))
    pts.append((x, yA, z1)); return pts
# v85 (Cristian, fotos y videos del recorrido 24-11): dos bandejas lado a lado al CENTRO de los pasillos, entre las dos cañerías de red húmeda
#   (pasillo sur: cañería junto a los pilares del muro de la calle y otra junto al muro de la sala; corredor poniente: las dos cañerías van
#   juntas por el lado del muro poniente). Bajo la losa del 2º nivel las bandejas bajan pegadas a la losa y vuelven a subir antes de recepción.
YH, YL = 6.1, 2.95
zT1, zT2 = 3.45, 3.88          # pasillo sur (centro z de cada bandeja)
xT1, xT2 = -57.2, -56.77       # corredor poniente (centro x de cada bandeja)
CAB1 = [('cab_neg', -.5), ('cab_gris', .1), ('cab_verde', .45), ('cab_azul', -.1), ('cab_nar', .3)]; CAB2 = [('cab_neg', .3), ('cab_gris', -.35), ('cab_neg', 0.)]
bandeja([(-4.6, YH, zT1), (xT1, YH, zT1)], .45, CAB1)                                     # pasillo sur
bandeja([(-4.6, YH, zT2), (xT2, YH, zT2)], .3, CAB2)
bandeja(ruta_z(xT1, zT1, K['RZ0'] + 1.6, YH, YL), .45, CAB1)                               # corredor de las cámaras: baja bajo la losa y vuelve a subir
bandeja(ruta_z(xT2, zT2, K['RZ0'] + 1.6, YH, YL), .3, CAB2)
bandeja([(xT1, YH, K['RZ0'] + 1.6), (K['RX0'] + .8, YH, K['RZ0'] + 1.6)], .45, CAB1)       # recepción
zm, xm = (zT1 + zT2) / 2, (xT1 + xT2) / 2
for x in [v for v in [-4.9 - 1.5 * k for k in range(40)] if v > xT1 + .3]: trapecio(x, YH, zm, True, .95)
zz = zT2 + .5
while zz < K['RZ0'] + 1.2:
    if zz < 15.3 or zz > 71.7: trapecio(xm, YH, zz, False, .95)
    elif 18.15 < zz < 69.1: trapecio(xm, YL, zz, False, .95)
    zz += 1.5
# ---- cámaras y salas de panel ----
for o in MAP:
    if o['tipo'] == 'camara' and not re.search('recicl', o.get('nombre', ''), re.I): camara(o)
# ---- jabas y canastos apilados (fotos: pilas de cajones negros y grises) ----
def jabas(o, gm):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); ax = (x1 - x0) >= (z1 - z0); L = (x1 - x0) if ax else (z1 - z0); D = (z1 - z0) if ax else (x1 - x0)
    cw, cd, ch = .6, .4, .14 if gm == 'jaba_n' else .3
    nu, nv = max(1, int(L // (cw + .02))), max(1, int(D // (cd + .02)))
    for i in range(nu):
        for j in range(nv):
            n = int((1.75 if gm == 'jaba_n' else 1.5) // ch) - rnd.randrange(0, 4); u = (x0 if ax else z0) + (i + .5) * L / nu; v = (z0 if ax else x0) + (j + .5) * D / nv
            for k in range(n):
                jx, jz = (rnd.random() - .5) * .025, (rnd.random() - .5) * .025; c = (u + jx, k * ch + ch / 2, v + jz) if ax else (v + jz, k * ch + ch / 2, u + jx)
                G[gm].box(c, (cw, ch - .004, cd) if ax else (cd, ch - .004, cw), (rnd.random() - .5) * .03, (0, 0, 1, 1))
    sombra(x0, x1, z0, z1, .3, 'sombra_m')
for o in MAP:
    if o['tipo'] == 'jabas': jabas(o, 'jaba_n' if 'negro' in o.get('nombre', '').lower() else 'jaba_g')
BOLS = [((min(o['x']) + max(o['x'])) / 2, (min(o['z']) + max(o['z'])) / 2) for o in MAP if o['tipo'] == 'objeto' and 'bolardo' in o.get('nombre', '').lower()]
BOLS += [(-55.15, 4.95), (-55.15, 6.65)]   # par junto a la puerta de la cámara de merma (como el simulador)
for cx, cz in BOLS:   # bolardo galvanizado con placa base (foto)
    if True:
        n = 16
        for k in range(n):
            a, b = 2 * math.pi * k / n, 2 * math.pi * (k + 1) / n; r = .055
            G['bolardo'].quad([(cx + r * math.cos(a), .02, cz + r * math.sin(a)), (cx + r * math.cos(b), .02, cz + r * math.sin(b)), (cx + r * math.cos(b), 1.0, cz + r * math.sin(b)), (cx + r * math.cos(a), 1.0, cz + r * math.sin(a))][::-1], [(k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, 1), (k / n, 1)][::-1])
        G['bolardo'].box((cx, 1.0, cz), (.1, .012, .1)); G['bolardo'].box((cx, .006, cz), (.2, .012, .2)); sombra(cx - .05, cx + .05, cz - .05, cz + .05, .18, 'sombra_m')
# cañería amarilla de gas en la cámara de panadería (fotos «cámara de panadería y ascensor» y «trastienda») [posición SUPUESTO]
for x, z in [(-55.93, 58.0)]:
    G['gas'].box((x - .04, (0.9 + LOSA_INF) / 2, z), (.034, LOSA_INF - .9, .034)); G['gas'].box((x - .04, LOSA_INF - .25, (z + 52.8) / 2), (.034, .034, z - 52.8))
    for y in (1.2, 1.9, 2.6): G['remate'].box((x - .02, y, z), (.04, .05, .07))
    G['gas'].box((x - .06, .95, z), (.07, .08, .07))
# ---- v80 (bug 16 «objetos no modelados ni texturizados», zona de merma): lavamanos inox, dispensadores, basurero de pedal y repisa de alambre
#      reemplazan las cajas del simulador (tras_inox / negro_suave / escobillon / bandeja_gris en esa zona). Medidas típicas de catálogo [SUPUESTO]
M.update(inox=mk('tras_inox', (.78, .79, .80), .28, 1.), inox_sat=mk('tras_inox_satinado', (.70, .71, .72), .42, 1.),
         abs_bl=mk('tras_abs_blanco', (.86, .87, .87), .38), abs_gr=mk('tras_abs_gris', (.22, .23, .25), .45), goma=mk('tras_goma', (.03, .03, .03), .8))
for k in ('inox', 'inox_sat', 'abs_bl', 'abs_gr', 'goma'): G[k] = MB()
def cil(g, a, b, r, n=14, tapa=True):   # cilindro entre a y b (coords del plano)
    a, b = Vector(a), Vector(b); d = (b - a); L = d.length
    if L < 1e-6: return
    d.normalize(); t = Vector((1, 0, 0)) if abs(d.x) < .9 else Vector((0, 0, 1)); u = d.cross(t).normalized(); w = d.cross(u)
    ring = lambda c, k: c + (u * math.cos(2 * math.pi * k / n) + w * math.sin(2 * math.pi * k / n)) * r
    for k in range(n):
        p0, p1, p2, p3 = ring(a, k), ring(a, k + 1), ring(b, k + 1), ring(b, k)
        G[g].quad([tuple(p0), tuple(p1), tuple(p2), tuple(p3)], [(k / n, 0), ((k + 1) / n, 0), ((k + 1) / n, L), (k / n, L)])
    if tapa:
        for c, sg in ((a, -1), (b, 1)):
            pts = [tuple(ring(c, k)) for k in range(n)]
            G[g].quad(pts if sg > 0 else pts[::-1], [(.5 + .5 * math.cos(2 * math.pi * k / n), .5 + .5 * math.sin(2 * math.pi * k / n)) for k in range(n)])
LAV = next((o for o in MAP if o['tipo'] == 'lavamanos'), None)
if LAV:   # lavamanos de pie contra el muro sur de la sala (z 4,86), mirando al norte (+z)
    x0, x1 = sorted(LAV['x']); z0, z1 = sorted(LAV['z']); cx = (x0 + x1) / 2; zb = 4.88; zf = zb + .48; W = x1 - x0; yt = .86
    G['inox'].box((cx, yt - .01, (zb + zf) / 2), (W, .02, zf - zb))                       # cubierta (se ve el borde)
    G['inox'].box((cx, yt - .07, zf - .01), (W, .14, .02))                                  # faldón frontal
    for sx in (-1, 1): G['inox'].box((cx + sx * (W / 2 - .01), yt - .07, (zb + zf) / 2), (.02, .14, zf - zb))
    G['inox'].box((cx, yt + .08, zb + .01), (W, .16, .02))                                  # respaldo
    G['inox_sat'].box((cx, yt - .12, (zb + zf) / 2 + .02), (W - .14, .02, zf - zb - .14))    # fondo del pozo
    for sx in (-1, 1): G['inox_sat'].box((cx + sx * (W / 2 - .07), yt - .065, (zb + zf) / 2 + .02), (.012, .11, zf - zb - .14))
    for sz_ in (-1, 1): G['inox_sat'].box((cx, yt - .065, (zb + zf) / 2 + .02 + sz_ * ((zf - zb - .14) / 2)), (W - .14, .11, .012))
    cil('goma', (cx, yt - .115, (zb + zf) / 2 + .02), (cx, yt - .105, (zb + zf) / 2 + .02), .025, 12)   # desagüe
    for sx in (-1, 1):
        for zz in (zb + .05, zf - .05): cil('inox_sat', (cx + sx * (W / 2 - .05), .03, zz), (cx + sx * (W / 2 - .05), yt - .14, zz), .016, 10); cil('goma', (cx + sx * (W / 2 - .05), 0, zz), (cx + sx * (W / 2 - .05), .03, zz), .022, 10)
    cil('inox_sat', (cx - W / 2 + .05, .2, zb + .05), (cx + W / 2 - .05, .2, zb + .05), .01, 8); cil('inox_sat', (cx - W / 2 + .05, .2, zf - .05), (cx + W / 2 - .05, .2, zf - .05), .01, 8)
    cil('inox', (cx, yt + .16, zb + .05), (cx, yt + .34, zb + .05), .012, 10); cil('inox', (cx, yt + .34, zb + .05), (cx, yt + .34, zb + .2), .011, 10); cil('inox', (cx, yt + .34, zb + .2), (cx, yt + .27, zb + .2), .009, 10)   # grifo cuello de cisne
    G['inox'].box((cx, .55, zf + .005), (.09, .07, .02)); cil('inox_sat', (cx, .55, zf + .015), (cx, .55, zf + .05), .02, 10)   # válvula de rodilla
    # dispensador de toalla de papel y de jabón en el muro (encima del lavamanos)
    G['abs_bl'].box((cx, 1.45, zb + .06), (.30, .36, .11)); G['abs_gr'].box((cx, 1.29, zb + .115), (.24, .02, .01)); G['abs_gr'].box((cx + .11, 1.6, zb + .114), (.03, .03, .006))
    G['abs_bl'].box((cx + W / 2 + .03, 1.18, zb + .05), (.11, .2, .1)); G['abs_gr'].box((cx + W / 2 + .03, 1.12, zb + .1), (.06, .05, .012)); G['abs_gr'].box((cx + W / 2 + .03, 1.07, zb + .08), (.02, .02, .03))
BAS = next((o for o in MAP if o['tipo'] == 'objeto' and 'basurero inox' in o.get('nombre', '').lower()), None)
if BAS:   # basurero inox de pedal (redondo, con tapa y pedal)
    x0, x1 = sorted(BAS['x']); z0, z1 = sorted(BAS['z']); cx, cz = (x0 + x1) / 2, (z0 + z1) / 2 + .02; r = min(x1 - x0, z1 - z0) / 2 - .02
    cil('inox_sat', (cx, .03, cz), (cx, .6, cz), r, 24); cil('inox', (cx, .6, cz), (cx, .63, cz), r + .005, 24); cil('goma', (cx, 0, cz), (cx, .03, cz), r - .01, 24)
    G['inox'].box((cx, .03, cz + r + .04), (.12, .02, .1)); cil('inox', (cx, .65, cz - r + .02), (cx, .66, cz - r + .02), .03, 8)
REP = next((o for o in MAP if o['tipo'] == 'repisa'), None)
if REP:   # repisa de alambre cromado: 4 parrillas, postes redondos, bandejas grises encima
    x0, x1 = sorted(REP['x']); z0, z1 = sorted(REP['z']); ax = (x1 - x0) >= (z1 - z0)
    for px_ in (x0 + .02, x1 - .02):
        for pz_ in (z0 + .02, z1 - .02): cil('inox', (px_, 0, pz_), (px_, 1.82, pz_), .0125, 10); cil('goma', (px_, 0, pz_), (px_, .02, pz_), .018, 10)
    for y in (.25, .7, 1.15, 1.6):
        for zz in (z0 + .02, z1 - .02): cil('inox', (x0 + .02, y, zz), (x1 - .02, y, zz), .006, 6, False)
        for xx in (x0 + .02, x1 - .02): cil('inox', (xx, y, z0 + .02), (xx, y, z1 - .02), .006, 6, False)
        n = int((x1 - x0) / .05)
        for k in range(1, n): xx = x0 + k * (x1 - x0) / n; G['inox'].box((xx, y + .004, (z0 + z1) / 2), (.004, .004, z1 - z0 - .04))
        nb = max(1, int((x1 - x0) / .6))
        for k in range(nb):
            u = x0 + (k + .5) * (x1 - x0) / nb; G['carro'].box((u, y + .12, (z0 + z1) / 2), (.52, .2, (z1 - z0) * .85), (rnd.random() - .5) * .04)
# ---- v81 (bug 16, resto de la simulación): rincón de aseo, tableros eléctricos, perchero, dispensador de agua y pisos de jaula
#      reemplazan las cajas del simulador (tras_aseo_*, tras_blanco/baliza de tableros, tras_gal/chaqueta, tras_dispensador, tras_banquito). Medidas de catálogo [SUPUESTO: sin foto de estos objetos]
M.update(pl_rojo2=mk('tras_plast_rojo', (.60, .06, .05), .45), pl_negro=mk('tras_plast_negro', (.035, .035, .04), .5), pl_amar=mk('tras_plast_amarillo', (.85, .62, .03), .45),
         pl_azul2=mk('tras_plast_azul', (.08, .25, .62), .45), pl_gris=mk('tras_plast_gris', (.42, .44, .46), .5), maq=mk('tras_maquina_gris', (.16, .17, .18), .4),
         ral=mk('tras_tablero_ral7035', (.74, .75, .73), .42), tela_n=mk('tras_tela_negra', (.03, .03, .035), .9), tela_az=mk('tras_tela_azul', (.03, .06, .16), .9),
         chaleco=mk('tras_chaleco_fluor', (.75, .85, .02), .7), refl=mk('tras_cinta_reflectante', (.62, .63, .62), .3, .6), agua=mk('tras_bidon_agua', (.30, .55, .85), .1, 0, alpha=.55),
         piloto_v=mk('tras_piloto_verde', (.1, .8, .2), .3), piloto_r=mk('tras_piloto_rojo', (.85, .08, .05), .3), madera_m=mk('tras_mango_madera', (.55, .38, .22), .7))
for k in ('pl_rojo2', 'pl_negro', 'pl_amar', 'pl_azul2', 'pl_gris', 'maq', 'ral', 'tela_n', 'tela_az', 'chaleco', 'refl', 'agua', 'piloto_v', 'piloto_r', 'madera_m'): G[k] = MB()
B3 = lambda g, x0, x1, y0, y1, z0, z1, r=0.: G[g].box(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), (x1 - x0, y1 - y0, z1 - z0), r)
# --- rincón de aseo contra el muro sur (z 1,74), de poniente a oriente (orden del simulador v49)
ASE = next((o for o in MAP if o['tipo'] == 'objeto' and re.search('fregadora', o.get('nombre', ''), re.I)), None)
if ASE:
    X0 = min(ASE['x']); ZW = max(1.74, min(ASE['z'])) + .02; sk = min(1, (max(ASE['x']) - X0) / 4.95); U = lambda u: X0 + u * sk
    # porta herramientas en el muro + 4 útiles colgados + balde de trapero con estrujador
    B3('galv', U(.12), U(.78), 1.38, 1.44, ZW, ZW + .04)
    for k, (col, cab) in enumerate([('pl_azul2', 'escoba'), ('pl_amar', 'trapero'), ('pl_rojo2', 'escoba'), ('pl_azul2', 'secador')]):
        xx = U(.2 + k * .17); cil('pl_negro', (xx, 1.36, ZW + .06), (xx, 1.44, ZW + .06), .018, 8)
        cil('madera_m' if k % 2 else 'galv', (xx, 1.42, ZW + .07), (xx + .03, .16, ZW + .11), .012, 8)
        if cab == 'escoba': B3(col, xx - .13, xx + .19, .1, .16, ZW + .07, ZW + .14); B3('pl_negro', xx - .12, xx + .18, .02, .1, ZW + .08, ZW + .13)
        elif cab == 'trapero':
            for j in range(9): cil('abs_bl', (xx + .03, .2, ZW + .11), (xx + .03 + (j % 3 - 1) * .05, .02, ZW + .11 + (j // 3 - 1) * .04), .012, 6)
        else: B3('goma', xx - .2, xx + .25, .02, .1, ZW + .1, ZW + .12); B3(col, xx - .2, xx + .25, .1, .14, ZW + .09, ZW + .13)
    bx, bz = U(.5), ZW + .42
    B3('pl_azul2', bx - .2, bx + .2, .08, .36, bz - .16, bz + .16); B3('pl_amar', bx - .1, bx + .2, .36, .52, bz - .12, bz + .12)
    for (a, c) in [(-.17, -.13), (.17, -.13), (-.17, .13), (.17, .13)]: cil('goma', (bx + a, .0, bz + c), (bx + a, .07, bz + c), .03, 8)
    cil('galv', (bx - .1, .52, bz), (bx - .1, .9, bz), .01, 6)
    # fregadora de conductor sentado (cuerpo, asiento, columna y volante, ruedas, secador trasero)
    fx, fz, L_, W_ = U(1.45), ZW + .36, 1.2 * sk, .66
    B3('maq', fx - L_ / 2, fx + L_ / 2, .14, .78, fz - W_ / 2, fz + W_ / 2); B3('pl_azul2', fx - L_ / 2 - .005, fx + L_ / 2 + .005, .5, .56, fz - W_ / 2 - .005, fz + W_ / 2 + .005)
    B3('pl_negro', fx - .05, fx + .35, .78, .9, fz - .2, fz + .2); B3('pl_negro', fx + .3, fx + .38, .9, 1.25, fz - .19, fz + .19)
    cil('maq', (fx - .35, .78, fz), (fx - .25, 1.15, fz), .035, 10); cil('pl_negro', (fx - .3, 1.15, fz - .15), (fx - .27, 1.17, fz + .15), .02, 8)
    cil('pl_negro', (fx - .27, 1.16, fz), (fx - .3, 1.13, fz), .16, 20)
    for xx in (fx - L_ / 2 + .2, fx + L_ / 2 - .25):
        for sg in (-1, 1): cil('goma', (xx, .13, fz + sg * (W_ / 2 - .02)), (xx, .13, fz + sg * (W_ / 2 + .03)), .13, 18)
    B3('goma', fx + L_ / 2 + .02, fx + L_ / 2 + .06, .0, .06, fz - W_ / 2 - .08, fz + W_ / 2 + .08); B3('maq', fx + L_ / 2, fx + L_ / 2 + .08, .06, .14, fz - W_ / 2 - .05, fz + W_ / 2 + .05)
    cil('pl_amar', (fx - .45, .78, fz + .2), (fx - .45, .8, fz + .2), .07, 14)   # tapa del estanque
    # carro de aseo: chasis negro, balde amarillo con estrujador, aro con bolsa gris, bandeja superior
    cx_, cz_ = U(2.35), ZW + .3
    B3('pl_negro', cx_ - .3, cx_ + .3, .1, .14, cz_ - .26, cz_ + .26); B3('pl_negro', cx_ + .2, cx_ + .3, .14, 1.0, cz_ - .24, cz_ + .24)
    B3('pl_negro', cx_ - .3, cx_ + .3, .95, 1.0, cz_ - .26, cz_ + .26)
    B3('pl_amar', cx_ - .28, cx_ + .02, .14, .42, cz_ - .2, cz_ + .2); B3('pl_gris', cx_ - .22, cx_ - .02, .42, .62, cz_ - .1, cz_ + .1)
    cil('galv', (cx_ - .02, .45, cz_ - .2), (cx_ - .02, .95, cz_ - .2), .01, 6); B3('pl_gris', cx_ - .05, cx_ + .18, .45, .9, cz_ - .2, cz_ + .2)
    for (a, c) in [(-.26, -.22), (.26, -.22), (-.26, .22), (.26, .22)]: cil('goma', (cx_ + a, .05, cz_ + c - .02), (cx_ + a, .05, cz_ + c + .02), .05, 12)
    # contenedor rojo de 240 L con tapa negra y ruedas
    rx, rz = U(3.05), ZW + .3
    B3('pl_rojo2', rx - .27, rx + .27, .08, .92, rz - .3, rz + .26); B3('pl_negro', rx - .29, rx + .29, .92, .97, rz - .33, rz + .3)
    B3('pl_negro', rx - .25, rx + .25, .86, .9, rz - .36, rz - .3)
    for sg in (-1, 1): cil('goma', (rx + sg * .29, .1, rz - .3), (rx + sg * .25, .1, rz - .3), .1, 16)
    # mesón inox con repisa inferior
    mx, mw = U(3.85), 1.0 * sk
    B3('inox', mx - mw / 2, mx + mw / 2, .83, .87, ZW, ZW + .6); B3('inox', mx - mw / 2, mx + mw / 2, .87, 1.0, ZW, ZW + .02)
    B3('inox_sat', mx - mw / 2 + .04, mx + mw / 2 - .04, .2, .22, ZW + .04, ZW + .56)
    for a in (-1, 1):
        for zz in (ZW + .05, ZW + .55): cil('inox_sat', (mx + a * (mw / 2 - .05), .03, zz), (mx + a * (mw / 2 - .05), .83, zz), .018, 10); cil('goma', (mx + a * (mw / 2 - .05), 0, zz), (mx + a * (mw / 2 - .05), .03, zz), .022, 10)
    # gabinete inox de 2 puertas
    gx, gw = U(4.6), .6 * sk
    B3('inox_sat', gx - gw / 2, gx + gw / 2, .08, 1.68, ZW, ZW + .48); B3('inox', gx - gw / 2 + .01, gx - .004, .1, 1.66, ZW + .48, ZW + .5); B3('inox', gx + .004, gx + gw / 2 - .01, .1, 1.66, ZW + .48, ZW + .5)
    for a in (-1, 1): B3('goma', gx + a * .03 - .007, gx + a * .03 + .007, .9, 1.1, ZW + .5, ZW + .52)
    sombra(U(.1), U(4.95), ZW, ZW + .7, .25, 'sombra_m')
# --- tableros eléctricos de piso contra el muro poniente (gris RAL 7035, puerta con manilla, pilotos y ducto al techo)
for o in MAP:
    if o['tipo'] != 'tablero' or not re.search('el[eé]ctrico', o.get('nombre', ''), re.I): continue
    x0 = min(o['x']); z0, z1 = sorted(o['z']); xf = x0 + .47
    B3('ral', x0 + .01, xf, .1, 2.0, z0 + .03, z1 - .03); B3('goma', x0 + .03, xf - .02, 0, .1, z0 + .05, z1 - .05)
    B3('ral', xf, xf + .015, .14, 1.96, z0 + .06, (z0 + z1) / 2 - .004); B3('ral', xf, xf + .015, .14, 1.96, (z0 + z1) / 2 + .004, z1 - .06)
    for zz in ((z0 + z1) / 2 - .05, (z0 + z1) / 2 + .05): B3('pl_negro', xf + .015, xf + .04, .95, 1.15, zz - .012, zz + .012)
    for k, g in enumerate(('piloto_v', 'piloto_r', 'pl_amar')): cil(g, (xf + .015, 1.75, z0 + .2 + k * .07), (xf + .03, 1.75, z0 + .2 + k * .07), .012, 10)
    B3('abs_bl', xf + .015, xf + .018, 1.55, 1.63, z0 + .15, z0 + .35); B3('pl_amar', xf + .015, xf + .018, 1.3, 1.42, z1 - .25, z1 - .13)
    for k in range(5): B3('maq', xf + .015, xf + .017, .3 + k * .03, .31 + k * .03, z1 - .3, z1 - .1)
    cil('pl_negro', (x0 + .15, 2.0, (z0 + z1) / 2), (x0 + .15, 2.72, (z0 + z1) / 2), .025, 10); cil('pl_gris', (x0 + .3, 2.0, (z0 + z1) / 2), (x0 + .3, 2.72, (z0 + z1) / 2), .02, 10)
    sombra(x0, xf, z0, z1, .2, 'sombra_m')
# --- perchero móvil con chaquetas y chaleco reflectante
PER = next((o for o in MAP if o['tipo'] == 'tablero' and 'perchero' in o.get('nombre', '').lower()), None)
if PER:
    cx = sum(PER['x']) / 2; z0, z1 = sorted(PER['z']); H_ = 1.75
    for zz in (z0 + .05, z1 - .05):
        cil('galv', (cx, .05, zz), (cx, H_, zz), .015, 10); cil('galv', (cx - .25, .04, zz), (cx + .25, .04, zz), .013, 8)
        for a in (-.25, .25): cil('goma', (cx + a, 0, zz), (cx + a, .03, zz), .025, 10)
    cil('galv', (cx, H_, z0 + .05), (cx, H_, z1 - .05), .012, 10)
    for k, g in enumerate(('tela_n', 'tela_az', 'chaleco', 'tela_n')):
        zz = z0 + .2 + k * (z1 - z0 - .4) / 3; yh = H_ - .06
        cil('galv', (cx, H_, zz), (cx, yh, zz), .003, 6); cil('pl_negro', (cx - .2, yh, zz), (cx + .2, yh, zz), .008, 6)
        if g == 'chaleco':
            B3(g, cx - .22, cx + .22, yh - .62, yh - .04, zz - .04, zz + .04); B3('refl', cx - .225, cx + .225, yh - .45, yh - .4, zz - .045, zz + .045); B3('refl', cx - .225, cx + .225, yh - .3, yh - .25, zz - .045, zz + .045)
        else:
            B3(g, cx - .23, cx + .23, yh - .78, yh - .05, zz - .06, zz + .06); B3(g, cx - .08, cx + .08, yh - .05, yh + .02, zz - .05, zz + .05)
            for sg in (-1, 1): cil(g, (cx + sg * .2, yh - .08, zz), (cx + sg * .25, yh - .72, zz), .055, 10)
            B3('pl_negro', cx - .005, cx + .005, yh - .7, yh - .1, zz + .058, zz + .062)   # cierre
# --- dispensador de agua de recepción (bidón 20 L) contra el muro norte
for (dx_, dz_) in [(-58.5, 82.25)]:   # posición del simulador (xo − 0,3; RZ1 − 0,25)
    B3('abs_bl', dx_ - .16, dx_ + .16, .02, 1.0, dz_ - .16, dz_ + .17); B3('abs_gr', dx_ - .16, dx_ + .16, 0, .04, dz_ - .16, dz_ + .17)
    B3('abs_gr', dx_ - .12, dx_ + .12, .7, .9, dz_ - .175, dz_ - .16); B3('abs_gr', dx_ - .1, dx_ + .1, .5, .52, dz_ - .2, dz_ - .12)
    cil('piloto_r', (dx_ - .05, .8, dz_ - .18), (dx_ - .05, .76, dz_ - .18), .012, 8); cil('pl_azul2', (dx_ + .05, .8, dz_ - .18), (dx_ + .05, .76, dz_ - .18), .012, 8)
    cil('agua', (dx_, 1.0, dz_), (dx_, 1.04, dz_), .08, 16); cil('agua', (dx_, 1.04, dz_), (dx_, 1.1, dz_), .135, 20); cil('agua', (dx_, 1.1, dz_), (dx_, 1.42, dz_), .14, 20); cil('agua', (dx_, 1.42, dz_), (dx_, 1.47, dz_), .1, 20)
    sombra(dx_ - .16, dx_ + .16, dz_ - .16, dz_ + .17, .15, 'sombra_m')
# --- pisos de plástico azul en las jaulas (posición del simulador: centro de la jaula + 0,3 en x)
for o in MAP:
    if o['tipo'] != 'jaula': continue
    sx = sum(o['x']) / 2 + .3; sz = sum(o['z']) / 2
    B3('pl_azul2', sx - .2, sx + .2, .42, .46, sz - .16, sz + .16); B3('pl_azul2', sx - .2, sx + .2, .2, .23, sz - .02, sz + .2)
    for (a, c) in [(-.17, -.14), (.17, -.14), (-.19, .18), (.19, .18)]: cil('pl_azul2', (sx + a * .9, .44, sz + c * .9), (sx + a, 0, sz + c), .018, 8)
# ---- v82 (bug 16, patio): pallets con mercadería envueltos, pilas de bandejas, jabas rojas, torres de pallets vacíos, carros de supermercado,
#      contenedores verdes de cartón y maxisacos, desde el plano del patio (PATIO_MAP_DEF del simulador). Fotos: carpeta «patio» (s1–s4, p10–p18).
#      El patio baja 1,2 m entre z 50,2 y el andén (z 73,3): cada objeto se asienta a la altura del piso en su centro (como el simulador).
PATIO = [{"tipo": "pallets", "nombre": "Torre de pallet vacíos (copia)", "x": [-72.85, -74.15], "z": [54.605, 73.135]}, {"tipo": "contenedor", "nombre": "Recicladora de cartones", "x": [-62.7, -65.8], "z": [62.4, 69.75]}, {"tipo": "contenedor", "nombre": "Contenedor verde zona media", "x": [-60.0, -62.6], "z": [25.1, 31.1]}, {"tipo": "torre_pallets", "nombre": "Torre de pallet vacíos (4)", "x": [-62.7, -64.0], "z": [57.75, 62.4]}, {"tipo": "torre_pallets", "nombre": "Torre de pallet vacíos (5)", "x": [-64.0, -65.3], "z": [57.75, 62.4]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (oriente 2)", "x": [-62.3, -63.7], "z": [32.0, 36.5]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (poniente)", "x": [-64.5, -67.2], "z": [8.9, 12.6]}, {"tipo": "jabas", "nombre": "Jabas rojas", "x": [-73.3, -74.5], "z": [50.6, 53.1]}, {"tipo": "jabas", "nombre": "Jabas rojas (2)", "x": [-73.3, -74.5], "z": [53.3, 54.5]}, {"tipo": "pallets", "nombre": "Pila de bandejas envuelta", "x": [-59.5, -60.9], "z": [36.7, 41.0]}, {"tipo": "carros", "nombre": "Zona de carros", "x": [-59.395, -61.745], "z": [43.2, 48.8]}, {"tipo": "maxisaco", "nombre": "Maxisacos", "x": [-61.8, -63.9], "z": [48.68, 50.98]}, {"tipo": "pallets", "nombre": "Pila de bandejas envuelta (copia)", "x": [-60.9, -62.3], "z": [36.7, 41.0]}, {"tipo": "pallets", "nombre": "Pila de bandejas envuelta (copia) (copia)", "x": [-62.3, -63.7], "z": [36.7, 41.0]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (oriente 2) (copia)", "x": [-60.9, -62.3], "z": [32.0, 36.5]}, {"tipo": "torre_pallets", "nombre": "Torre de pallet vacíos (3) (copia)", "x": [-59.5, -63.55], "z": [23.0, 24.5]}, {"tipo": "torre_pallets", "nombre": "Torre de pallet vacíos (3) (copia) (2)", "x": [-59.5, -60.9], "z": [32.0, 36.5]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (oriente) (copia)", "x": [-59.5, -60.9], "z": [20.0, 23.0]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (oriente) (copia) (copia)", "x": [-60.9, -62.3], "z": [20.0, 23.0]}, {"tipo": "pallets", "nombre": "Pallets con mercadería (oriente) (copia) (copia) (copia)", "x": [-62.3, -63.55], "z": [20.0, 23.0]}, {"tipo": "carros", "nombre": "Jaula guardar bicicletas", "x": [-59.55, -63.75], "z": [13.7, 19.7]}]
M.update(jaba_a=mk('tras_jaba_azul', (.16, .36, .70), .55, 0, 'jaba_diff', 'jaba_norm', .6), jaba_r=mk('tras_jaba_roja', (.72, .16, .13), .55, 0, 'jaba_diff', 'jaba_norm', .6),
         verde=mk('tras_contenedor_verde', (.14, .36, .13), .55, .25), verde_o=mk('tras_contenedor_verde_osc', (.08, .24, .08), .6, .25), oxido=mk('tras_oxido', (.30, .16, .08), .9),
         rafia=mk('tras_maxisaco_rafia', (.86, .85, .80), .92), pl_verde=mk('tras_pallet_plastico_verde', (.20, .48, .24), .5))
for k in ('jaba_a', 'jaba_r', 'verde', 'verde_o', 'oxido', 'rafia', 'pl_verde'): G[k] = MB()
for k, src in (('tp_azul', 'pl_azul'), ('tp_rojo', 'pl_rojo'), ('tp_pino', 'pino'), ('tp_verde', 'pl_verde')): M[k] = M[src]; G[k] = MB()   # pallets apilados del patio: sin bisel (rendimiento: ~150 tris por pallet)
ZS0_, ZS1_ = 50.2, 73.3
yPat = lambda z: 0. if z <= ZS0_ else (-1.2 if z >= ZS1_ else -1.2 * (z - ZS0_) / (ZS1_ - ZS0_))
def asentar(fn, z):   # desplaza en altura todo lo que fn agregue (piso en pendiente del patio)
    dy = yPat(z); n0 = {k: len(g.v) for k, g in G.items()}; fn()
    if dy:
        for k, g in G.items():
            for i in range(n0.get(k, 0), len(g.v)): x_, y_, z_ = g.v[i]; g.v[i] = (x_, y_, z_ + dy)
def pallet_vacio(X, Z, ax, y0, g):   # pallet plástico (9 tacos, 3 patines) o de madera, sin carga
    su, sv = (1.2, 1.0) if ax else (1.0, 1.2); B = lambda du, y, dv, a, h, bb, gg: G[gg].box((X + du, y0 + y, Z + dv), (a, h, bb), 0)
    gt = {'pl_azul': 'tp_azul', 'pl_rojo': 'tp_rojo', 'pino': 'tp_pino', 'pl_verde': 'tp_verde'}[g]; madera = g == 'pino'; g = gt
    if madera:
        for k in range(7):
            t = -.55 + k * 1.1 / 6
            if ax: B(t, .133, 0, .1, .022, sv, g)
            else: B(0, .133, t, su, .022, .1, g)
        for k in (-1, 0, 1):
            for j in (-1, 0, 1): B(j * (su / 2 - .05), .061, k * (sv / 2 - .05), .1, .078, .1, g)
            if ax: B(0, .011, k * (sv / 2 - .05), su, .022, .1, g)
            else: B(k * (su / 2 - .05), .011, 0, .1, .022, sv, g)
    else:
        B(0, .135, 0, su, .03, sv, g)
        for i in (-1, 0, 1):
            for j in (-1, 0, 1): B(i * (su / 2 - .07), .075, j * (sv / 2 - .07), .13, .09, .13, g)
        for i in (-1, 0, 1): B(0 if ax else i * (su / 2 - .07), .01, i * (sv / 2 - .07) if ax else 0, su if ax else .13, .02, .13 if ax else sv, g)
def col_pallet():
    r = rnd.random(); return 'pl_azul' if r < .72 else 'pl_rojo' if r < .84 else 'pino' if r < .95 else 'pl_verde'
def torre(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); az = (z1 - z0) >= (x1 - x0); Lg = (z1 - z0) if az else (x1 - x0); W2 = (x1 - x0) if az else (z1 - z0)
    n = max(1, int(Lg // 1.06)); m = max(1, int(W2 // 1.25))
    for i in range(n):
        for q in range(m):
            X = x0 + W2 * (q + .5) / m if az else x0 + Lg * (i + .5) / n; Z = z0 + Lg * (i + .5) / n if az else z0 + W2 * (q + .5) / m; bc = col_pallet(); k = 11 + rnd.randrange(8)
            def pila(X=X, Z=Z, bc=bc, k=k):
                for j in range(k): pallet_vacio(X + (rnd.random() - .5) * .05, Z + (rnd.random() - .5) * .05, not az, j * .15, bc if rnd.random() < .8 else col_pallet())
                sombra(X - .55, X + .55, Z - .55, Z + .55, .2, 'sombra_m')
            asentar(pila, Z)
def bandejas_patio(o, mezcla):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); az = (z1 - z0) >= (x1 - x0); cw, cd, ch = .6, .4, .3
    nx = max(1, int((x1 - x0) // ((cd if az else cw) + .02))); nz = max(1, int((z1 - z0) // ((cw if az else cd) + .02)))
    def f():
        for i in range(nx):
            for k in range(nz):
                X = x0 + (x1 - x0) * (i + .5) / nx; Z = z0 + (z1 - z0) * (k + .5) / nz; g = rnd.choice(mezcla); n = 5 + rnd.randrange(3)
                for j in range(n):
                    gg = g if rnd.random() < .85 else rnd.choice(mezcla)
                    G[gg].box((X + (rnd.random() - .5) * .02, .005 + j * ch + ch / 2, Z + (rnd.random() - .5) * .02), ((cd, ch - .006, cw) if az else (cw, ch - .006, cd)), (rnd.random() - .5) * .025, (0, 0, 1, 1))
        G['film'].box(((x0 + x1) / 2, 1.05, (z0 + z1) / 2), (x1 - x0 + .03, 2.1, z1 - z0 + .03))   # «pila envuelta»
        sombra(x0, x1, z0, z1, .3, 'sombra_f')
    asentar(f, (z0 + z1) / 2)
def jabas_rojas(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); az = (z1 - z0) >= (x1 - x0); Lg = (z1 - z0) if az else (x1 - x0); W2 = (x1 - x0) if az else (z1 - z0)
    n = max(1, int((Lg + .05) // 1.25)); m = max(1, int((W2 + .05) // 1.05))
    for i in range(n):
        for q in range(m):
            X = x0 + W2 * (q + .5) / m if az else x0 + Lg * (i + .5) / n; Z = z0 + Lg * (i + .5) / n if az else z0 + W2 * (q + .5) / m
            def f(X=X, Z=Z):
                pallet_vacio(X, Z, not az, 0, 'pl_azul')
                for a in range(3):
                    for b in range(2):
                        lu, lv = -.4 + a * .4, -.24 + b * .48
                        lx, lz = (lv, lu) if az else (lu, lv)
                        for c in range(4): G['jaba_r'].box((X + lx, .15 + c * .3 + .145, Z + lz), ((.46, .28, .38) if az else (.38, .28, .46)), (rnd.random() - .5) * .03, (0, 0, 1, 1))
                sombra(X - .6, X + .6, Z - .55, Z + .55, .2, 'sombra_m')
            asentar(f, Z)
def carros_super(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); az = (z1 - z0) >= (x1 - x0); Lg = (z1 - z0) if az else (x1 - x0); W2 = (x1 - x0) if az else (z1 - z0)
    nf = max(1, int(W2 // .72)); nc = int((Lg - .7) // .3)
    def P3(u, v, y):   # (u a lo largo de la fila, v transversal) → plano
        return (v, y, u) if az else (u, y, v)
    for f in range(nf):
        v0 = (x0 if az else z0) + W2 * (f + .5) / nf
        for i in range(nc):
            u0 = (z0 if az else x0) + .45 + i * .3; yb = .1
            # canasto de malla: piso, costados y frente (más angosto atrás para encajar)
            pts = lambda du, dv, y: P3(u0 + du, v0 + dv, y)
            for (a, b, c, d) in [((-.42, -.2, .5), (.38, -.27, .5), (.38, -.27, .95), (-.42, -.2, .95)), ((.38, .27, .5), (-.42, .2, .5), (-.42, .2, .95), (.38, .27, .95)),
                                 ((-.42, .2, .5), (-.42, -.2, .5), (-.42, -.2, .95), (-.42, .2, .95)), ((-.42, -.2, .5), (-.42, .2, .5), (.38, .27, .5), (.38, -.27, .5))]:
                q = [pts(*a), pts(*b), pts(*c), pts(*d)]; G['malla'].quad(q, [(0, 0), (4, 0), (4, 2.25), (0, 2.25)]); G['malla'].quad(q[::-1], [(0, 2.25), (4, 2.25), (4, 0), (0, 0)])   # malla fina del canasto (1 u = 0,2 m)
            for dv in (-.27, .27): cil('galv', pts(.38, dv, .5), pts(.38, dv, .95), .008, 6); cil('galv', pts(-.42, dv * .74, .95), pts(.38, dv, .95), .007, 6)
            for dv in (-.24, .24):
                cil('galv', pts(.42, dv, .12), pts(.42, dv, 1.0), .011, 8); cil('galv', pts(-.38, dv * .8, .12), pts(.42, dv, .12), .011, 8)
                for du in (-.34, .36): cil('rueda', pts(du, dv * (.8 if du < 0 else 1), .06), pts(du, dv * (.8 if du < 0 else 1) + .03, .06), .055, 12)
            cil('pl_azul2', pts(.47, -.26, 1.0), pts(.47, .26, 1.0), .018, 10)   # manilla azul
        u_mid = (z0 + z1) / 2 if az else (x0 + x1) / 2
    sombra(x0, x1, z0, z1, .25, 'sombra_m')
def contenedor(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); az = (z1 - z0) >= (x1 - x0)
    def f():
        a0, a1, b0, b1 = x0 + .05, x1 - .05, z0 + .05, z1 - .05; H = 2.45; yb = .25
        # tolva: costados inclinados hacia afuera arriba (contenedor de gancho), piso, frente y puerta trasera
        dz = .12
        Wl = lambda y: dz * (y - yb) / (H - yb)
        if az:
            for sx, xx in ((-1, a0), (1, a1)):
                q = [(xx, yb, b0), (xx, yb, b1), (xx + sx * Wl(H), H, b1), (xx + sx * Wl(H), H, b0)]; G['verde'].quad(q if sx > 0 else q[::-1], [(0, 0), (b1 - b0, 0), (b1 - b0, H), (0, H)]); G['verde'].quad(q[::-1] if sx > 0 else q, [(0, 0), (b1 - b0, 0), (b1 - b0, H), (0, H)])
            for zz in (b0, b1): G['verde'].box(((a0 + a1) / 2, (yb + H) / 2, zz), (a1 - a0 + .25, H - yb, .05))
            for u in [b0 + .5 + k * .7 for k in range(int((b1 - b0 - .6) // .7) + 1)]:
                for sx, xx in ((-1, a0), (1, a1)): G['verde_o'].box((xx + sx * .05, (yb + H) / 2 + .1, u), (.07, H - yb - .2, .09))
            for sx, xx in ((-1, a0), (1, a1)): G['verde_o'].box((xx + sx * (dz + .03), H - .05, (b0 + b1) / 2), (.1, .1, b1 - b0 + .1))
            for xr in (a0 + .35, a1 - .35): G['pl_negro'].box((xr, yb / 2, (b0 + b1) / 2), (.14, yb, b1 - b0 - .2))
            for zz in (b0 + .3, b1 - .3):
                for xr in (a0 + .35, a1 - .35): cil('maq', (xr - .1, .12, zz), (xr + .1, .12, zz), .12, 14)
            G['verde_o'].box(((a0 + a1) / 2, 1.4, b1 + .25), (.12, 1.8, .08)); G['verde_o'].box(((a0 + a1) / 2, 2.25, b1 + .15), (.12, .12, .3))   # gancho
            G['verde_o'].box(((a0 + a1) / 2, (yb + H) / 2, b0 - .04), (.03, H - yb - .1, .02))
            for y in (.7, 1.4, 2.1):
                for s in (-1, 1): G['pl_negro'].box(((a0 + a1) / 2 + s * (a1 - a0) * .42, y, b0 - .05), (.1, .14, .04))
            G['oxido'].box(((a0 + a1) / 2, yb + .02, (b0 + b1) / 2), (a1 - a0 - .05, .04, b1 - b0 - .05))
            for k in range(150):   # cartón aplastado sobre el borde
                x = a0 + .2 + rnd.random() * (a1 - a0 - .4); z = b0 + .3 + rnd.random() * (b1 - b0 - .6); y = H - .35 + rnd.random() * .55
                caja((x, y, z), (.4 + rnd.random() * .6, .015 + rnd.random() * .02, .3 + rnd.random() * .5), rnd.random() * 6.28, 0)
        sombra(x0, x1, z0, z1, .35, 'sombra_f')
    asentar(f, (z0 + z1) / 2)
def maxisacos(o):
    x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z']); nx = max(1, int((x1 - x0) // 1.0)); nz = max(1, int((z1 - z0) // 1.0))
    def f():
        for i in range(nx):
            for k in range(nz):
                X = x0 + (x1 - x0) * (i + .5) / nx; Z = z0 + (z1 - z0) * (k + .5) / nz; h = .8 + rnd.random() * .25
                pallet_vacio(X, Z, True, 0, 'pino') if rnd.random() < .5 else None; y0 = .15
                G['rafia'].box((X, y0 + h / 2, Z), (.9, h, .9), (rnd.random() - .5) * .2); G['rafia'].box((X, y0 + h + .04, Z), (.8, .08, .8), 0)
                for (a, c) in [(-.42, -.42), (.42, -.42), (-.42, .42), (.42, .42)]: cil('rafia', (X + a, y0 + h - .05, Z + c), (X + a * .8, y0 + h + .22, Z + c * .8), .02, 6)
        sombra(x0, x1, z0, z1, .25, 'sombra_m')
    asentar(f, (z0 + z1) / 2)
for o in PATIO:
    t, nm = o['tipo'], o.get('nombre', '').lower()
    if t == 'torre_pallets' or (t == 'pallets' and 'torre' in nm): torre(o)
    elif t == 'pallets' and 'bandeja' in nm: bandejas_patio(o, ['jaba_g', 'jaba_n', 'jaba_a', 'jaba_g', 'jaba_n'])
    elif t == 'pallets': asentar(lambda o=o: (linea(o, True), sombra(min(o['x']), max(o['x']), min(o['z']), max(o['z']), .3, 'sombra_f')), sum(o['z']) / 2)
    elif t == 'jabas': jabas_rojas(o)
    elif t == 'carros' and 'bici' not in nm: carros_super(o)
    elif t == 'contenedor': contenedor(o)
    elif t == 'maxisaco': maxisacos(o)
# ---- v83 (auditoría): los pallets azules de recepción y del vestíbulo estaban ocultos (regla del kit) y sus cajas quedaban flotando a 14 cm:
#      fila de pallets plásticos azules contra el muro norte de recepción (posiciones del simulador; carga en 1 de cada 3) y 2 pallets cargados en el vestíbulo
for k, x in enumerate([-59.45, -60.7, -61.95, -63.2, -64.45, -65.7, -68.45, -69.7, -70.95]):
    if k % 3 == 2: pallet((x, 81.95), True, carga_max=1.9, wrap=True, plast=True)
    else:
        pallet_vacio(x, 81.95, True, 0, 'pl_azul')
        if rnd.random() < .5: pallet_vacio(x + (rnd.random() - .5) * .04, 81.95 + (rnd.random() - .5) * .04, True, .15, 'pl_azul')
    sombra(x - .6, x + .6, 81.45, 82.45, .2, 'sombra_m')
linea({'x': [-5.8, -4.75], 'z': [6.25, 8.75]}, True); sombra(-5.8, -4.75, 6.25, 8.75, .25, 'sombra_f')
# ---- sombras de contacto (fotos: el piso se oscurece bajo los racks, pallets y en la base de las cámaras) ----
for o in MAP:
    t = o['tipo']; x0, x1 = sorted(o['x']); z0, z1 = sorted(o['z'])
    if t == 'rack': sombra(x0, x1, z0, z1, .35, 'sombra_f'); sombra(x0 + .25, x1 - .25, z0 + .25, z1 - .25, .2, 'sombra_m', .005)
    elif t in ('pallets', 'cajas') and not re.search('torre|vac', o.get('nombre', ''), re.I): sombra(x0, x1, z0, z1, .3, 'sombra_f')
    elif t == 'camara' and not re.search('recicl', o.get('nombre', ''), re.I): sombra(x0, x1, z0, z1, .4, 'sombra_l')
    elif t in ('tablero', 'jaula', 'lavamanos', 'repisa'): sombra(x0, x1, z0, z1, .25, 'sombra_l')
BEV = {'panel': 0, 'zocalo': .003, 'remate': .004, 'baranda': .004, 'franjas': 0, 'canal': .003, 'jaba_n': .01, 'jaba_g': .01, 'gas': .005, 'br_w': .002, 'br_c': .002, 'br_b': .002, 'mont_w': .003, 'mont_c': .003, 'mont_b': .003, 'viga': .006, 'viga_w': .006, 'galv': .002, 'deck': .003, 'carton': .006, 'pino': .004, 'pl_azul': .008, 'pl_rojo': .008, 'bandeja': .006, 'carro': .004, 'inox': .003, 'inox_sat': .002, 'abs_bl': .01, 'abs_gr': .002, 'goma': .002, 'pl_rojo2': .01, 'pl_negro': .006, 'pl_amar': .01, 'pl_azul2': .008, 'pl_gris': .006, 'maq': .025, 'ral': .004, 'tela_n': .02, 'tela_az': .02, 'chaleco': .01, 'refl': 0, 'agua': .004, 'madera_m': .002, 'jaba_a': .01, 'jaba_r': .01, 'verde': .004, 'verde_o': .004, 'oxido': 0, 'rafia': .05, 'pl_verde': .008}
objs = []
for k, mb in G.items():
    o = mb.obj('tras_' + k, M[k], BEV.get(k, 0.), wn=k not in ('film', 'malla', 'sombra_f', 'sombra_m', 'sombra_l', 'panel', 'techo_cam') and not k.startswith('cab_'))
    if o: objs.append(o)
tris = 0
for o in objs:
    dg = bpy.context.evaluated_depsgraph_get(); e = o.evaluated_get(dg); tris += sum(len(p.vertices) - 2 for p in e.data.polygons)
kw = dict(filepath=OUT, export_format='GLB', export_apply=True, export_yup=True, export_image_format='WEBP')
try: bpy.ops.export_scene.gltf(**kw, export_vertex_color='ACTIVE')
except TypeError: bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(D, 'tras_v78.blend'))
result = {'objs': len(objs), 'tris': tris, 'glb': os.path.getsize(OUT)}
print(result)
