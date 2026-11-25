# build_plano.py — Modelo completo del Líder San Felipe generado desde el plano por capas (plano_final.json)
# Plano: x → Riquelme, y arriba, z → O'Higgins (metros). Blender: X=x, Y=-z, Z=y.
# Texturas: fotográficas CC0 a 2K (ambientCG / Poly Haven) + propias, en techo_blender\tex2k.
# v76: lee plano_final2.json (pilares como en el simulador, vigas con quiebre, red húmeda nueva) y agrega detalle: nervios de chapa,
# juntas de membrana, perfiles C, tensores, cartelas, placas base, canaletas con soportes, equipos detallados, red húmeda completa.
import bpy, math, os, json, re
from mathutils import Vector

BASE = r"C:\Users\eliza\Desktop\Cowork\Proyect 3D"
TB = os.path.join(BASE, "techo_blender")
TX = os.path.join(TB, "tex2k")
PLANO = json.load(open(os.path.join(TB, "plano_final2.json"), encoding="utf-8"))
OUT_GLB = os.path.join(TB, "edificio_plano.glb")
OUT_BLEND = os.path.join(TB, "edificio_plano.blend")

# ---------------- cotas del techo principal ----------------
EAVE, RIDGE, XR, XW, XE, Z0, ZF = 7.55, 9.68, -13.55, -59.2, 39.8, 1.5, 74.0
def top(x):
    if x <= XR: return EAVE + (min(max(x, XW), XR) - XW) * (RIDGE - EAVE) / (XR - XW)
    return RIDGE - (min(x, XE) - XR) * (RIDGE - EAVE) / (XE - XR)
N2 = (-59.2, -46.4, 18.2, 69.0)                     # 2º nivel (x0, x1, z0, z1)
def roof2(x): return 10.4 - (x - N2[0]) * 0.4 / (N2[1] - N2[0])

def V(p): return Vector((p[0], -p[2], p[1]))
O = PLANO
by_t = lambda *t: [o for o in O if o["t"] in t]

def inpoly(x, z, P):
    c = False
    for i in range(len(P)):
        (xi, zi), (xj, zj) = P[i], P[i - 1]
        if (zi > z) != (zj > z) and x < (xj - xi) * (z - zi) / (zj - zi) + xi: c = not c
    return c
def cota(o, d=None):
    m = re.findall(r"[\d]+[,.]?\d*", (o.get("cota") or "").replace("≈", ""))
    return float(m[-1].replace(",", ".")) if m else d
ROOFS = [o for o in by_t("agua", "plana") if o["L"] == "techo"]
MAIN = [o for o in ROOFS if o["t"] == "agua" and o.get("cae") in (0, 180) and "2º nivel" not in o["n"]]
def roofY(x, z, cubiertas_bajas=True):
    """altura de la cara inferior de la cubierta en (x,z); None si al aire libre"""
    for o in MAIN:
        if inpoly(x, z, o["p"]): return top(x)
    for o in ROOFS:
        if o["t"] == "plana" and inpoly(x, z, o["p"]): return cota(o, 7.55)
    return None
def techado(x, z):
    return any(inpoly(x, z, o["p"]) for o in ROOFS if not re.search("alero|malla|escaleras", o["n"], re.I))

# ---------------- escena ----------------
bpy.ops.wm.read_homefile(use_empty=True)
scn = bpy.context.scene; scn.unit_settings.system = "METRIC"

# ---------------- materiales ----------------
MATS = {}
def img(n):
    p = os.path.join(TX, n + ".webp")
    if not os.path.exists(p): raise RuntimeError("falta textura " + p)
    return bpy.data.images.load(p, check_existing=True)
def mk(name, color=(0.8, 0.8, 0.8), rough=0.7, metal=0.0, diff=None, nrm=None, nstr=0.6, emis=None, estr=1.0, alpha=None, tr=0.0):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*color, 1); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if diff:
        t = nt.nodes.new("ShaderNodeTexImage"); t.image = img(diff); nt.links.new(t.outputs["Color"], b.inputs["Base Color"])
        if alpha == "clip":
            rn = nt.nodes.new("ShaderNodeMath"); rn.operation = "ROUND"; nt.links.new(t.outputs["Alpha"], rn.inputs[0]); nt.links.new(rn.outputs[0], b.inputs["Alpha"])
    if nrm:
        t2 = nt.nodes.new("ShaderNodeTexImage"); t2.image = img(nrm); t2.image.colorspace_settings.name = "Non-Color"
        nm = nt.nodes.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = nstr
        nt.links.new(t2.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs["Normal"], b.inputs["Normal"])
    if emis: b.inputs["Emission Color"].default_value = (*emis, 1); b.inputs["Emission Strength"].default_value = estr
    if tr:
        b.inputs["Alpha"].default_value = 1 - tr
        for at, v in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try: setattr(m, at, v)
            except Exception: pass
    MATS[name] = m; return m
M = dict(
  panel=mk("panel_hormigon", rough=0.85, diff="panel_hormigon_diff", nrm="panel_hormigon_norm", nstr=0.7),
  estuco=mk("estuco_arena", rough=0.9, diff="estuco_arena_diff", nrm="estuco_norm", nstr=0.5),
  estgris=mk("estuco_gris", rough=0.9, diff="estuco_gris_diff", nrm="estuco_norm", nstr=0.5),
  pint=mk("pintura_interior", rough=0.85, diff="pintura_interior_diff", nrm="pintura_norm", nstr=0.25),
  ladr=mk("ladrillo_octogono", rough=0.85, diff="ladrillo_diff", nrm="ladrillo_norm", nstr=0.6),
  acero=mk("acero_blanco", rough=0.45, metal=0.3, diff="acero_pintado_diff", nrm="metal_norm", nstr=0.2),
  galv=mk("acero_galv", rough=0.35, metal=0.75, diff="galvanizado_diff", nrm="metal_norm", nstr=0.3),
  chapa=mk("chapa_techo", rough=0.4, metal=0.45, diff="chapa_diff", nrm="chapa_norm", nstr=0.8),
  memb=mk("membrana_techo", rough=0.85, diff="membrana_diff", nrm="membrana_norm", nstr=0.5),
  plano=mk("techo_plano", rough=0.85, diff="membrana_diff", nrm="membrana_norm", nstr=0.4),
  trasl=mk("tragaluz_techo", rough=0.25, diff="traslucido_diff", nrm="chapa_norm", nstr=0.6, emis=(1, 0.97, 0.9), estr=0.25),
  deck=mk("deck_interior", rough=0.6, metal=0.2, diff="deck_diff", nrm="deck_norm", emis=(1, 1, 1), estr=0.1),
  cielo=mk("cielo_modular", rough=0.9, diff="cielo_modular_diff"),
  list=mk("listones_alero", rough=0.7, diff="listones_diff", nrm="listones_norm", nstr=0.5),
  vidrio=mk("vidrio_local", color=(0.10, 0.13, 0.14), rough=0.04, metal=0.25, tr=0.72),   # v77: vitrina transparente (fotos: se ve la mercadería)
  vidrioc=mk("vidrio_caseta", color=(0.55, 0.65, 0.68), rough=0.05, metal=0.2, tr=0.55),
  marco=mk("marco_aluminio", color=(0.12, 0.12, 0.13), rough=0.35, metal=0.8),
  negro=mk("metal_negro", color=(0.035, 0.035, 0.04), rough=0.45, metal=0.5),
  ledc=mk("led_carcasa", color=(0.78, 0.79, 0.8), rough=0.35, metal=0.6),
  led=mk("led_sala", color=(1, 1, 1), rough=0.3, emis=(0.96, 0.98, 1.0), estr=4.0),
  down=mk("led_downlight", color=(1, 1, 1), rough=0.3, emis=(1.0, 0.96, 0.9), estr=5.0),
  ledal=mk("led_alero", color=(1, 1, 1), emis=(1, 0.95, 0.88), estr=3.0),
  letr=mk("letrero_luz", color=(1, 1, 1), emis=(1, 1, 1), estr=3.5),
  letrf=mk("letrero_fondo", color=(0.05, 0.12, 0.3), rough=0.4),
  rejilla=mk("bandeja_rejilla", rough=0.4, metal=0.6, diff="rejilla_diff", alpha="clip"),
  hvac=mk("hvac_galv", color=(0.72, 0.73, 0.72), rough=0.45, metal=0.6, diff="galvanizado_diff", nrm="metal_norm", nstr=0.3),
  vent=mk("ventilador_negro", color=(0.05, 0.05, 0.05), rough=0.6),
  ducto=mk("ducto_galv", rough=0.35, metal=0.7, diff="galvanizado_diff", nrm="metal_norm", nstr=0.4),
  asf=mk("asfalto_estac", rough=0.95, diff="asfalto_diff", nrm="asfalto_norm", nstr=0.6),
  acera=mk("acera_frente", rough=0.9, diff="acera_diff", nrm="acera_norm", nstr=0.6),
  linea=mk("linea_blanca", color=(0.9, 0.9, 0.86), rough=0.7),
  horm=mk("hormigon_rampa", color=(0.6, 0.6, 0.58), rough=0.9, diff="acera_diff", nrm="acera_norm", nstr=0.3),
  rampa=mk("rampa_oscura", color=(0.08, 0.08, 0.08), rough=0.9),
  pasto=mk("pasto_jardin", color=(0.16, 0.27, 0.1), rough=0.95),
  arbusto=mk("arbusto", color=(0.12, 0.25, 0.08), rough=0.9),
  malla=mk("malla_raschel", rough=0.9, diff="malla_diff", alpha="clip"),
  losainf=mk("losa_inferior_2nivel", color=(0.42, 0.42, 0.40), rough=0.92, diff="acera_diff", nrm="acera_norm", nstr=0.35),
  pvc_neg=mk("conduit_negro", color=(0.03, 0.03, 0.03), rough=0.5),
  pvc_bco=mk("tubo_blanco", color=(0.80, 0.80, 0.78), rough=0.45),
  horm2=mk("hormigon_losa", color=(0.62, 0.62, 0.6), rough=0.9, diff="acera_diff", nrm="acera_norm", nstr=0.25),
  escalon=mk("escalon_metal", color=(0.35, 0.36, 0.37), rough=0.4, metal=0.7, diff="galvanizado_diff"),
  pilarh=mk("pilar_hormigon", color=(0.86, 0.85, 0.82), rough=0.92, diff="pilar_hormigon_diff", nrm="pilar_hormigon_norm", nstr=0.5),
  pilarp=mk("pilar_pintura_base", rough=0.88, diff="pilar_pintura_diff", nrm="pintura_norm", nstr=0.2),
  rojo_ext=mk("extintor_rojo", color=(0.55, 0.02, 0.02), rough=0.35, metal=0.1),
  letrero_rojo=mk("letrero_extintor", color=(0.62, 0.04, 0.03), rough=0.5),
  letrero_verde=mk("letrero_salida", color=(0.02, 0.36, 0.12), rough=0.5),
  muro_osc=mk("muro_cierre_oscuro", color=(0.10, 0.105, 0.11), rough=0.9, diff="pintura_interior_diff", nrm="pintura_norm", nstr=0.25),
  mbruto=mk("muro_bruto_blanco", rough=0.9, diff="muro_bruto_diff", nrm="pilar_hormigon_norm", nstr=0.35),
  mgris=mk("muro_franja_gris", rough=0.88, diff="muro_gris_diff", nrm="pilar_hormigon_norm", nstr=0.3),
  amarillo=mk("pintura_amarilla", color=(0.80, 0.55, 0.04), rough=0.6),
  rojo=mk("canieria_roja", color=(0.55, 0.035, 0.025), rough=0.4, metal=0.15),
  bronce=mk("rociador_bronce", color=(0.75, 0.55, 0.25), rough=0.35, metal=0.9),
  letrb=mk("letra_blanca", color=(0.92, 0.92, 0.9), rough=0.5),
  puerta=mk("puerta_metal", color=(0.42, 0.44, 0.46), rough=0.5, metal=0.4, diff="acero_pintado_diff", nrm="metal_norm", nstr=0.2),
  cable=mk("cable_negro", color=(0.025, 0.025, 0.028), rough=0.6),
  aislante=mk("aislante_negro", color=(0.04, 0.04, 0.04), rough=0.85),
  listc=mk("listones_oscuro", rough=0.62, diff="listones_oscuro_diff", nrm="listones_norm", nstr=0.4),
  faja=mk("faja_alero", color=(0.12, 0.115, 0.11), rough=0.42, metal=0.35),
  vitri=mk("vitrina_interior", rough=0.8, diff="vitrina_interior_diff"),
  chapav=mk("chapa_muro_patio", rough=0.45, metal=0.55, diff="chapa_oscura_diff", nrm="chapa_norm", nstr=0.9),   # fotos patio: chapa ondulada vertical gris oscuro
  colneg=mk("columna_negra", color=(0.03, 0.03, 0.032), rough=0.4, metal=0.6),
)
# tamaño de baldosa UV (u, v) en metros por material
UVT = {"losa_inferior_2nivel": (3, 3), "pilar_hormigon": (1.2, 1.2), "pilar_pintura_base": (1, 1), "muro_cierre_oscuro": (2, 2), "muro_bruto_blanco": (2.4, 2.4), "muro_franja_gris": (2.4, 0.9), "extintor_rojo": (1, 1), "letrero_extintor": (1, 1), "letrero_salida": (1, 1), "pintura_amarilla": (1, 1), "conduit_negro": (1, 1), "tubo_blanco": (1, 1), "panel_hormigon": (4.0, 2.5), "estuco_arena": (3, 3), "estuco_gris": (3, 3), "pintura_interior": (3, 3), "ladrillo_octogono": (1.2, 1.2),
       "chapa_techo": (2.5, 2.5), "membrana_techo": (6, 6), "techo_plano": (6, 6), "tragaluz_techo": (2.5, 2.5), "deck_interior": (2.5, 2.5),
       "cielo_modular": (2.4, 2.4), "listones_alero": (1.5, 1.5), "listones_oscuro": (1.2, 1.2), "vitrina_interior": (6.0, 3.0), "faja_alero": (2, 2), "columna_negra": (1, 1), "chapa_muro_patio": (2.0, 2.0), "asfalto_estac": (5, 5), "acera_frente": (2.5, 2.5), "hormigon_rampa": (2.5, 2.5),
       "hormigon_losa": (3, 3), "bandeja_rejilla": (0.5, 0.5), "malla_raschel": (1, 1), "acero_blanco": (2, 2), "acero_galv": (2, 2),
       "hvac_galv": (1.5, 1.5), "ducto_galv": (1.5, 1.5), "escalon_metal": (1, 1)}

