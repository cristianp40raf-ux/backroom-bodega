# v93 · Oclusión de contacto del piso de TODO el edificio (v92: solo trastienda)
# v93: región x −62..42, Blender y −85..3 (sim z −3..85), rejilla 1040x880 (10 cm). Sin pallets/cargas/carros/grúas/personas.
# Post v93: gauss 1 px; s=smoothstep((ao−0,35)/(0,92−0,35)); sombra=1−0,6·(1−s); desvanecido 60 cm en bordes de la máscara; inversión vertical.
# (v92) Oclusión ambiental del piso de la trastienda (se ejecuta en Blender, por partes por el límite de 80 s del MCP).
# Entrada: tras_geo.glb (geometría visible exportada del sim: kit + edificio + trastienda + sala, sin personas ni vehículos)
# Se quitan las caras del piso (horizontales a ~0) de los oclusores; malla de bake = grilla 0,5 m solo donde hay piso a altura 0.
# Cycles AO bake dio un resultado que no correspondía a la geometría (píxeles junto a muros en blanco), así que se calcula
# con mathutils.bvhtree: 32 rayos coseno por píxel, distancia 1,5 m, peso 1-(d/1,5)*0,6. Rejilla 256x1024 sobre
# x −63,5..−44,5 / Blender y −80,5..0,5 (sim z 80,5..−0,5). Salida float32 fila 0 = Blender y −80,5.
# Post (fuera de Blender): desenfoque gaussiano 1 px, ×2 bilineal → 512x2048, inversión vertical, 1−0,85·(1−ao) → ao_piso.webp.
import bpy, mathutils, math, time, array
from mathutils.bvhtree import BVHTree
ns = bpy.app.driver_namespace
W, H = 256, 1024; X0, X1, Y0, Y1 = -63.5, -44.5, -80.5, 0.5
def preparar():
    dg = bpy.context.evaluated_depsgraph_get(); V = []; P = []
    for o in bpy.data.objects:
        if o.type != 'MESH' or not o.name.startswith('src_'): continue
        oe = o.evaluated_get(dg); me = oe.to_mesh(); mw = o.matrix_world; b = len(V)
        V += [mw @ v.co for v in me.vertices]; P += [[b + i for i in p.vertices] for p in me.polygons]; oe.to_mesh_clear()
    ns['ao_bvh'] = BVHTree.FromPolygons(V, P, all_triangles=False)
    cells = set()
    for p in bpy.data.objects['ao_piso_malla'].data.polygons: cells.add((int((p.center.x - X0) / .5), int((p.center.y - Y0) / .5)))
    ns['ao_cells'] = cells; ns['ao_buf'] = array.array('f', [1.0] * (W * H)); ns['ao_row'] = 0
def tramo(seg=62, salida=None):
    bvh = ns['ao_bvh']; N = 32; D = []
    for i in range(N):
        u = (i + .5) / N; v = (i * .618034) % 1; r = math.sqrt(u); th = 2 * math.pi * v; D.append((r * math.cos(th), r * math.sin(th), math.sqrt(max(0, 1 - u))))
    buf = ns['ao_buf']; cells = ns['ao_cells']; t = time.time(); row = ns['ao_row']
    while row < H and time.time() - t < seg:
        y = Y0 + (row + .5) / H * (Y1 - Y0); cy = int((y - Y0) / .5); rot = row * .37
        for col in range(W):
            x = X0 + (col + .5) / W * (X1 - X0)
            if (int((x - X0) / .5), cy) not in cells: continue
            p = mathutils.Vector((x, y, .01)); occ = 0.; a = rot + col * 1.3; ca, sa = math.cos(a), math.sin(a)
            for dx, dy, dz in D:
                h = bvh.ray_cast(p, mathutils.Vector((dx * ca - dy * sa, dx * sa + dy * ca, dz)), 1.5)
                if h[0] is not None: occ += 1 - (h[3] / 1.5) * .6
            buf[row * W + col] = 1 - occ / N
        row += 1
    ns['ao_row'] = row
    if row >= H and salida: open(salida, 'wb').write(buf.tobytes())
    return row
