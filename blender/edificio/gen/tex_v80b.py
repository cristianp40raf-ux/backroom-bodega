# v80b: texturas de muro y pilar pintado más fieles a las fotos (hormigón en bruto pintado, sin manchas tipo camuflaje)
import numpy as np
from scipy.ndimage import gaussian_filter
from PIL import Image
rng = np.random.default_rng(80)
def ruido(h, w, s, wrap=True):
    n = rng.standard_normal((h, w)); n = gaussian_filter(n, s, mode='wrap' if wrap else 'reflect'); return (n - n.mean()) / (n.std() + 1e-9)
def fbm(h, w, ss, ws):
    return sum(wt * ruido(h, w, s) for s, wt in zip(ss, ws))
def guardar(a, n):
    Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).save('/home/claude/techo/tex2k/' + n + '.webp', quality=95)
# ---- muro bruto pintado: 2,4 m por baldosa (2048 px → 1,17 mm/px)
N = 2048; px = N / 2.4
base = np.array([.83, .825, .805])
t = .022 * fbm(N, N, [160, 50], [1, .4]) + .009 * fbm(N, N, [6, 2], [1, .6]) + .005 * ruido(N, N, .7)
# juntas de moldaje (horizontal cada 0,6 m, vertical cada 1,2 m), finas y tenues
y = np.arange(N)[:, None] / px; x = np.arange(N)[None, :] / px
dj = lambda u, p: np.minimum(u % p, p - u % p)
junta = np.exp(-(dj(y, .6) / .004) ** 2) * .05 + np.exp(-(dj(x, 1.2) / .004) ** 2) * .04
t -= junta
# poros (burbujas de hormigón bajo la pintura): puntos pequeños algo más oscuros
P = np.zeros((N, N)); idx = rng.integers(0, N, (2, 3500)); P[idx[0], idx[1]] = 1; P = gaussian_filter(P, 1.2, mode='wrap'); t -= P / P.max() * .07
# chorreado vertical muy leve
st = gaussian_filter(rng.standard_normal((1, N)), 3, mode='wrap'); st = np.repeat(st, N, 0) * (gaussian_filter(rng.standard_normal((N, N)), (200, 2), mode='wrap') > .02)
t -= np.abs(st) * .012
img = base[None, None, :] + t[..., None] * np.array([1, 1, 1.05])[None, None, :]
guardar(img, 'muro_bruto_diff')
# ---- franja gris inferior 0–0,9 m (2048×768): pintura gris gastada con suciedad del zócalo
H = 768; base_g = np.array([.37, .39, .40])
t = .014 * fbm(H, N, [80, 20], [1, .4]) + .008 * ruido(H, N, 1.5)
yy = np.arange(H)[:, None] / H   # 0 = arriba (0,9 m), 1 = piso
t -= np.clip((yy - .78) / .22, 0, 1) ** 1.5 * (.10 + .04 * ruido(H, N, 8))   # suciedad de los últimos 20 cm
P = np.zeros((H, N)); idx = rng.integers(0, [H, N], (900, 2)).T; P[idx[0], idx[1]] = 1; P = gaussian_filter(P, 1.4, mode='wrap'); t -= P / P.max() * .05
sc = np.zeros((H, N))   # rozaduras de carros/pallets: trazos horizontales claros y suaves a 15–35 cm
for _ in range(40):
    r0 = int(H * (1 - rng.uniform(.15, .38) / .9)); c0 = rng.integers(0, N); L = rng.integers(60, 400)
    sc[r0:r0 + 2, c0:min(N, c0 + L)] = 1
sc = gaussian_filter(sc, (1, 3), mode='wrap'); t += sc / (sc.max() + 1e-9) * .06
img = base_g[None, None, :] + t[..., None]
guardar(img, 'muro_gris_diff')
# ---- base pintada del pilar 0–2,35 m (512×2048, abajo = piso): blanco gastado uniforme (foto pilar6)
W, H = 512, 2048; base_p = np.array([.84, .835, .82])
t = .025 * fbm(H, W, [90, 25], [1, .5]) + .012 * ruido(H, W, 1.2)
yy = np.arange(H)[:, None] / H
t -= np.clip((yy - .9) / .1, 0, 1) ** 1.6 * (.12 + .04 * ruido(H, W, 6))       # suciedad del pie (24 cm)
for _ in range(18):   # manchas suaves (roces), poco contraste, borde difuso
    m = np.zeros((H, W)); r, c = rng.integers(0, H), rng.integers(0, W); m[r, c] = 1; m = gaussian_filter(m, rng.uniform(6, 18)); t -= m / m.max() * rng.uniform(.03, .07)
ed = np.minimum(np.arange(W), W - 1 - np.arange(W))[None, :] / W   # aristas gastadas: algo más grises
t -= np.exp(-ed / .012) * (.05 + .03 * np.clip(ruido(H, W, 3), 0, None))
img = base_p[None, None, :] + t[..., None]
for _ in range(9):    # salpicaduras de pintura azul (foto: puntos azules en la base)
    r = int(H * rng.uniform(.75, .97)); c = rng.integers(20, W - 20); rr = rng.uniform(4, 9)
    Y, X = np.ogrid[:H, :W]; mk = np.clip(1 - np.sqrt((Y - r) ** 2 + (X - c) ** 2) / rr, 0, 1) ** .5
    img = img * (1 - mk[..., None]) + mk[..., None] * np.array([.18, .32, .70])
guardar(img, 'pilar_pintura_diff')
print('ok')