ONDA = {"chapa_techo", "tragaluz_techo", "deck_interior"}
# ---------------- grupos ----------------
GROUPS = {}
def group(name):
    if name in GROUPS: return GROUPS[name]
    col = bpy.data.collections.new(name); scn.collection.children.link(col)
    e = bpy.data.objects.new("G_" + name, None); col.objects.link(e); GROUPS[name] = (col, e); return GROUPS[name]

def newell(pts):
    n = [0.0, 0.0, 0.0]
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n[0] += (a[1] - b[1]) * (a[2] + b[2]); n[1] += (a[2] - b[2]) * (a[0] + b[0]); n[2] += (a[0] - b[0]) * (a[1] + b[1])
    return n
class MB:
    def __init__(s, name, grp): s.name, s.grp = name, grp; s.v, s.f, s.uv, s.mi, s.mats = [], [], [], [], []
    def face(s, pts, m, nrm=None, uvs=None):
        n = newell(pts)
        if nrm is not None and n[0] * nrm[0] + n[1] * nrm[1] + n[2] * nrm[2] < 0:
            pts = pts[::-1]; n = [-c for c in n]; uvs = uvs[::-1] if uvs else None
        if m not in s.mats: s.mats.append(m)
        tu, tv = UVT.get(m.name, (1.0, 1.0)); ax = max(range(3), key=lambda i: abs(n[i]))
        if uvs is None:
            uvs = []
            for p in pts:
                if ax == 1: u, w = (p[2], p[0]) if m.name in ONDA else (p[0], p[2])   # ondas de la chapa siguen la pendiente (x)
                elif ax == 0: u, w = p[2], p[1]
                else: u, w = p[0], p[1]
                uvs.append((u / tu, w / tv))
        i0 = len(s.v); s.v += list(pts); s.f.append(list(range(i0, i0 + len(pts)))); s.uv.append(uvs); s.mi.append(s.mats.index(m))
    def box(s, x0, x1, y0, y1, z0, z1, m, skip=(), mtop=None):
        x0, x1 = sorted((x0, x1)); y0, y1 = sorted((y0, y1)); z0, z1 = sorted((z0, z1))
        F = {"+y": ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0)), "-y": ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0)),
             "+x": ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0)), "-x": ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], (-1, 0, 0)),
             "+z": ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1)), "-z": ([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1))}
        for k, (pts, nn) in F.items():
            if k not in skip: s.face(pts, mtop if (k == "+y" and mtop) else m, nn)
    def seg(s, p0, p1, w, h, m, up=(0, 1, 0)):
        d = Vector(p1) - Vector(p0)
        if d.length < 1e-4: return
        d.normalize(); side = d.cross(Vector(up))
        if side.length < 1e-4: side = Vector((1, 0, 0))
        side.normalize(); u2 = side.cross(d).normalized()
        A, B = Vector(p0), Vector(p1); hw, hh = side * (w / 2), u2 * (h / 2)
        c = [tuple(v) for v in [A - hw - hh, A + hw - hh, A + hw + hh, A - hw + hh, B - hw - hh, B + hw - hh, B + hw + hh, B - hw + hh]]; ctr = (A + B) / 2
        for idx in [(0, 1, 2, 3), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]:
            pts = [c[i] for i in idx]; s.face(pts, m, tuple(sum((Vector(p) for p in pts), Vector()) / 4 - ctr))
    def ibeam(s, p0, p1, D, m, bf=0.22, tf=0.025, tw=0.014):
        d = (Vector(p1) - Vector(p0))
        if d.length < 1e-4: return
        d.normalize(); side = d.cross(Vector((0, 1, 0)))
        if side.length < 1e-4: side = Vector((1, 0, 0))
        side.normalize(); u2 = side.cross(d).normalized()
        for off, w, h in [((D - tf) / 2, bf, tf), (-(D - tf) / 2, bf, tf), (0, tw, D - 2 * tf)]:
            o = u2 * off; s.seg(tuple(Vector(p0) + o), tuple(Vector(p1) + o), w, h, m)
    def cyl(s, p0, p1, r, m, n=8):
        d = (Vector(p1) - Vector(p0))
        if d.length < 1e-4: return
        d.normalize(); a = Vector((0, 1, 0)) if abs(d.y) < 0.9 else Vector((1, 0, 0))
        u = d.cross(a).normalized(); w = d.cross(u).normalized()
        ring = lambda c: [tuple(Vector(c) + (u * math.cos(2 * math.pi * k / n) + w * math.sin(2 * math.pi * k / n)) * r) for k in range(n)]
        r0, r1 = ring(p0), ring(p1); ctr = (Vector(p0) + Vector(p1)) / 2
        for k in range(n):
            pts = [r0[k], r0[(k + 1) % n], r1[(k + 1) % n], r1[k]]; s.face(pts, m, tuple(sum((Vector(p) for p in pts), Vector()) / 4 - ctr))
    def disk(s, c, r, m, up=True, n=12):
        x, y, z = c; s.face([(x + r * math.cos(2 * math.pi * k / n), y, z + r * math.sin(2 * math.pi * k / n)) for k in range(n)], m, (0, 1 if up else -1, 0))
    def cprof(s, p0, p1, D, B, m, t=0.004):
        """perfil C (costanera): alma + alas"""
        d = Vector(p1) - Vector(p0)
        if d.length < 1e-4: return
        d.normalize(); side = d.cross(Vector((0, 1, 0)))
        if side.length < 1e-4: side = Vector((1, 0, 0))
        side.normalize(); u2 = side.cross(d).normalized()
        A, Bv = Vector(p0), Vector(p1)
        o = side * (-B / 2); s.seg(tuple(A + o), tuple(Bv + o), t, D, m)
        for sg in (1, -1):
            o = u2 * (sg * (D / 2 - t / 2)); s.seg(tuple(A + o), tuple(Bv + o), B, t, m)
            o2 = side * (B / 2) + u2 * (sg * (D / 2 - .01)); s.seg(tuple(A + o2), tuple(Bv + o2), t, .02, m)
    def poly(s, P, y, m, up=True):
        s.face([(x, y, z) for x, z in P], m, (0, 1 if up else -1, 0))
    def slab(s, P, y0, y1, mt, mb=None, ms=None):
        s.poly(P, y1, mt, True); s.poly(P, y0, mb or mt, False)
        cx = sum(p[0] for p in P) / len(P); cz = sum(p[1] for p in P) / len(P)
        for i in range(len(P)):
            a, b = P[i], P[(i + 1) % len(P)]; nx, nz = b[1] - a[1], -(b[0] - a[0])
            if nx * ((a[0] + b[0]) / 2 - cx) + nz * ((a[1] + b[1]) / 2 - cz) < 0: nx, nz = -nx, -nz
            s.face([(a[0], y0, a[1]), (b[0], y0, b[1]), (b[0], y1, b[1]), (a[0], y1, a[1])], ms or mt, (nx, 0, nz))
    def build(s):
        if not s.f: return None
        me = bpy.data.meshes.new(s.name); me.from_pydata([tuple(V(p)) for p in s.v], [], s.f)
        for m in s.mats: me.materials.append(m)
        for i, p in enumerate(me.polygons): p.material_index = s.mi[i]
        uvl = me.uv_layers.new(name="UVMap")
        for i, p in enumerate(me.polygons):
            for k, l in enumerate(p.loop_indices): uvl.data[l].uv = s.uv[i][k]
        me.validate(); me.update()
        ob = bpy.data.objects.new(s.name, me); col, e = group(s.grp); col.objects.link(ob); ob.parent = e; return ob

def letrero(txt, c, normal, size, grp="Frontis", mat=None):
    cu = bpy.data.curves.new("txt", "FONT"); cu.body = txt; cu.size = size; cu.extrude = 0.025; cu.align_x = "CENTER"; cu.align_y = "CENTER"
    tmp = bpy.data.objects.new("tmp", cu); scn.collection.objects.link(tmp)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg)); bpy.data.objects.remove(tmp); bpy.data.curves.remove(cu)
    me.materials.clear(); me.materials.append(mat or M["letr"])
    ob = bpy.data.objects.new("letrero_" + re.sub(r"\W+", "_", txt.lower())[:30], me); col, e = group(grp); col.objects.link(ob); ob.parent = e
    ob.location = V(c); bx, by = normal[0], -normal[1]
    ob.rotation_euler = (math.radians(90), 0, math.atan2(by, bx) - math.atan2(-1, 0)); return ob

def scan(P, z):
    """intervalos en x del polígono P sobre la línea z"""
    xs = []
    for i in range(len(P)):
        (xi, zi), (xj, zj) = P[i], P[i - 1]
        if (zi > z) != (zj > z): xs.append(xi + (z - zi) * (xj - xi) / (zj - zi))
    xs.sort(); return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
def restar(iv, cortes):
    out = []
    for a, b in iv:
        segs = [(a, b)]
        for c0, c1 in cortes:
            nu = []
            for p, q in segs:
                if c1 <= p or c0 >= q: nu.append((p, q))
                else:
                    if c0 > p: nu.append((p, c0))
                    if c1 < q: nu.append((c1, q))
            segs = nu
        out += segs
    return [(p, q) for p, q in out if q - p > .05]
def fan(P):
    return [[P[0], P[i], P[i + 1]] for i in range(1, len(P) - 1)]
CHAPA_X0 = XR   # el faldón poniente es chapa, el oriente membrana (foto aérea)

# =====================================================================
# 1) MUROS (dos caras: exterior según el plano, interior pintado)
# =====================================================================
def zona_bruta(x, z):
    return (z < 12.2 and x > -6.5) or x < -52.0 or z < 4.9 or (z > 73.0 and x < -58.0)
G = "Frontis"; mw = MB("muros_edificio", G); mr = MB("rejas", G)
STREET = 8.2      # altura del muro perimetral de calle (panel de hormigón)
def face_type(o):
    L = math.hypot(o["x2"] - o["x1"], o["z2"] - o["z1"]) or 1; nx, nz = (o["z2"] - o["z1"]) / L, -(o["x2"] - o["x1"]) / L
    mx, mz = (o["x1"] + o["x2"]) / 2, (o["z1"] + o["z2"]) / 2; d = o.get("e", .25) / 2 + .5
    ex = o.get("ext", "auto")
    if ex == "lado A": return "ext", "int", nx, nz
    if ex == "lado B": return "int", "ext", nx, nz
    if ex == "ambas": return "ext", "ext", nx, nz
    if ex == "ninguna": return "int", "int", nx, nz
    a, b = techado(mx + nx * d, mz + nz * d), techado(mx - nx * d, mz - nz * d)
    return ("int" if a else "ext"), ("int" if b else "ext"), nx, nz
def ext_mat(o, side_ext):
    ce = (o.get("cara_ext") or "").lower()
    if "panel" in ce: return M["panel"]
    if o["n"] == "Octágono" or "distinto" in ce: return M["ladr"]
    if (o["n"] == "Cuerpo principal" and abs(o["x1"] + 59.2) < .05 and abs(o["x2"] + 59.2) < .05) or (o["n"] == "Recepción" and abs(o["z1"] - 73.3) < .05):
        return M["chapav"]                                                                   # caras hacia el patio (fotos patio/muro quedivide…)
    mz = (o["z1"] + o["z2"]) / 2
    if mz < 82 or o["n"].startswith("Cierre patio"): return M["panel"]
    return M["estuco"]
def int_face(A_, B_, ha, hb, nrm, ua, ub):   # v80: cara interior de muro en bodega/trastienda = hormigón en bruto pintado, franja gris de 0,9 m (como los muros de la bodega)
    mw.face([(A_[0], 0, A_[1]), (B_[0], 0, B_[1]), (B_[0], .9, B_[1]), (A_[0], .9, A_[1])], M["mgris"], nrm, [(ua / 2.4, 0), (ub / 2.4, 0), (ub / 2.4, 1), (ua / 2.4, 1)])
    mw.face([(A_[0], .9, A_[1]), (B_[0], .9, B_[1]), (B_[0], hb, B_[1]), (A_[0], ha, A_[1])], M["mbruto"], nrm, [(ua / 2.4, .9 / 2.4), (ub / 2.4, .9 / 2.4), (ub / 2.4, hb / 2.4), (ua / 2.4, ha / 2.4)])
