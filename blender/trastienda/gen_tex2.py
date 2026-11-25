# v79 · texturas propias (sin marcas) según fotos de la trastienda
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np, random
O='tex/'; rnd=np.random.default_rng(79); random.seed(79)
def save(im,n): im.save(O+n+'.webp',quality=95, lossless=False)
def nrm(h,s):
    h=np.asarray(h,float)/255; gx=np.roll(h,-1,1)-np.roll(h,1,1); gy=np.roll(h,-1,0)-np.roll(h,1,0)
    n=np.dstack([-gx*s,gy*s,np.ones_like(h)]); n/=np.linalg.norm(n,axis=2,keepdims=True); return Image.fromarray(((n*.5+.5)*255).astype('uint8'))
def noise(w,h,sc,seed):
    r=np.random.default_rng(seed).random((max(2,h//sc),max(2,w//sc))); return np.asarray(Image.fromarray((r*255).astype('uint8')).resize((w,h),Image.BICUBIC),float)/255
# 1 · panel sándwich de cámara: módulo 1,15 m de ancho × 3,0 m de alto (1024×2672 → 1024×2048 escalado vertical). Junta machihembrada en los bordes,
#     microperfilado horizontal suave, marcas de carros/zapatos y suciedad en la base (0–35 cm), salpicaduras leves a media altura.
W,H=1024,2048; y=np.linspace(0,1,H)[:,None]; x=np.linspace(0,1,W)[None,:]
base=np.full((H,W),236.0)
base+= (noise(W,H,64,1)-.5)*6 + (noise(W,H,8,2)-.5)*3
hb=np.clip((y-(1-0.35/3.0))/(0.35/3.0),0,1)            # 0 arriba … 1 en el piso (y=1 abajo)
sucio=(noise(W,H,24,3)*.6+noise(W,H,6,4)*.4)
base-= hb**1.6*(38+30*sucio)
for k in range(9):                                       # rayas horizontales de carros/transpaletas a 15–40 cm
    yy=int(H*(1-random.uniform(.05,.13))); x0=random.randint(0,W-300); L=random.randint(120,700); 
    base[yy:yy+random.randint(2,5), x0:x0+L]-=random.uniform(18,40)
for k in range(5):                                       # manchas de manos cerca de 1,0–1,4 m
    cx,cy=random.randint(100,W-100),int(H*(1-random.uniform(.33,.47))); r=random.randint(25,60)
    yy,xx=np.ogrid[:H,:W]; m=((xx-cx)**2+(yy-cy)**2)<r*r; base[m]-=random.uniform(4,9)
J=np.zeros((H,W)); J[:, :6]=1; J[:, -6:]=1                # junta
base=np.where(J>0, 150, base)
rib=(np.sin(np.arange(H)/H*3.0/0.008*np.pi)[:,None]*.5+.5)*np.ones((1,W))   # microperfil cada 8 mm (solo en relieve)
img=np.clip(base,0,255); col=np.dstack([img*0.995,img,img*1.005]).clip(0,255).astype('uint8')
save(Image.fromarray(col),'panel_camara_diff')
hgt=(1-J)*200 + rib*12; hgt=Image.fromarray(hgt.clip(0,255).astype('uint8')).filter(ImageFilter.GaussianBlur(1.2)); save(nrm(hgt,5),'panel_camara_norm')
# 2 · sombra suave (alfa) para oclusión de contacto en 9 cortes: núcleo opaco, borde que se desvanece
S=256; a=np.zeros((S,S)); m=48; a[m:S-m,m:S-m]=1
a=np.asarray(Image.fromarray((a*255).astype('uint8')).filter(ImageFilter.GaussianBlur(26)),float)/255
a=(a/a.max())**1.3; rgba=np.dstack([np.zeros((S,S,3)),a*255]).astype('uint8'); Image.fromarray(rgba,'RGBA').save(O+'sombra_suave.png')
# 3 · malla de bandeja portacables (alambre blanco 50×100 mm, módulo 0,4 × 0,4 m), RGBA
M=Image.new('RGBA',(512,512),(0,0,0,0)); d=ImageDraw.Draw(M)
for i in range(0,513,64): d.line([i,0,i,512],fill=(238,240,240,255),width=7)        # 50 mm
for j in range(0,513,128): d.line([0,j,512,j],fill=(238,240,240,255),width=7)       # 100 mm
M.save(O+'malla_bandeja.png')
# 4 · jaba / canasto plástico (lateral con ranuras), base gris claro: el color lo da el material
B=Image.new('L',(512,256),210); d=ImageDraw.Draw(B)
d.rectangle([0,0,511,26],fill=235); d.rectangle([0,232,511,255],fill=235)
for i in range(11):
    for r in range(3): x0=22+i*44; y0=46+r*62; d.rounded_rectangle([x0,y0,x0+28,y0+44],radius=8,fill=40)
d.rounded_rectangle([200,6,312,22],radius=6,fill=60)
save(Image.merge('RGB',(B,B,B)),'jaba_diff'); save(nrm(B.filter(ImageFilter.GaussianBlur(2)),4),'jaba_norm')
# 5 · funda de bolardo/poste de baranda: franjas negras y blancas a 45°
F=Image.new('RGB',(256,256),(235,235,232)); d=ImageDraw.Draw(F)
for k in range(-256,512,64): d.polygon([(k,0),(k+32,0),(k+32+256,256),(k+256,256)],fill=(25,25,25))
save(F,'franjas_diff')
print('ok')