for o in by_t("muro"):
    x1, z1, x2, z2, e = o["x1"], o["z1"], o["x2"], o["z2"], max(o.get("e", .25), .12)
    L = math.hypot(x2 - x1, z2 - z1)
    if L < .05: continue
    if o.get("k") == "reja":
        h = o.get("h", 1.6); n = max(1, int(L / 2.5))
        for i in range(n + 1):
            t = i / n; px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t; mr.box(px - .04, px + .04, 0, h, pz - .04, pz + .04, M["galv"])
        ux, uz = (x2 - x1) / L, (z2 - z1) / L
        mr.face([(x1, .1, z1), (x2, .1, z2), (x2, h - .05, z2), (x1, h - .05, z1)], M["rejilla"], None, [(0, 0), (L / .5, 0), (L / .5, (h - .15) / .5), (0, (h - .15) / .5)])
        mr.face([(x1, .1, z1), (x1, h - .05, z1), (x2, h - .05, z2), (x2, .1, z2)], M["rejilla"], None, [(0, 0), (0, (h - .15) / .5), (L / .5, (h - .15) / .5), (L / .5, 0)])
        continue
    fa, fb, nx, nz = face_type(o)
    # esquinas cerradas: cada extremo se prolonga medio espesor
    ux_, uz_ = (x2 - x1) / L, (z2 - z1) / L; x1, z1, x2, z2 = x1 - ux_ * e / 2, z1 - uz_ * e / 2, x2 + ux_ * e / 2, z2 + uz_ * e / 2; L += e
    # altura: muros bajo cubierta llegan a la cubierta (+ antepecho si dan al exterior)
    nseg = max(1, int(L / 2.0)); xs = []
    for i in range(nseg + 1):
        t = i / nseg; px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t; d = e / 2 + .6
        r = [roofY(px + nx * d, pz + nz * d), roofY(px - nx * d, pz - nz * d)]; r = [v for v in r if v is not None]
        street = "panel" in (o.get("cara_ext") or "").lower()
        if r:
            ytop = max(r) + (0.65 if "ext" in (fa, fb) else 0.0)
            if street: ytop = max(ytop, STREET)
        else: ytop = STREET if street else o.get("h", 3)
        xs.append((px, pz, ytop, roofY(px + nx * d, pz + nz * d), roofY(px - nx * d, pz - nz * d)))
    hw = e / 2
    for sgn, ft in ((1, fa), (-1, fb)):
        m = ext_mat(o, ft) if ft == "ext" else M["pint"]; tu, tv = UVT[m.name]
        mx_ = ext_mat(o, "ext"); tu2, tv2 = UVT[mx_.name]
        for i in range(nseg):
            (ax, az, ay, rpa, rma), (bx, bz, by, rpb, rmb) = xs[i], xs[i + 1]
            ra, rb = (rpa, rpb) if sgn > 0 else (rma, rmb)
            u0 = math.hypot(ax - x1, az - z1) / tu; u1 = math.hypot(bx - x1, bz - z1) / tu
            A_, B_ = (ax + nx * hw * sgn, az + nz * hw * sgn), (bx + nx * hw * sgn, bz + nz * hw * sgn)
            if ft == "int" and ra is not None and rb is not None and (ay > ra + .05 or by > rb + .05):
                ra, rb = min(ra, ay), min(rb, by)   # bajo la cubierta pintura; el antepecho sobre la cubierta lleva la cara exterior
                if zona_bruta((A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2): int_face(A_, B_, ra, rb, (nx * sgn, 0, nz * sgn), math.hypot(ax - x1, az - z1), math.hypot(bx - x1, bz - z1))
                else: mw.face([(A_[0], 0, A_[1]), (B_[0], 0, B_[1]), (B_[0], rb, B_[1]), (A_[0], ra, A_[1])], m, (nx * sgn, 0, nz * sgn), [(u0, 0), (u1, 0), (u1, rb / tv), (u0, ra / tv)])
                v0 = math.hypot(ax - x1, az - z1) / tu2; v1 = math.hypot(bx - x1, bz - z1) / tu2
                mw.face([(A_[0], ra, A_[1]), (B_[0], rb, B_[1]), (B_[0], by, B_[1]), (A_[0], ay, A_[1])], mx_, (nx * sgn, 0, nz * sgn), [(v0, ra / tv2), (v1, rb / tv2), (v1, by / tv2), (v0, ay / tv2)])
                continue
            if ft == "int" and zona_bruta((A_[0] + B_[0]) / 2, (A_[1] + B_[1]) / 2): int_face(A_, B_, ay, by, (nx * sgn, 0, nz * sgn), math.hypot(ax - x1, az - z1), math.hypot(bx - x1, bz - z1)); continue
            pts = [(A_[0], 0, A_[1]), (B_[0], 0, B_[1]), (B_[0], by, B_[1]), (A_[0], ay, A_[1])]
            mw.face(pts, m, (nx * sgn, 0, nz * sgn), [(u0, 0), (u1, 0), (u1, by / tv), (u0, ay / tv)])
    for i in range(nseg):   # coronación metálica
        (ax, az, ay), (bx, bz, by) = xs[i][:3], xs[i + 1][:3]
        mw.face([(ax + nx * (hw + .03), ay, az + nz * (hw + .03)), (bx + nx * (hw + .03), by, bz + nz * (hw + .03)), (bx - nx * (hw + .03), by, bz - nz * (hw + .03)), (ax - nx * (hw + .03), ay, az - nz * (hw + .03))], M["galv"], (0, 1, 0))
    for (px, pz, py, _a, _b), sg in ((xs[0], -1), (xs[-1], 1)):
        ux, uz = (x2 - x1) / L * sg, (z2 - z1) / L * sg
        mw.face([(px + nx * hw, 0, pz + nz * hw), (px - nx * hw, 0, pz - nz * hw), (px - nx * hw, py, pz - nz * hw), (px + nx * hw, py, pz + nz * hw)], M["pint"], (ux, 0, uz))
# muro cortina del acceso (vidrio) delante de la fachada entre x 4 y 20,3
fz = 82.6 + .2
for x in [4 + 1.63 * k for k in range(11)]: mw.box(x - .05, x + .05, 0, 4.6, fz - .05, fz + .05, M["marco"])
mw.box(4, 20.3, 4.55, 4.75, fz - .06, fz + .06, M["marco"]); mw.face([(4, 0, fz), (20.3, 0, fz), (20.3, 4.55, fz), (4, 4.55, fz)], M["vidrio"], (0, 0, 1))
# puerta de escape hacia Cinco de Abril (del plano: x −1,48, ancho 1,7) — hoja metálica por fuera del muro
for (dx, dz, w_, nx_, nz_, wall) in [(-1.48, 1.5, 1.7, 0, -1, .15)]:
    zf = dz + nz_ * (wall + .01)
    mw.box(dx - w_ / 2 - .08, dx + w_ / 2 + .08, 0, 2.35, zf, zf + nz_ * .06, M["marco"])
    mw.box(dx - w_ / 2, dx + w_ / 2, 0, 2.25, zf + nz_ * .06, zf + nz_ * .1, M["puerta"])
    mw.box(dx - .02, dx + .02, 0, 2.25, zf + nz_ * .1, zf + nz_ * .11, M["negro"])
    mw.box(dx - w_ / 2 - .2, dx + w_ / 2 + .2, 2.4, 2.48, zf, zf + nz_ * .5, M["galv"])          # botaguas
# v83 (auditoría): puertas de escape del muro poniente hacia el patio (plano de trastienda: z 11,64–13,54 y 49,43–51,33). El muro Blender es macizo
#      y las puertas del simulador quedaban dentro de él: hoja doble con marco por ambas caras, barra antipánico y letrero de salida por dentro
for (dz, w_) in [(12.59, 1.9), (50.38, 1.9)]:
    for sx in (1, -1):
        xf = -59.2 + sx * .155; a0, a1 = dz - w_ / 2, dz + w_ / 2
        xs = sorted((xf, xf + sx * .05)); mw.box(xs[0], xs[1], 0, 2.32, a0 - .07, a1 + .07, M["marco"])
        for (z0, z1) in ((a0, dz - .006), (dz + .006, a1)):
            xs = sorted((xf + sx * .05, xf + sx * .09)); mw.box(xs[0], xs[1], .01, 2.24, z0, z1, M["puerta"])
        if sx > 0:
            xs = sorted((xf + sx * .09, xf + sx * .14)); mw.box(xs[0], xs[1], .98, 1.05, a0 + .1, a1 - .1, M["galv"])          # barra antipánico
            for zz in (a0 + .1, a1 - .1): xs = sorted((xf + sx * .09, xf + sx * .14)); mw.box(xs[0], xs[1], .94, 1.09, zz - .03, zz + .03, M["negro"])
            xs = sorted((xf + sx * .02, xf + sx * .06)); mw.box(xs[0], xs[1], 2.45, 2.65, dz - .2, dz + .2, M["letrero_verde"])   # letrero de salida
        else:
            xs = sorted((xf + sx * .09, xf + sx * .11)); mw.box(xs[0], xs[1], 1.0, 1.2, a1 - .25, a1 - .2, M["negro"])
# octágono: vitrinas y acceso hacia O'Higgins y Riquelme (SUPUESTO: el plano lo marca como ciego)
OCT = [((39.8, 118.85), (26.7, 118.85), (0, 1)), ((39.8, 101.75), (39.8, 118.85), (1, 0))]
for (a, b, (nx_, nz_)) in OCT:
    off = .15 + .06; L_ = math.hypot(b[0] - a[0], b[1] - a[1]); ux_, uz_ = (b[0] - a[0]) / L_, (b[1] - a[1]) / L_
    A2 = (a[0] + ux_ * 1.2 + nx_ * off, a[1] + uz_ * 1.2 + nz_ * off); B2 = (b[0] - ux_ * 1.2 + nx_ * off, b[1] - uz_ * 1.2 + nz_ * off)
    mw.face([(A2[0], .3, A2[1]), (B2[0], .3, B2[1]), (B2[0], 3.4, B2[1]), (A2[0], 3.4, A2[1])], M["vidrio"], (nx_, 0, nz_))
    nmu = max(2, int((L_ - 2.4) / 1.6))
    for k in range(nmu + 1):
        t = k / nmu; px, pz = A2[0] + (B2[0] - A2[0]) * t, A2[1] + (B2[1] - A2[1]) * t
        mw.box(px - .05, px + .05, 0, 3.5, pz - .05, pz + .05, M["marco"])
    for yy in (.3, 3.45): mw.seg((A2[0], yy, A2[1]), (B2[0], yy, B2[1]), .1, .1, M["marco"])
    mx_, mz_ = (A2[0] + B2[0]) / 2, (A2[1] + B2[1]) / 2
    mw.seg((mx_ - ux_ * 1.0 + nx_ * .02, 2.6, mz_ - uz_ * 1.0 + nz_ * .02), (mx_ + ux_ * 1.0 + nx_ * .02, 2.6, mz_ + uz_ * 1.0 + nz_ * .02), .06, .06, M["marco"])   # dintel de la puerta
    mw.seg((A2[0] + nx_ * .03, 3.75, A2[1] + nz_ * .03), (B2[0] + nx_ * .03, 3.75, B2[1] + nz_ * .03), .06, .5, M["marco"])                                   # dintel corrido
mw.build(); mr.build()

# =====================================================================
# 2) CUBIERTAS
# =====================================================================
G = "Techo_Exterior"; tc = MB("cubiertas", G); tu = MB("cubiertas_inferior", "Estructura_Principal")
for o in ROOFS:
    P = o["p"]
    if o in MAIN:
        mt = M["chapa"] if o.get("cae") == 180 else M["memb"]
        for tri in fan(P):
            tc.face([(x, top(x), z) for x, z in tri], mt, (0, 1, 0)); tu.face([(x, top(x) - .08, z) for x, z in tri], M["deck"], (0, -1, 0))
    elif "2º nivel" in o["n"]:
        x0, x1, z0, z1 = N2
        tc.face([(x0, roof2(x0), z0), (x1, roof2(x1), z0), (x1, roof2(x1), z1), (x0, roof2(x0), z1)], M["chapa"], (0, 1, 0))
        tu.face([(x0, roof2(x0) - .1, z0), (x1, roof2(x1) - .1, z0), (x1, roof2(x1) - .1, z1), (x0, roof2(x0) - .1, z1)], M["deck"], (0, -1, 0))
        for zz, sg in ((z0, -1), (z1, 1)):     # testeros del volumen sobre la cubierta general
            tc.face([(x0, top(x0), zz), (x1, top(x1), zz), (x1, roof2(x1) + .3, zz), (x0, roof2(x0) + .3, zz)], M["hvac"], (0, 0, sg))
        tc.face([(x1, top(x1), z0), (x1, top(x1), z1), (x1, roof2(x1) + .3, z1), (x1, roof2(x1) + .3, z0)], M["hvac"], (1, 0, 0))
        tc.face([(x0, top(x0), z0), (x0, top(x0), z1), (x0, roof2(x0) + .3, z1), (x0, roof2(x0) + .3, z0)], M["hvac"], (-1, 0, 0))
    elif "escaleras" in o["n"]:
        x0, x1 = min(p[0] for p in P), max(p[0] for p in P); z0, z1 = min(p[1] for p in P), max(p[1] for p in P)
        tc.face([(x0, 5.2, z0), (x1, 5.2, z0), (x1, 4.6, z1), (x0, 4.6, z1)], M["galv"], (0, 1, 0)); tc.face([(x0, 5.0, z0), (x1, 5.0, z0), (x1, 4.4, z1), (x0, 4.4, z1)], M["acero"], (0, -1, 0))
        for zz, y in ((z0, 5.2), (z1, 4.6)): tc.box(x0, x1, y - .45, y, zz - .03, zz + .03, M["galv"])
    else:
        y = cota(o, 7.55); alero = "alero" in o["n"].lower()
        tc.slab(P, y, y + .3, M["plano"], M["list"] if alero else M["pint"], M["galv"] if alero else M["estgris"])
for o in by_t("lucarna"):
    P = o["p"]
    if all(inpoly(x, z, MAIN[0]["p"]) or inpoly(x, z, MAIN[-1]["p"]) for x, z in P):
        for tri in fan(P): tc.face([(x, top(x) + .02, z) for x, z in tri], M["trasl"], (0, 1, 0)); tu.face([(x, top(x) - .06, z) for x, z in tri], M["trasl"], (0, -1, 0))
    else:
        y = 5.85; x0, x1 = min(p[0] for p in P), max(p[0] for p in P); z0, z1 = min(p[1] for p in P), max(p[1] for p in P)
        tc.box(x0, x1, y, y + .25, z0, z1, M["galv"], skip=("+y",)); tc.face([(x0, y + .25, z0), (x1, y + .25, z0), ((x0 + x1) / 2, y + 1.0, (z0 + z1) / 2)], M["trasl"], (0, 1, -1))
        tc.face([(x1, y + .25, z0), (x1, y + .25, z1), ((x0 + x1) / 2, y + 1.0, (z0 + z1) / 2)], M["trasl"], (1, 1, 0)); tc.face([(x1, y + .25, z1), (x0, y + .25, z1), ((x0 + x1) / 2, y + 1.0, (z0 + z1) / 2)], M["trasl"], (0, 1, 1))
        tc.face([(x0, y + .25, z1), (x0, y + .25, z0), ((x0 + x1) / 2, y + 1.0, (z0 + z1) / 2)], M["trasl"], (-1, 1, 0))
# cumbrera, canaletas y bajadas
tc.face([(XR - .3, RIDGE + .01, Z0), (XR, RIDGE + .12, Z0), (XR, RIDGE + .12, ZF), (XR - .3, RIDGE + .01, ZF)], M["galv"], (0, 1, 0))
tc.face([(XR, RIDGE + .12, Z0), (XR + .3, RIDGE + .01, Z0), (XR + .3, RIDGE + .01, ZF), (XR, RIDGE + .12, ZF)], M["galv"], (0, 1, 0))
for o in by_t("canaleta"):
    x = o["x1"]; s = -1 if x > 0 else 1; za, zb = sorted((o["z1"], o["z2"]))   # v80: s invertido → canaleta y bajadas por el lado EXTERIOR del muro (antes caían dentro de la trastienda)
    tc.box(x - s * .1, x - s * .45, EAVE - .25, EAVE - .22, za, zb, M["galv"]); tc.box(x - s * .1, x - s * .13, EAVE - .25, EAVE + .02, za, zb, M["galv"]); tc.box(x - s * .42, x - s * .45, EAVE - .25, EAVE + .05, za, zb, M["galv"])
    for zz in (za, zb): tc.box(x - s * .1, x - s * .45, EAVE - .25, EAVE + .02, zz - .01, zz + .01, M["galv"])      # tapas
    for k in range(int((zb - za) / 1.0) + 1):                                                                       # soportes cada 1 m
        zz = za + k * 1.0; tc.seg((x - s * .08, EAVE - .1, zz), (x - s * .47, EAVE - .1, zz), .025, .004, M["galv"])
        tc.seg((x - s * .1, EAVE - .26, zz), (x - s * .1, EAVE + .03, zz), .025, .004, M["galv"])
    for zz in [za + 6 + 12 * k for k in range(int((zb - za) / 12))]:
        xd = x - s * .75; tc.box(x - s * .2, x - s * .35, EAVE - .45, EAVE - .25, zz - .1, zz + .1, M["galv"])           # embudo
        tc.cyl((x - s * .27, EAVE - .45, zz), (xd, EAVE - .75, zz), .06, M["galv"]); tc.cyl((xd, .45, zz), (xd, EAVE - .75, zz), .06, M["galv"])
        tc.cyl((xd, .45, zz), (xd + s * .25, .12, zz), .06, M["galv"])                                               # zapata
        for yy in [1.0 + 1.8 * k for k in range(int((EAVE - 1.5) / 1.8))]:
            tc.cyl((xd, yy, zz), (xd, yy + .04, zz), .075, M["galv"]); tc.seg((xd, yy + .02, zz), (xd + s * .12, yy + .02, zz), .02, .03, M["galv"])
# malla raschel con postes
for o in by_t("malla"):
    P = o["p"]; y = cota(o, 6.35); tc.face([(x, y, z) for x, z in P], M["malla"], (0, 1, 0))
    x0, x1 = min(p[0] for p in P), max(p[0] for p in P); z0, z1 = min(p[1] for p in P), max(p[1] for p in P)
    for zz in (z0, z0 + (z1 - z0) / 2, z1): tc.box(x0 - .06, x0 + .06, 0, y, zz - .06, zz + .06, M["galv"])
# equipos sobre cubiertas (según foto aérea: ductos y condensadores sobre el 2º nivel; equipos en la franja frontal y el octágono)
x0, x1, z0, z1 = N2
def cond(cx, cz, y, nf=6):
    hz = 1.6 * nf / 6 * 2; y0 = y + .25
    for xx in (cx - .8, cx + .8): tc.box(xx - .06, xx + .06, y, y0, cz - hz - .3, cz + hz + .3, M["galv"])         # rieles base
    tc.box(cx - 1.1, cx + 1.1, y0, y0 + 1.5, cz - hz, cz + hz, M["hvac"])
    for sg in (1, -1):                                                                                               # serpentines con rejilla
        xf = cx + sg * 1.11; tc.face([(xf, y0 + .15, cz - hz + .15), (xf, y0 + .15, cz + hz - .15), (xf, y0 + 1.35, cz + hz - .15), (xf, y0 + 1.35, cz - hz + .15)], M["rejilla"], (sg, 0, 0), [(0, 0), ((2 * hz - .3) / .25, 0), ((2 * hz - .3) / .25, 1.2 / .25), (0, 1.2 / .25)])
        for k in range(int(2 * hz / .5)): tc.box(xf - .01, xf + .01, y0 + .1, y0 + 1.4, cz - hz + .25 + k * .5 - .01, cz - hz + .25 + k * .5 + .01, M["galv"])
    for k in range(nf):
        zz = cz - hz + .8 + k * (2 * hz - 1.6) / max(1, nf - 1)
        for xx in (cx - .5, cx + .5):
            tc.cyl((xx, y0 + 1.5, zz), (xx, y0 + 1.62, zz), .4, M["hvac"], 16); tc.disk((xx, y0 + 1.52, zz), .38, M["vent"], True, 16)
            tc.disk((xx, y0 + 1.63, zz), .4, M["rejilla"], True, 16); tc.cyl((xx, y0 + 1.5, zz), (xx, y0 + 1.6, zz), .06, M["negro"], 8)
    tc.box(cx + 1.1, cx + 1.3, y0 + .6, y0 + 1.1, cz - .25, cz + .25, M["negro"])                                   # seccionador
    for k, dx in enumerate((-.08, .08)): tc.cyl((cx + 1.2, y0 + .3, cz + .6 + dx), (cx + 1.2, y + .08, cz + .6 + dx), .025 + .01 * k, M["aislante"], 8)
cond(-53.5, 38, roof2(-53.5)); cond(-50.3, 41, roof2(-50.3), 4)
for zz in [24, 31, 47, 55, 62]:
    yb = roof2(-55); tc.box(-56.6, -54.6, yb, yb + 1.3, zz - 1, zz + 1, M["hvac"])
    tc.box(-54.6, -45.5, yb + .3, yb + 1.1, zz - .5, zz + .5, M["ducto"]); tc.box(-46.3, -45.5, top(-45.9), yb + 1.1, zz - .5, zz + .5, M["ducto"])
tc.box(-55.6, -54.8, roof2(-55), roof2(-55) + 1.0, 21, 66, M["ducto"])
for (cx, cz) in [(-40, 78), (-20, 77), (-2, 79), (12, 77.5), (28, 79), (30.5, 106), (25, 111), (34, 113)]:
    yb = roofY(cx, cz) or 7.55; yb += .3; tc.box(cx - 1.35, cx + 1.35, yb, yb + .25, cz - 1.05, cz + 1.05, M["galv"]); yb += .25   # base / curb
    tc.box(cx - 1.2, cx + 1.2, yb, yb + 1.2, cz - .9, cz + .9, M["hvac"]); tc.cyl((cx, yb + 1.2, cz), (cx, yb + 1.3, cz), .47, M["hvac"], 16)
    tc.disk((cx, yb + 1.22, cz), .45, M["vent"], True, 16); tc.disk((cx, yb + 1.31, cz), .47, M["rejilla"], True, 16)
    for k in range(7): tc.box(cx - 1.21, cx - 1.2, yb + .15 + k * .14, yb + .2 + k * .14, cz - .8, cz + .8, M["galv"])          # celosía
    tc.box(cx + 1.2, cx + 1.38, yb + .4, yb + .85, cz - .2, cz + .2, M["negro"])
# ---- detalle de cubiertas: nervios de la chapa, juntas de membrana, línea de vida, escotilla ----
LUC = [o["p"] for o in by_t("lucarna")]
def huecos(z): return [iv for P in LUC for iv in scan(P, z)] + ([(N2[0] - .1, N2[1])] if N2[2] < z < N2[3] else [])
def rib(xa, xb, z, fy, w, h, m):
    pts = [xa, xb] + ([XR] if xa < XR < xb else [])
    pts.sort()
    for a_, b_ in zip(pts, pts[1:]): tc.seg((a_, fy(a_) + h / 2, z), (b_, fy(b_) + h / 2, z), w, h, m)
for o in MAIN:
    P = o["p"]; z0_, z1_ = min(p[1] for p in P), max(p[1] for p in P); ch = o.get("cae") == 180
    paso = .25 if ch else 2.0; z = z0_ + paso / 2
    while z < z1_:
        for xa, xb in restar(scan(P, z), huecos(z)):
            if ch: rib(xa, xb, z, top, .035, .035, M["chapa"])
            else: rib(xa, xb, z, top, .06, .006, M["memb"])
        z += paso
x0, x1, z0, z1 = N2; z = z0 + .125
while z < z1:
    tc.seg((x0, roof2(x0) + .0175, z), (x1, roof2(x1) + .0175, z), .035, .035, M["chapa"]); z += .25
for o in ROOFS:                                                     # juntas en las cubiertas planas (no aleros)
    if o["t"] != "plana" or re.search("alero|escaleras|2º nivel", o["n"], re.I): continue
    P = o["p"]; y = cota(o, 7.55) + .3; z0_, z1_ = min(p[1] for p in P), max(p[1] for p in P); z = z0_ + 1.0
    while z < z1_:
        for xa, xb in scan(P, z): tc.seg((xa, y + .003, z), (xb, y + .003, z), .06, .006, M["plano"])
        z += 2.0
for zz in [Z0 + 2 + 9 * k for k in range(9)]:                       # línea de vida en la cumbrera
    tc.cyl((XR + .5, top(XR + .5), zz), (XR + .5, top(XR + .5) + .55, zz), .025, M["galv"], 8); tc.box(XR + .38, XR + .62, top(XR + .5), top(XR + .5) + .02, zz - .12, zz + .12, M["galv"])
tc.cyl((XR + .5, top(XR + .5) + .5, Z0 + 2), (XR + .5, top(XR + .5) + .5, Z0 + 2 + 72), .006, M["galv"], 6)
hx, hz = -40.0, 60.0; yh = top(hx)                                     # escotilla de acceso (SUPUESTO)
tc.box(hx - .6, hx + .6, yh, yh + .45, hz - .6, hz + .6, M["hvac"]); tc.box(hx - .65, hx + .65, yh + .45, yh + .52, hz - .65, hz + .65, M["galv"])
for sg in (1, -1): tc.cyl((hx + sg * .55, yh + .5, hz + .65), (hx + sg * .55, yh + 1.5, hz + .9), .02, M["galv"], 6)
tc.build(); tu.build()

# =====================================================================
# 3) ESTRUCTURA
# =====================================================================
G = "Estructura_Principal"; es = MB("estructura", G)
def under(x, z, d=0.0, fb=4.5):
    r = roofY(x, z)
    if x >= N2[0] - .1 and x <= N2[1] and N2[2] <= z <= N2[3] and r is None: r = top(x)
    return (r if r is not None else fb) - d
# v80 (Cristian): los pilares nacen desde el subterráneo → sin dado de hormigón, sin placa base ni pernos; columna desde el piso.
#   En bodega, trastienda, patio y recepción: hormigón en bruto con la base pintada de blanco gastado (fotos pilar 2, pilar 3, pilar6).
#   En bodega además: marco amarillo pintado, extintor colgado de su gancho (sin soporte) y letreros, en la cara hacia el pasillo.
EXT_BOD = {(3.68, 2.35): 1, (19.43, 2.35): 1, (34.97, 2.35): 1, (19.43, 10.47): -1, (3.68, 10.47): -1}   # cara z+ (1) o z− (−1)
SAL_BOD = {(19.43, 2.35), (34.97, 2.35), (19.43, 10.47)}
def extintor(cx, cz, nz, y0=.95):
    zf = cz + nz * .11
    es.cyl((cx, y0, zf), (cx, y0 + .46, zf), .085, M["rojo_ext"], 16); es.cyl((cx, y0 + .46, zf), (cx, y0 + .5, zf), .07, M["rojo_ext"], 16)      # cilindro y hombro
    es.cyl((cx, y0 + .5, zf), (cx, y0 + .58, zf), .022, M["negro"], 8); es.box(cx - .05, cx + .03, y0 + .58, y0 + .6, zf - .015, zf + .015, M["negro"])   # válvula y palanca
    es.cyl((cx + .02, y0 + .55, zf + nz * .05), (cx + .06, y0 + .2, zf + nz * .09), .009, M["negro"], 6)                                          # manguera
    es.box(cx - .03, cx + .03, y0 + .4, y0 + .62, cz + nz * .002, cz + nz * .03, M["negro"])                                                         # gancho al pilar
def pilar_bruto(x, z, w, l, yt):
    es.box(x - w / 2, x + w / 2, 0, yt, z - l / 2, z + l / 2, M["pilarh"])
    hb = 2.35; d = .004                                                                                  # base pintada (calcomanía 4 caras)
    for (nx_, nz_) in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        if nz_:
            zf = z + nz_ * (l / 2 + d); xa, xb = (x - w / 2, x + w / 2) if nz_ > 0 else (x + w / 2, x - w / 2)
            es.face([(xa, 0, zf), (xb, 0, zf), (xb, hb, zf), (xa, hb, zf)], M["pilarp"], (0, 0, nz_), [(0, 0), (1, 0), (1, 1), (0, 1)])
        else:
            xf = x + nx_ * (w / 2 + d); za, zb = (z + l / 2, z - l / 2) if nx_ > 0 else (z - l / 2, z + l / 2)
            es.face([(xf, 0, za), (xf, 0, zb), (xf, hb, zb), (xf, hb, za)], M["pilarp"], (nx_, 0, 0), [(0, 0), (1, 0), (1, 1), (0, 1)])
    key = min(EXT_BOD, key=lambda k: math.hypot(k[0] - x, k[1] - z))
    if math.hypot(key[0] - x, key[1] - z) < .3:
        nz_ = EXT_BOD[key]; zf = z + nz_ * (l / 2 + .006)
        for (xa, xb, ya, yb) in [(x - .3, x - .22, 0, 2.0), (x + .22, x + .3, 0, 2.0)]:                   # franjas amarillas pintadas (foto pilar 2)
            P_ = [(xa, ya, zf), (xb, ya, zf), (xb, yb, zf), (xa, yb, zf)]
            es.face(P_ if nz_ > 0 else P_[::-1], M["amarillo"], (0, 0, nz_))
        extintor(x, z + nz_ * (l / 2), nz_)
        for (ya, yb, mt) in [(1.72, 1.92, "letrero_rojo")] + ([(2.6, 2.78, "letrero_verde")] if key in SAL_BOD else []):
            P_ = [(x - .09 if mt == "letrero_rojo" else x - .14, ya, zf + nz_ * .002), (x + .09 if mt == "letrero_rojo" else x + .14, ya, zf + nz_ * .002), (x + .09 if mt == "letrero_rojo" else x + .14, yb, zf + nz_ * .002), (x - .09 if mt == "letrero_rojo" else x - .14, yb, zf + nz_ * .002)]
            es.face(P_ if nz_ > 0 else P_[::-1], M[mt], (0, 0, nz_))
for o in by_t("pilar"):
    yt = under(o["x"], o["z"], 1.33 if roofY(o["x"], o["z"]) and o["z"] < 74.5 else 0.35, o.get("h", 4.5))
    w, l = o.get("w", .6), o.get("l", .6); x, z = o["x"], o["z"]
    if "alero" in (o.get("n") or "").lower():       # fotos (automotora, mall chino): columna metálica redonda negra
        es.cyl((x, 0, z), (x, yt, z), .11, M["colneg"], 24); es.cyl((x, 0, z), (x, .06, z), .2, M["colneg"], 24); es.disk((x, .06, z), .2, M["colneg"], True, 24)
        continue
    if zona_bruta(x, z): pilar_bruto(x, z, w, l, yt)
    else: es.box(x - w / 2, x + w / 2, 0, yt, z - l / 2, z + l / 2, M["acero"])                         # sala: columna pintada
    if roofY(x, z) and z < 74.5:                                                                                      # cartelas hacia la viga longitudinal
        for sz in (1, -1):
            for sx in (1, -1):
                xx = x + sx * .006; es.face([(xx, yt, z + sz * l / 2), (xx, yt, z + sz * (l / 2 + .8)), (xx, yt - .8, z + sz * l / 2)], M["acero"], (sx, 0, 0))
def split74(o):
    a, b = (o["x1"], o["z1"]), (o["x2"], o["z2"]); segs = [(a, b)]
    for zc in (74.0,):
        out = []
        for p, q in segs:
            if (p[1] - zc) * (q[1] - zc) < 0:
                t = (zc - p[1]) / (q[1] - p[1]); m = (p[0] + (q[0] - p[0]) * t, zc); out += [(p, m), (m, q)]
            else: out.append((p, q))
        segs = out
    return segs
for o in by_t("viga"):
    nm = o.get("n", ""); D = 0.68 if "IPE 680" in o.get("perfil", "") else 0.5 if "500" in o.get("perfil", "") else 0.45 if "450" in o.get("perfil", "") else 0.3
    for (p, q) in split74(o):
        if nm == "Marco":
            pts = [p[0], q[0]] + ([XR] if min(p[0], q[0]) < XR < max(p[0], q[0]) else []); pts = sorted(pts)
            for a, b in zip(pts, pts[1:]): es.ibeam((a, top(a) - .49, p[1]), (b, top(b) - .49, p[1]), D, M["acero"])
        elif nm.startswith("Viga longitudinal") or nm == "Viga ochava":
            ya = top(p[0]) - 1.08 if p[1] < 74.5 else 7.55 - .5; yb = top(q[0]) - 1.08 if q[1] < 74.5 else 7.55 - .5
            es.ibeam((p[0], ya, p[1]), (q[0], yb, q[1]), D, M["acero"], bf=.2)
        else:
            mx, mz = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2; y = under(mx, mz, .25 + D / 2)
            es.ibeam((p[0], y, p[1]), (q[0], y, q[1]), D, M["acero"], bf=.15)
for o in by_t("costanera"):
    for (p, q) in split74(o):
        mx, mz = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
        if mz < 74 and XW <= mx <= XE: ya, yb = top(p[0]) - .17, top(q[0]) - .17
        else: ya = yb = under(mx, mz, .17)
        es.cprof((p[0], ya, p[1]), (q[0], yb, q[1]), .15, .06, M["acero"])
# tensores (colgadores de costaneras) a media luz entre marcos
MZ = sorted(set(round(o["z1"], 2) for o in by_t("viga") if o.get("n") == "Marco" and o["z1"] < 74))
for za_, zb_ in zip(MZ, MZ[1:]):
    zm = (za_ + zb_) / 2
    for xa_, xb_ in ((XW + .3, XR - .2), (XR + .2, XE - .3)): es.cyl((xa_, top(xa_) - .2, zm), (xb_, top(xb_) - .2, zm), .006, M["galv"], 4)
for o in by_t("arriostre"):
    ya = under(o["x1"], o["z1"], .3); yb = under(o["x2"], o["z2"], .3); es.cyl((o["x1"], ya, o["z1"]), (o["x2"], yb, o["z2"]), .014, M["galv"], 6)
for o in by_t("cercha"):
    x, za, zb = o["x1"], o["z1"], o["z2"]; yt = under(x, (za + zb) / 2, .15); yb = yt - .9
    es.seg((x, yt, za), (x, yt, zb), .1, .1, M["acero"]); es.seg((x, yb, za), (x, yb, zb), .1, .1, M["acero"])
    n = int((zb - za) / 1.5)
    for k in range(n + 1):
        z = za + (zb - za) * k / n; es.seg((x, yb, z), (x, yt, z), .05, .05, M["acero"])
        if k < n: z2 = za + (zb - za) * (k + 1) / n; es.seg((x, yb, z), (x, yt, z2), .05, .05, M["acero"])
es.build()

# =====================================================================
# 4) LUMINARIAS
# =====================================================================
G = "Luminarias_Techo"; lu = MB("luminarias", G)
for o in by_t("led"):
    x1, z1, x2, z2, h = o["x1"], o["z1"], o["x2"], o["z2"], o.get("h", 5.4)
    lu.seg((x1, h + .04, z1), (x2, h + .04, z2), .14, .07, M["ledc"]); lu.seg((x1, h - .003, z1), (x2, h - .003, z2), .1, .01, M["led"])
    rt = under((x1 + x2) / 2, (z1 + z2) / 2, .5)
    for t in (.15, .85):
        px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t
        if rt > h + .1: lu.cyl((px, h + .07, pz), (px, rt, pz), .004, M["galv"], 4)
for o in by_t("downlight"):
    x, z, h = o["x"], o["z"], o.get("h", 3) - .01
    lu.cyl((x, h + .005, z), (x, h - .012, z), .115, M["ledc"], 16); lu.disk((x, h - .012, z), .115, M["ledc"], False, 16)       # aro
    lu.disk((x, h - .014, z), .095, M["down"], False, 16)                                                                     # difusor
    lu.cyl((x, h + .005, z), (x, h + .13, z), .1, M["ledc"], 12); lu.disk((x, h + .13, z), .1, M["ledc"], True, 12)           # carcasa cerrada
lu.build()

# =====================================================================
# 5) CIELOS FALSOS, 2º NIVEL, ESCALERA Y ASCENSOR
# =====================================================================
G = "Frontis"; ci = MB("cielos_nivel2", G)
for o in by_t("cielo"):
    P = o["p"]; h = o.get("h", 3.0); ci.slab(P, h, h + .04, M["pint"], M["cielo"], M["pint"])
    for i in range(len(P)):      # faldón blanco del borde (como en la foto de carnicería)
        a, b = P[i], P[(i + 1) % len(P)]; ci.face([(a[0], h, a[1]), (b[0], h, b[1]), (b[0], h + .7, b[1]), (a[0], h + .7, a[1])], M["pint"], None)
for o in by_t("losa"):
    P = o["p"]; h = o.get("h", 3.4); ci.slab(P, h - .2, h, M["horm2"], M["losainf"], M["losainf"])
    # v79 · cielo del 2º nivel visto desde el pasillo (foto «trastienda»): losa de hormigón oscura con vigas, conduits negros y tubos blancos colgados
    x0, x1, z0, z1 = N2; yb = h - .2
    # v80 (Cristian): bajo el 2º nivel las vigas no están a la vista → sin vigas, solo la losa
    for k, (xx, rr, mt) in enumerate([(-57.0, .025, "pvc_neg"), (-57.25, .02, "pvc_neg"), (-58.9, .03, "pvc_bco"), (-56.4, .04, "pvc_bco"), (-58.7, .02, "pvc_neg")]):
        yy = yb - .06 - (k % 2) * .05
        ci.cyl((xx, yy, z0 + .3), (xx, yy, z1 - .3), rr, M[mt], 8)
        zz = z0 + 1.0
        while zz < z1:
            ci.box(xx - .02, xx + .02, yy, yb, zz - .015, zz + .015, M["galv"]); zz += 2.0
    x0, x1, z0, z1 = N2
    for (a, b) in [((x1, z0), (x1, z1)), ((x0, z0), (x1, z0)), ((x0, z1), (x1, z1))]:     # tabiques del 2º nivel hasta la cubierta propia
        for sg in (1, -1):
            yA, yB = roof2(a[0]) - .1, roof2(b[0]) - .1; off = .08 * sg
            if a[0] == b[0]: ci.face([(a[0] + off, h, a[1]), (b[0] + off, h, b[1]), (b[0] + off, yB, b[1]), (a[0] + off, yA, a[1])], M["muro_osc"], (sg, 0, 0))
            else: ci.face([(a[0], h, a[1] + off), (b[0], h, b[1] + off), (b[0], yB, b[1] + off), (a[0], yA, a[1] + off)], M["muro_osc"], (0, 0, sg))
# v80 (Cristian): sobre el cielo falso de vinos hay un muro de cierre (oscuro) desde el cielo hasta la cubierta, en los bordes que dan a la sala
for (a, b) in [((-28.27, 15.37), (-3.72, 15.37)), ((-28.27, 4.86), (-28.27, 15.37)), ((-3.72, 12.08), (-3.72, 15.37))]:
    for sg in (1, -1):
        off = .06 * sg; L_ = math.hypot(b[0] - a[0], b[1] - a[1]); n_ = max(1, int(L_ / 2.0))
        for k in range(n_):
            p0 = (a[0] + (b[0] - a[0]) * k / n_, a[1] + (b[1] - a[1]) * k / n_); p1 = (a[0] + (b[0] - a[0]) * (k + 1) / n_, a[1] + (b[1] - a[1]) * (k + 1) / n_)
            y0a = 3.04; ya = under(p0[0], p0[1], .05); yb = under(p1[0], p1[1], .05)
            if a[0] == b[0]: ci.face([(p0[0] + off, y0a, p0[1]), (p1[0] + off, y0a, p1[1]), (p1[0] + off, yb, p1[1]), (p0[0] + off, ya, p0[1])], M["muro_osc"], (sg, 0, 0))
            else: ci.face([(p0[0], y0a, p0[1] + off), (p1[0], y0a, p1[1] + off), (p1[0], yb, p1[1] + off), (p0[0], ya, p0[1] + off)], M["muro_osc"], (0, 0, sg))
for o in by_t("escalera"):
    d = (math.cos(math.radians(o["a"])), math.sin(math.radians(o["a"]))); lf = (d[1], -d[0]); side = (-lf[0], -lf[1]) if o.get("giro") == "der" else lf
    w, t1, t2, H = o["ancho"], o["t1"], o["t2"], o.get("h", 3.4); n = max(4, round(H / .17)); rise = H / n
    q = lambda p, v, k: (p[0] + v[0] * k, p[1] + v[1] * k)
    tramos = [((o["x"], o["z"]), d, t1)]
    B = q((o["x"], o["z"]), d, t1)
    if o.get("giro") != "recta": tramos.append((q(B, side, w), side, t2))
    tot = sum(t[2] for t in tramos); k = 0; yl = 0
    for ti, (A0, dv, L) in enumerate(tramos):
        ns = max(1, round(n * L / tot)) if ti < len(tramos) - 1 else n - k; run = L / ns
        sv = side if ti == 0 else d; y0s = k * rise
        for i in range(ns):
            a = q(A0, dv, run * i); b = q(A0, dv, run * (i + 1)); y = (k + 1) * rise; k += 1
            c = [a, b, q(b, sv, w), q(a, sv, w)]; ci.slab(c, y - .05, y, M["escalon"], M["acero"], M["acero"])
        yl = k * rise
        if ti == 0 and len(tramos) > 1:
            c = [B, q(B, d, w), q(q(B, d, w), side, w), q(B, side, w)]; ci.slab(c, yl - .12, yl, M["escalon"], M["acero"], M["acero"])
        e0 = A0; e1 = q(A0, dv, L)
        ci.cyl((e0[0], y0s + .9, e0[1]), (e1[0], yl + .9, e1[1]), .025, M["galv"])
for o in by_t("ascensor"):
    c, s_ = math.cos(math.radians(o["a"])), math.sin(math.radians(o["a"])); w, l = o["w"] / 2, o["l"] / 2
    P = [(o["x"] + u * c - v * s_, o["z"] + u * s_ + v * c) for u, v in ((-w, -l), (w, -l), (w, l), (-w, l))]
    ci.slab(P, 0, 6.6, M["estgris"], M["estgris"], M["estgris"])
ci.build()

# =====================================================================
# 6) LOCALES (vitrinas, tabiques, letreros) y FRONTIS EXTERIOR
# =====================================================================
G = "Frontis"; lo = MB("locales", G)
def rect(o):
    c, s_ = math.cos(math.radians(o.get("a", 0))), math.sin(math.radians(o.get("a", 0))); w, l = o["w"] / 2, o["l"] / 2
    return [(o["x"] + u * c - v * s_, o["z"] + u * s_ + v * c) for u, v in ((-w, -l), (w, -l), (w, l), (-w, l))]
SIDE = {"abajo": (0, 1), "derecha": (1, 2), "arriba": (2, 3), "izquierda": (3, 0)}
for o in by_t("local", "local_poly"):
    nm = (o.get("n") or "").strip(); sign = re.sub(r"\s*\(.*?\)", "", nm).strip() or "LOCAL"
    if "jard" in nm.lower():
        P = o["p"]; lo.poly(P, .08, M["pasto"])
        cx = sum(p[0] for p in P) / len(P); cz = sum(p[1] for p in P) / len(P)
        for dx, dz in ((-2.5, -2), (2, 1.5), (-1, 2.5), (2.6, -2.4)): lo.box(cx + dx - .6, cx + dx + .6, .08, 1.1, cz + dz - .6, cz + dz + .6, M["arbusto"])
        continue
    P = rect(o) if o["t"] == "local" else o["p"]; h = o.get("h", 3.5); fs = SIDE.get(o.get("fach")) if o["t"] == "local" else None
    big = "mall chino" in nm.lower()
    if not big and o["t"] == "local":
        lo.slab(P, h, h + .1, M["pint"], M["pint"], M["estgris"])
        for i in range(4):
            if fs and i == fs[0]: continue
            a, b = P[i], P[(i + 1) % 4]; ux, uz = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uz) or 1; nx, nz = uz / L * .06, -ux / L * .06
            lo.face([(a[0] + nx, 0, a[1] + nz), (b[0] + nx, 0, b[1] + nz), (b[0] + nx, h, b[1] + nz), (a[0] + nx, h, a[1] + nz)], M["pint"], None)
            lo.face([(a[0] - nx, 0, a[1] - nz), (a[0] - nx, h, a[1] - nz), (b[0] - nx, h, b[1] - nz), (b[0] - nx, 0, b[1] - nz)], M["pint"], None)
    if fs:
        a, b = P[fs[0]], P[fs[1]]; ux, uz = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uz) or 1
        cx = sum(p[0] for p in P) / 4; cz = sum(p[1] for p in P) / 4; nx, nz = uz / L, -ux / L
        if nx * ((a[0] + b[0]) / 2 - cx) + nz * ((a[1] + b[1]) / 2 - cz) < 0: nx, nz = -nx, -nz
        off = .21; A2 = (a[0] + nx * off, a[1] + nz * off); B2 = (b[0] + nx * off, b[1] + nz * off); hv = min(h, 3.2)
        lo.face([(A2[0], .05, A2[1]), (B2[0], .05, B2[1]), (B2[0], hv, B2[1]), (A2[0], hv, A2[1])], M["vidrio"], (nx, 0, nz))
        dI = 1.4; Ai, Bi = (A2[0] - nx * dI, A2[1] - nz * dI), (B2[0] - nx * dI, B2[1] - nz * dI)        # interior genérico visto a través del vidrio
        lo.face([(Ai[0], 0, Ai[1]), (Bi[0], 0, Bi[1]), (Bi[0], hv + .2, Bi[1]), (Ai[0], hv + .2, Ai[1])], M["vitri"], (nx, 0, nz), [(0, 0), (L / 6, 0), (L / 6, (hv + .2) / 3), (0, (hv + .2) / 3)])
        nm_ = max(1, int(L / 1.8))
        for k in range(nm_ + 1):
            t = k / nm_; px, pz = A2[0] + (B2[0] - A2[0]) * t, A2[1] + (B2[1] - A2[1]) * t; lo.box(px - .04, px + .04, 0, hv, pz - .04, pz + .04, M["marco"])
        lo.seg((A2[0], hv + .05, A2[1]), (B2[0], hv + .05, B2[1]), .1, .1, M["marco"])
        # letrero sobre la vitrina
        mx, mz = (A2[0] + B2[0]) / 2, (A2[1] + B2[1]) / 2; lw = min(L * .8, 1.0 + .42 * len(sign))
        lo.seg((mx - ux / L * lw / 2 + nx * .05, hv + .55, mz - uz / L * lw / 2 + nz * .05), (mx + ux / L * lw / 2 + nx * .05, hv + .55, mz + uz / L * lw / 2 + nz * .05), .08, .7, M["letrf"])
        letrero(sign.upper()[:24], (mx + nx * .12, hv + .55, mz + nz * .12), (nx, nz), .42 if len(sign) < 14 else .32)
    elif o["t"] == "local_poly":
        P2 = o["p"]; i = max(range(len(P2)), key=lambda i: (P2[i][1] + P2[(i + 1) % len(P2)][1]) - .3 * (P2[i][0] + P2[(i + 1) % len(P2)][0]))
        a, b = P2[i], P2[(i + 1) % len(P2)]; ux, uz = b[0] - a[0], b[1] - a[1]; L = math.hypot(ux, uz) or 1
        cx = sum(p[0] for p in P2) / len(P2); cz = sum(p[1] for p in P2) / len(P2); nx, nz = uz / L, -ux / L
        if nx * ((a[0] + b[0]) / 2 - cx) + nz * ((a[1] + b[1]) / 2 - cz) < 0: nx, nz = -nx, -nz
        letrero(sign.upper()[:24], ((a[0] + b[0]) / 2 + nx * .3, 5.2, (a[1] + b[1]) / 2 + nz * .3), (nx, nz), .7)
# letrero principal del supermercado (genérico) sobre el acceso
letrero("SUPERMERCADO", (12.15, 6.3, 82.6 + .3), (0, 1), 1.1)
lo.build()

# frontis exterior: alero (piso), estacionamiento, rampa, caseta de escaleras, vereda de O'Higgins
G = "Frontis"; fe = MB("frontis_suelo", G)
fe.slab([(-58.2, 82.6), (20.3, 82.6), (20.3, 91.25), (-58.2, 91.25)], 0, .15, M["acera"], M["horm"], M["horm"])
fe.slab([(-58.2, 91.25), (-51.85, 91.25), (-51.85, 120.55), (-58.2, 120.55)], 0, .15, M["acera"], M["horm"], M["horm"])
fe.slab([(20.3, 82.6), (39.8, 86.7), (40.2, 101.75), (35.5, 94.35), (21, 94.35), (20.3, 91.25)], 0, .15, M["acera"], M["horm"], M["horm"])
RX0, RX1, RZ0, RZ1 = -24.0, -8.2, 106.5, 117.5      # rampa vehicular al subterráneo (foto aérea)
for P in ([(-51.85, 91.25), (21, 91.25), (21, RZ0), (-51.85, RZ0)], [(-51.85, RZ0), (RX0, RZ0), (RX0, RZ1), (-51.85, RZ1)], [(RX1, RZ0), (21, RZ0), (21, RZ1), (RX1, RZ1)], [(-51.85, RZ1), (21, RZ1), (21, 120.55), (-51.85, 120.55)]):
    fe.poly(P, .02, M["asf"])
for x in [-50.5 + 2.5 * k for k in range(29)]:
    if not (-32 < x < -22): fe.box(x - .06, x + .06, .02, .03, 99.0, 104.0, M["linea"])
    if not (RX0 - 1 < x < RX1 + 1): fe.box(x - .06, x + .06, .02, .03, 115.0, 120.0, M["linea"])
fe.box(-51.0, 20.0, .02, .03, 104.0, 104.12, M["linea"])
fe.face([(RX0, .0, RZ0), (RX1, .0, RZ0), (RX1, -3.2, RZ1), (RX0, -3.2, RZ1)], M["rampa"], (0, 1, 0))
for x in (RX0, RX1): fe.box(x - .1, x + .1, -3.2, 1.0, RZ0, RZ1, M["horm"])
fe.box(RX0, RX1, -3.2, 1.0, RZ1, RZ1 + .2, M["horm"])
# caseta de escaleras mecánicas (fuera del alero)
cx0, cx1, cz0, cz1 = -31.4, -22.7, 91.25, 98.5
for x in (cx0, cx1):
    fe.face([(x, .05, cz0), (x, .05, cz1), (x, 4.6, cz1), (x, 5.2, cz0)], M["vidrioc"], None)
    for z in [cz0 + k * (cz1 - cz0) / 4 for k in range(5)]: fe.box(x - .05, x + .05, 0, 5.2 - .6 * (z - cz0) / (cz1 - cz0), z - .05, z + .05, M["marco"])
fe.face([(cx0, .05, cz1), (cx1, .05, cz1), (cx1, 4.6, cz1), (cx0, 4.6, cz1)], M["vidrioc"], None)
fe.face([(cx0 + .6, .03, cz0 + .4), (cx1 - .6, .03, cz0 + .4), (cx1 - .6, .03, cz1 - .3), (cx0 + .6, .03, cz1 - .3)], M["rampa"], (0, 1, 0))
for x in (cx0 + 1.6, cx0 + 3.3, cx1 - 3.3, cx1 - 1.6):
    fe.seg((x, 1.0, cz0 + .5), (x, -3.0, cz1 - .4), .9, .08, M["escalon"]); fe.seg((x - .48, 1.9, cz0 + .5), (x - .48, -2.1, cz1 - .4), .05, .9, M["vidrioc"]); fe.seg((x + .48, 1.9, cz0 + .5), (x + .48, -2.1, cz1 - .4), .05, .9, M["vidrioc"])
fe.box(cx0, cx1, 4.35, 5.2, cz0 - .02, cz0 + .1, M["letrf"])                       # faja opaca: el letrero no se lee desde atrás
letrero("ESTACIONAMIENTO", ((cx0 + cx1) / 2, 4.78, cz0 - .07), (0, -1), .45)
# topes de estacionamiento y postes de iluminación (SUPUESTO)
for x in [-50.5 + 2.5 * k for k in range(28)]:
    xc = x + 1.25
    if not (-33 < xc < -21): fe.box(xc - .8, xc + .8, .02, .14, 103.25, 103.4, M["horm"])
    if not (RX0 - 1 < xc < RX1 + 1) and xc < 20: fe.box(xc - .8, xc + .8, .02, .14, 119.45, 119.6, M["horm"])
for px in (-45.0, -15.0, 12.0):
    pz = 104.06; fe.box(px - .25, px + .25, 0, .5, pz - .25, pz + .25, M["horm"]); fe.cyl((px, .5, pz), (px, 8.0, pz), .07, M["galv"], 10)
    for sg in (1, -1):
        fe.seg((px, 7.9, pz), (px + sg * 1.3, 8.05, pz), .06, .06, M["galv"])
        fe.box(px + sg * 1.3 - .35, px + sg * 1.3 + .35, 7.95, 8.1, pz - .16, pz + .16, M["negro"]); fe.face([(px + sg * 1.3 - .3, 7.94, pz - .12), (px + sg * 1.3 + .3, 7.94, pz - .12), (px + sg * 1.3 + .3, 7.94, pz + .12), (px + sg * 1.3 - .3, 7.94, pz + .12)], M["ledal"], (0, -1, 0))
# barandas sobre los muros de la rampa
for x in (RX0, RX1):
    for z in [RZ0 + 1.375 * k for k in range(9)]: fe.cyl((x, 1.0, z), (x, 1.9, z), .025, M["galv"], 6)
    fe.cyl((x, 1.9, RZ0), (x, 1.9, RZ1), .03, M["galv"], 8); fe.cyl((x, 1.45, RZ0), (x, 1.45, RZ1), .02, M["galv"], 6)
# ---- alero v77 (fotos fachada/mallchino, salud dental, sobreelalero, automotora) ----
# cielo suspendido de listones de madera clara a 4,5 m y faja oscura alta en el borde; la cubierta sigue en la cota del plano (7,55). Alturas: SUPUESTO por fotos.
AY = 4.5; al = MB("alero_v77", "Frontis")
def cielo_listones(x0, x1, z0, z1, eje):
    al.box(x0, x1, AY + .12, AY + .14, z0, z1, M["faja"])                                  # tablero oscuro sobre los listones
    if eje == "x":
        z = z0 + .06
        while z < z1 - .03: al.box(x0, x1, AY, AY + .04, z - .035, z + .035, M["listc"]); z += .11
        for xx in [x0 + 1.2 * k for k in range(int((x1 - x0) / 1.2) + 1)]: al.box(xx - .02, xx + .02, AY + .04, AY + .12, z0, z1, M["galv"])
    else:
        x = x0 + .06
        while x < x1 - .03: al.box(x - .035, x + .035, AY, AY + .04, z0, z1, M["listc"]); x += .11
        for zz in [z0 + 1.2 * k for k in range(int((z1 - z0) / 1.2) + 1)]: al.box(x0, x1, AY + .04, AY + .12, zz - .02, zz + .02, M["galv"])
cielo_listones(-58.2, 20.3, 82.75, 91.2, "x")
cielo_listones(-58.2, -51.9, 91.2, 120.5, "z")
def faja(a, b, n):
    (x0, z0), (x1, z1) = a, b; nx, nz = n; t = .16
    pts = lambda o: [(x0 + nx * o, 0, z0 + nz * o), (x1 + nx * o, 0, z1 + nz * o)]
    xs = sorted([x0, x1, x0 + nx * t, x1 + nx * t]); zs = sorted([z0, z1, z0 + nz * t, z1 + nz * t])
    al.box(xs[0], xs[-1], AY - .05, AY + 1.15, zs[0], zs[-1], M["faja"])                   # faja oscura (~1,2 m, foto mallchinoautomotora)
    al.box(xs[0] + (.02 if nx else 0), xs[-1] - (.02 if nx else 0), AY + 1.15, 7.95, zs[0] + (.02 if nz else 0), zs[-1] - (.02 if nz else 0), M["estgris"])   # banda gris clara sobre la faja
    L_ = math.hypot(x1 - x0, z1 - z0); ux, uz = (x1 - x0) / L_, (z1 - z0) / L_
    for k in range(1, int(L_ / 2.4)):                                                       # juntas de los paneles
        px, pz = x0 + ux * 2.4 * k + nx * (t + .003), z0 + uz * 2.4 * k + nz * (t + .003)
        al.box(px - .006, px + .006, AY, AY + 1.15, pz - .006, pz + .006, M["negro"])
    al.box(xs[0] - .02, xs[-1] + .02, AY - .08, AY - .02, zs[0] - .02, zs[-1] + .02, M["marco"])  # remate inferior de aluminio
    al.box(xs[0] - .03, xs[-1] + .03, 7.95, 8.0, zs[0] - .03, zs[-1] + .03, M["galv"])          # coronación
faja((-58.2, 91.2), (20.3, 91.2), (0, 1))
faja((-51.9, 91.2), (-51.9, 120.5), (1, 0))
faja((-58.2, 120.5), (-51.9, 120.5), (0, 1))
faja((20.3, 82.6), (20.3, 91.2), (1, 0))
for x in [-56 + 3.5 * k for k in range(22)]:                                                 # luminarias empotradas en el cielo de listones
    for zz in (85.0, 88.6): al.disk((x, AY - .005, zz), .09, M["ledal"], False, 12); al.cyl((x, AY - .004, zz), (x, AY + .02, zz), .11, M["marco"], 12)
for zz in [93 + 3.5 * k for k in range(8)]: al.disk((-55.05, AY - .005, zz), .09, M["ledal"], False, 12)
o_al = al.build()
if o_al is not None:                                                                         # biseles y normales ponderadas (skill)
    wd = o_al.modifiers.new("Weld", "WELD"); wd.merge_threshold = .0005
    bv = o_al.modifiers.new("Bevel", "BEVEL"); bv.width = .006; bv.segments = 2; bv.limit_method = "ANGLE"; bv.angle_limit = math.radians(30)
    try: bv.harden_normals = True
    except Exception: pass
    wn = o_al.modifiers.new("WeightedNormal", "WEIGHTED_NORMAL"); wn.keep_sharp = True
fe.build()

# v85 (Cristian, fotos y videos del recorrido 24-11): en la trastienda las bandejas van al centro del pasillo y las dibuja el kit
#   (tras_blender): se quitan las del plano que corrían en paralelo (pasillo sur, corredor poniente y recepción) y se empalman las que siguen
O[:] = [o for o in O if o.get("id") not in ("o772", "o777", "bj1", "bj2", "bj3", "bk4", "bk5", "bk6")]
for o in O:
    if o.get("id") == "o773": o.update(z1=3.66, h=6.1, h2=5.3)        # paso a bodega: baja desde las bandejas del pasillo sur
    elif o.get("id") == "bk1": o.update(x1=-56.6)                        # franja frontal: sale de la bandeja central del corredor
# ---------------- bandejas portacables (rejilla) ----------------
G = "Arriostramientos_MEP"; bj = MB("bandejas", G)
for o in by_t("bandeja"):
    x1, z1, x2, z2, w = o["x1"], o["z1"], o["x2"], o["z2"], o.get("w", .3); h1 = o.get("h", 5.3); h2 = o.get("h2", h1)
    L = math.hypot(x2 - x1, z2 - z1) or 1; nx, nz = (z2 - z1) / L * w / 2, -(x2 - x1) / L * w / 2
    uv = [(0, 0), (L / .5, 0), (L / .5, w / .5), (0, w / .5)]
    bj.face([(x1 + nx, h1, z1 + nz), (x2 + nx, h2, z2 + nz), (x2 - nx, h2, z2 - nz), (x1 - nx, h1, z1 - nz)], M["rejilla"], (0, 1, 0), uv)
    bj.seg((x1, h1 + .03, z1), (x2, h2 + .03, z2), w * .7, .05, M["cable"])                                          # cables
    bj.face([(x1 + nx, h1, z1 + nz), (x1 - nx, h1, z1 - nz), (x2 - nx, h2, z2 - nz), (x2 + nx, h2, z2 + nz)], M["rejilla"], (0, -1, 0), uv[::-1])
    for sg in (1, -1):
        uv2 = [(0, 0), (L / .5, 0), (L / .5, .2), (0, .2)]
        bj.face([(x1 + nx * sg, h1, z1 + nz * sg), (x2 + nx * sg, h2, z2 + nz * sg), (x2 + nx * sg, h2 + .1, z2 + nz * sg), (x1 + nx * sg, h1 + .1, z1 + nz * sg)], M["rejilla"], None, uv2)
    n = max(1, int(L / 2.5))
    for k in range(n + 1):
        t = k / n; px, pz = x1 + (x2 - x1) * t, z1 + (z2 - z1) * t; hh = h1 + (h2 - h1) * t
        bj.seg((px + nx * 1.15, hh - .03, pz + nz * 1.15), (px - nx * 1.15, hh - .03, pz - nz * 1.15), .04, .04, M["galv"])
        rt = under(px, pz, .3) if not (N2[0] <= px <= N2[1] and N2[2] <= pz <= N2[3]) else 3.2
        if rt > hh + .1:
            for sg in (1, -1): bj.cyl((px + nx * 1.15 * sg, hh - .03, pz + nz * 1.15 * sg), (px + nx * 1.15 * sg, rt, pz + nz * 1.15 * sg), .006, M["galv"], 4)
bj.build()

# =====================================================================
# 7) RED HÚMEDA (rociadores, matrices, montantes, gabinetes, red seca) — diseño v76 desde el plano
# =====================================================================
G = "Red_Humeda"; rh = MB("red_humeda", G); rk = MB("rociadores", G)
# v80 (Cristian): la entrada de la red (válvula y montante principal) quedaba en la mitad del pasillo (x −57): se pega al muro poniente
for o in O:
    if o.get("id") == "rh2": o["x2"] = -58.8
    elif o.get("id") == "rh3": o["x"], o["h"] = -58.8, 1.45
    elif o.get("id") == "rh4": o["x"] = -58.8
O.append({"id": "rh4b", "t": "matriz", "n": "Unión montante principal → matriz bajo el 2º nivel", "x1": -58.8, "z1": 66.5, "x2": -57.0, "z2": 66.5, "h": 3.05, "dn": 150, "L": "red_humeda"})
# v85 (Cristian, fotos «redhumedaybandejadecables…» y videos del recorrido): dos matrices por la trastienda.
#   Pasillo sur: A junto a los pilares del muro de la calle y B junto al muro de la sala, la bandeja al centro.
#   Corredor poniente: A y B juntas por el lado del muro poniente; en el pilar del borde del 2º nivel (z 18) A baja bajo la losa y sigue sola
#   hasta recepción, y B sube y sigue sobre el 2º nivel (alimenta la sala norte). [SUPUESTO: recorrido de B sobre el 2º nivel, no visible]
XA, XB, HH, HL, ZA_, ZB_ = -58.15, -57.8, 6.5, 3.08, 2.9, 4.4
O[:] = [o for o in O if o.get("id") not in ("rh4b", "rh5", "rh6", "rh7", "rh8", "rh9", "rh10", "rh11", "rh14", "rh119", "rh120", "rh121")]
for o in O:
    i_ = o.get("id")
    if i_ == "rh4": o["h2"] = HL
    elif i_ == "rh12": o["x1"] = XB
    elif i_ == "rh13": o.update(x1=XB, h=HH)
    elif i_ in ("rh122", "rh16", "rh17"): o["x1"] = XA
def _t(id_, t, dn, x1, z1, x2, z2, h, n, **kw):
    d = {"id": id_, "t": t, "dn": dn, "x1": x1, "z1": z1, "x2": x2, "z2": z2, "h": h, "n": n, "L": "red_humeda"}; d.update(kw); O.append(d)
def _m(id_, x, z, h, h2, dn, n): O.append({"id": id_, "t": "montante", "x": x, "z": z, "h": h, "h2": h2, "dn": dn, "w": .3, "l": .3, "a": 0, "n": n, "L": "red_humeda"})
_t("v85a1", "matriz", 150, -58.8, 66.5, XA, 66.5, HL, "Unión montante principal → matriz A")
_t("v85a2", "ramal", 100, XA, 69.5, XA, 17.9, HL, "Matriz A bajo el 2º nivel (sola hasta recepción)")
_m("v85a3", XA, 17.9, HL, HH, 100, "Matriz A: baja junto al pilar del borde del 2º nivel")
_t("v85a4", "ramal", 100, XA, 17.9, XA, ZA_, HH, "Matriz A corredor poniente (lado muro)")
_t("v85a5", "ramal", 100, XA, ZA_, -3.0, ZA_, HH, "Matriz A pasillo sur (junto a los pilares)")
_t("v85x1", "matriz", 100, -3.0, ZA_, -3.0, ZB_, HH, "Cruce A–B junto al montante de bombas")
_t("v85b1", "ramal", 100, -3.0, ZB_, XB, ZB_, HH, "Matriz B pasillo sur (junto al muro de la sala)")
_t("v85b2", "ramal", 100, XB, ZB_, XB, 17.9, HH, "Matriz B corredor poniente")
_t("v85b3", "matriz", 100, XB, 17.9, XB, 65.5, HH, "Matriz B sobre el 2º nivel [SUPUESTO]")
_t("v85s1", "matriz", 100, -3.0, 3.3, 38.0, 3.3, 6.5, "Matriz sur bodega")
_m("v85r1", XA, 69.5, HL, 6.5, 150, "Matriz A sube al salir del 2º nivel (recepción)")
_t("v85r2", "matriz", 150, XA, 69.5, XA, 78.3, 6.5, "Matriz A hacia el frente / recepción")
RAD = {150: .084, 100: .057, 80: .045, 65: .038, 50: .03, 40: .024, 32: .021, 25: .017}
def rad(o): return RAD.get(int(o.get("dn", 50)), .03)
CIELOS = [(o["p"], o.get("h", 3.0)) for o in by_t("cielo")]
def techo_colgador(px, pz, h):
    if N2[0] - .1 <= px <= N2[1] + .1 and N2[2] <= pz <= N2[3] and h < 3.4: return 3.2      # bajo la losa del 2º nivel
    return under(px, pz, .25)
def colgadores(p0, p1, h0, h1, r, paso=3.0):
    L_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1]); n = max(1, int(L_ / paso))
    for k in range(n + 1):
        t = (k + .5) / (n + 1); px, pz = p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t; hh = h0 + (h1 - h0) * t
        yt = techo_colgador(px, pz, hh)
        if yt > hh + r + .05:
            rh.cyl((px, hh + r, pz), (px, yt, pz), .005, M["galv"], 4); rh.cyl((px, hh - r - .012, pz), (px, hh + r + .012, pz), r + .012, M["galv"], 8)
TUBOS = []; NHEAD = 0
for o in by_t("matriz", "ramal", "redseca"):
    r = rad(o); h1 = o.get("h", 6.5); h2 = o.get("h2", h1); p0, p1 = (o["x1"], o["z1"]), (o["x2"], o["z2"])
    rh.cyl((p0[0], h1, p0[1]), (p1[0], h2, p1[1]), r, M["rojo"], 12 if r > .05 else 8); TUBOS.append((p0, p1, h1, r))
    L_ = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    if L_ < .05: continue
    ux_, uz_ = (p1[0] - p0[0]) / L_, (p1[1] - p0[1]) / L_
    if o["t"] == "matriz":                                                     # coples ranurados cada 6 m
        for k in range(1, int(L_ / 6) + 1):
            px, pz = p0[0] + ux_ * 6 * k, p0[1] + uz_ * 6 * k
            if 6 * k < L_ - .2: rh.cyl((px - ux_ * .04, h1, pz - uz_ * .04), (px + ux_ * .04, h1, pz + uz_ * .04), r * 1.22, M["rojo"], 12 if r > .05 else 8)
    if h1 > 1.5: colgadores(p0, p1, h1, h2, r)
    if o["t"] == "ramal":                                                      # rociadores colgantes
        paso, ini = o.get("paso", 3.0), o.get("ini", 1.5); d = ini
        while d <= L_ - .2:
            px, pz = p0[0] + ux_ * d, p0[1] + uz_ * d; hh = h1 + (h2 - h1) * d / L_
            yb = hh - r - .1
            for P, hc in CIELOS:
                if inpoly(px, pz, P) and hh > hc: yb = hc - .03                # atraviesa el cielo falso
            rk.cyl((px, hh - r * .5, pz), (px, yb + .03, pz), .011, M["rojo"], 6)          # niple
            rk.cyl((px, yb + .045, pz), (px, yb + .005, pz), .016, M["bronce"], 6)        # cuerpo
            for sg in (1, -1): rk.seg((px + sg * .014, yb + .045, pz), (px + sg * .014, yb - .005, pz), .004, .004, M["bronce"])   # marco
            rk.cyl((px, yb - .005, pz), (px, yb - .009, pz), .028, M["bronce"], 10); rk.disk((px, yb - .009, pz), .028, M["bronce"], False, 10)  # deflector
            rk.cyl((px, yb + .012, pz), (px, yb - .002, pz), .005, M["rojo"], 4)                                                 # ampolleta
            d += paso; NHEAD += 1
for o in by_t("montante"):
    r = rad(o); x, z, ha, hb = o["x"], o["z"], o.get("h", 1), o.get("h2", 6.5)
    rh.cyl((x, min(ha, hb) - r, z), (x, max(ha, hb) + r, z), r, M["rojo"], 12)
    for yy in (ha, hb): rh.cyl((x, yy - r * 1.4, z), (x, yy + r * 1.4, z), r * 1.15, M["rojo"], 12)                  # codos / tees
    for yy in [y for y in (1.2, 3.0, 5.0) if min(ha, hb) + .3 < y < max(ha, hb) - .3]:
        rh.seg((x - .25, yy, z), (x + .25, yy, z), .04, .04, M["galv"]); rh.cyl((x, yy - .03, z), (x, yy + .03, z), r + .012, M["galv"], 10)   # abrazaderas
for o in by_t("acometida"):
    x, z, h = o["x"], o["z"], o.get("h", 1.0); r = .084
    rh.cyl((x, 0, z), (x, h + r, z), r, M["rojo"], 12); rh.cyl((x, .3, z), (x, .34, z), r * 1.6, M["rojo"], 12); rh.cyl((x, h - r * 1.3, z), (x, h + r * 1.3, z), r * 1.15, M["rojo"], 12)
    rh.box(x - .3, x + .3, 0, .06, z - .3, z + .3, M["horm2"])
for o in by_t("valvula"):
    x, z, h = o["x"], o["z"], o.get("h", 1.0); w_ = min(o.get("w", .4), .45) / 2
    rh.box(x - w_, x + w_, h - .14, h + .14, z - .12, z + .12, M["rojo"])
    rh.cyl((x, h + .14, z), (x, h + .45, z), .015, M["galv"], 6); rh.cyl((x, h + .45, z), (x, h + .47, z), .14, M["negro"], 12)
    rh.cyl((x + w_, h + .05, z), (x + w_ + .1, h + .05, z), .008, M["galv"], 6); rh.cyl((x + w_ + .1, h + .05, z - .02), (x + w_ + .1, h + .05, z + .02), .05, M["letrb"], 10)   # manómetro
for o in by_t("gabinete"):
    if abs(o["x"] + .05) < .3 and abs(o["z"] - 7.5) < .5: continue   # v80 (Cristian): se elimina el gabinete de la reja de entrada a la bodega
    if o.get("id") in ("rh138", "rh139"):   # v84: los gabinetes del corredor poniente quedaban dentro de los pilares (z 10,47 y 48,95): van montados en la cara del pilar hacia el pasillo
        pz_ = {"rh138": 10.47, "rh139": 48.95}[o["id"]]; o = dict(o, x=-58.35 + o.get("l", .25) / 2 + .01, z=pz_)
    a_ = math.radians(o.get("a", 0)); f = (math.cos(a_), math.sin(a_)); t_ = (-f[1], f[0]); w_, dp, ht = o.get("w", .8) / 2, o.get("l", .25), o.get("h", 1.7)
    cx, cz = o["x"], o["z"]; yb = ht - .85
    Q = lambda u, v: (cx + t_[0] * u + f[0] * v, cz + t_[1] * u + f[1] * v)
    rh.slab([Q(-w_, -dp / 2), Q(w_, -dp / 2), Q(w_, dp / 2), Q(-w_, dp / 2)], yb, ht, M["rojo"], M["rojo"], M["rojo"])
    A_, B_ = Q(-w_ + .08, dp / 2 + .004), Q(w_ - .08, dp / 2 + .004)
    rh.face([(A_[0], yb + .12, A_[1]), (B_[0], yb + .12, B_[1]), (B_[0], ht - .08, B_[1]), (A_[0], ht - .08, A_[1])], M["vidrioc"], (f[0], 0, f[1]))
    for k in range(3):                                                         # manguera enrollada (vista por el vidrio)
        cc = Q(0, .02); rh.cyl((cc[0], yb + .2 + k * .14, cc[1]), (cc[0], yb + .3 + k * .14, cc[1]), .25 - k * .02, M["rojo"], 12)
    letrero("RED HÚMEDA", (Q(0, -dp / 2 + .03)[0], ht + .12, Q(0, -dp / 2 + .03)[1]), f, .09, G, M["rojo"])
    # conexión a la cañería más cercana (sube junto al muro y empalma)
    bk = Q(0, -dp / 2 + .06); best = None
    for (p0, p1, hh, r) in TUBOS:
        if hh < ht + .3: continue
        vx, vz = p1[0] - p0[0], p1[1] - p0[1]; LL = vx * vx + vz * vz or 1
        t = max(0, min(1, ((bk[0] - p0[0]) * vx + (bk[1] - p0[1]) * vz) / LL)); nxp, nzp = p0[0] + vx * t, p0[1] + vz * t
        dd = math.hypot(nxp - bk[0], nzp - bk[1]) + abs(hh - ht) * .3
        if best is None or dd < best[0]: best = (dd, nxp, nzp, hh)
    if best:
        _, nxp, nzp, hh = best; r = .03
        rh.cyl((bk[0], ht, bk[1]), (bk[0], hh, bk[1]), r, M["rojo"], 8); rh.cyl((bk[0], hh, bk[1]), (nxp, hh, nzp), r, M["rojo"], 8)
        for yy in [ht + .8 + 2.0 * k for k in range(int((hh - ht - .8) / 2.0) + 1)]: rh.seg((bk[0] - f[0] * .05, yy, bk[1] - f[1] * .05), (bk[0] - f[0] * .09, yy, bk[1] - f[1] * .09), .1, .03, M["galv"])
for o in by_t("siamesa"):
    a_ = math.radians(o.get("a", 90)); f = (math.cos(a_), math.sin(a_)); t_ = (-f[1], f[0]); x, z, h = o["x"], o["z"], o.get("h", .9)
    Q = lambda u, v: (x + t_[0] * u + f[0] * v, z + t_[1] * u + f[1] * v)
    rh.slab([Q(-.35, -.12), Q(.35, -.12), Q(.35, .02), Q(-.35, .02)], h - .3, h + .3, M["rojo"], M["rojo"], M["rojo"])
    for u in (-.16, .16):
        p0 = Q(u, .02); p1 = Q(u, .2); rh.cyl((p0[0], h, p0[1]), (p1[0], h, p1[1]), .045, M["bronce"], 12); p2 = Q(u, .23); rh.cyl((p1[0], h, p1[1]), (p2[0], h, p2[1]), .055, M["bronce"], 12)
    lp = Q(0, .03); letrero("RED SECA", (lp[0], h + .45, lp[1]), f, .12, G, M["rojo"])
# ---- v80 · montante de bombas (foto «trastienda salida de emergencia y red de incendio»): 6 cañerías verticales junto a la salida de emergencia,
#      colector arriba y unión a la matriz sur (antes era un objeto del simulador que no conectaba con nada) ----
XB = [-4.25, -3.99, -3.73, -3.47, -3.21, -2.95]; ZB = 2.05; YC = 5.9; rB = .045
for xb in XB:
    rh.cyl((xb, 0, ZB), (xb, YC + rB, ZB), rB, M["rojo"], 12)
    rh.cyl((xb, .25, ZB), (xb, .3, ZB), rB * 1.5, M["rojo"], 12)                                   # brida de piso
    for yy in (1.15, 3.2):                                                                        # válvulas y coples ranurados
        rh.cyl((xb, yy - .05, ZB), (xb, yy + .05, ZB), rB * 1.25, M["rojo"], 12)
    rh.box(xb - .07, xb + .07, 1.35, 1.5, ZB - .07, ZB + .07, M["rojo"]); rh.cyl((xb, 1.5, ZB), (xb, 1.62, ZB), .01, M["galv"], 6); rh.cyl((xb, 1.62, ZB), (xb, 1.64, ZB), .08, M["negro"], 12)
    for yy in (2.2, 4.4): rh.seg((xb, yy, ZB - .07), (xb, yy, ZB - .55), .03, .03, M["galv"])        # abrazadera al muro
rh.cyl((XB[0] - .12, YC, ZB), (XB[-1] + .12, YC, ZB), .07, M["rojo"], 12)                        # colector
rh.cyl((XB[-1] + .12, YC, ZB), (XB[-1] + .12, YC, 3.3), .07, M["rojo"], 12)                      # hacia la matriz sur (z 3,3)
rh.cyl((XB[-1] + .12, YC, 3.3), (XB[-1] + .12, 6.5, 3.3), .07, M["rojo"], 12)
rh.cyl((XB[-1] + .12, 6.5 - .1, 3.3), (XB[-1] + .12, 6.5 + .1, 3.3), .09, M["rojo"], 12)           # tee de empalme
for xb in XB: rh.cyl((xb, YC - .08, ZB), (xb, YC + .08, ZB), rB * 1.3, M["rojo"], 12)
# ---- v80 · carrete de manguera de la ochava (fotos «manguera de incendio junto al pilar 3», «conexión de la manguera a la red húmeda»):
#      tambor rojo abierto en el muro con marco amarillo pintado, válvula, y bajada roja desde la matriz sur ----
OA, OB = (36.6, 1.5), (39.8, 4.3); oux, ouz = (OB[0] - OA[0]), (OB[1] - OA[1]); oL = math.hypot(oux, ouz); oux, ouz = oux / oL, ouz / oL
onx, onz = -ouz, oux                                                     # normal hacia el interior de la bodega
ocx, ocz = (OA[0] + OB[0]) / 2 + onx * .16, (OA[1] + OB[1]) / 2 + onz * .16
OQ = lambda u, v: (ocx + oux * u + onx * v, ocz + ouz * u + onz * v)
for (u0, u1, y0, y1) in [(-.5, -.42, .35, 2.05), (.42, .5, .35, 2.05), (-.5, .5, .35, .43), (-.5, .5, 1.97, 2.05)]:   # marco amarillo pintado
    a_, b_ = OQ(u0, .004), OQ(u1, .004); rh.face([(a_[0], y0, a_[1]), (b_[0], y0, b_[1]), (b_[0], y1, b_[1]), (a_[0], y1, a_[1])], M["amarillo"] if "amarillo" in M else M["rojo"], (onx, 0, onz))
hb = OQ(0, .08); rh.cyl((hb[0] - onx * .08, 1.25, hb[1] - onz * .08), (hb[0], 1.25, hb[1]), .03, M["galv"], 8)          # eje al muro
d0, d1 = OQ(0, .05), OQ(0, .2)
rh.cyl((d0[0], 1.25, d0[1]), (d0[0] + onx * .012, 1.25, d0[1] + onz * .012), .33, M["rojo"], 24)                           # disco trasero
rh.cyl((d1[0] - onx * .012, 1.25, d1[1] - onz * .012), (d1[0], 1.25, d1[1]), .33, M["rojo"], 24)                           # disco delantero
rh.cyl((d0[0], 1.25, d0[1]), (d1[0], 1.25, d1[1]), .2, M["rojo"], 20)                                                       # manguera enrollada
for k in range(6):                                                                                                         # rayos del disco
    an = k * math.pi / 3; ru, rv = math.cos(an) * .3, math.sin(an) * .3
    p0 = (d1[0], 1.25, d1[1]); p1 = (d1[0] + oux * ru, 1.25 + rv, d1[1] + ouz * ru); rh.seg(p0, p1, .03, .012, M["rojo"])
vb = OQ(.42, .06); rh.box(vb[0] - .06, vb[0] + .06, 1.55, 1.7, vb[1] - .06, vb[1] + .06, M["rojo"])                          # válvula
rh.cyl((vb[0], 1.7, vb[1]), (vb[0], 6.5, vb[1]), .03, M["rojo"], 8)                                                         # bajada desde la matriz
rh.cyl((vb[0], 6.5, vb[1]), (vb[0], 6.5, 3.3), .03, M["rojo"], 8)
rh.cyl((vb[0], 6.5, 3.3), (38.0, 6.5, 3.3), .03, M["rojo"], 8); rh.cyl((38.0, 6.5 - .07, 3.3), (38.0, 6.5 + .07, 3.3), .06, M["rojo"], 8)   # empalme al extremo de la matriz sur
for yy in (2.6, 4.2, 5.8): rh.seg((vb[0], yy, vb[1]), (vb[0] - onx * .08, yy, vb[1] - onz * .08), .06, .02, M["galv"])
rh.build(); rk.build()

# ---------------- exportar ----------------
kw = dict(filepath=OUT_GLB, export_format="GLB", export_yup=True, export_apply=True, export_cameras=False, export_lights=False, export_image_format="WEBP")
_win = bpy.context.window_manager.windows[0]; _area = next((a for a in _win.screen.areas if a.type == "VIEW_3D"), _win.screen.areas[0])
with bpy.context.temp_override(window=_win, area=_area, screen=_win.screen):
    try: bpy.ops.export_scene.gltf(export_image_quality=95, **kw)
    except TypeError: bpy.ops.export_scene.gltf(**kw)
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
tris = 0
for o in bpy.data.objects:
    if o.type == "MESH": o.data.calc_loop_triangles(); tris += len(o.data.loop_triangles)
result = {"rociadores": NHEAD, "glb": os.path.getsize(OUT_GLB), "objs": len(bpy.data.objects), "mats": len(bpy.data.materials), "tris": tris, "groups": list(GROUPS.keys())}
