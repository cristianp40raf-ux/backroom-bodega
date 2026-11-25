# Texturas del kit de trastienda (2K). Base CC0 ambientCG (Cardboard004, Wood066, Plastic010, DiamondPlate008A) + trazado propio sin marcas.
from PIL import Image, ImageDraw, ImageFilter, ImageOps
import numpy as np, random
R='/home/claude/pbr/raw4/'; O='tex/'; random.seed(7); np.random.seed(7)
def save(im,n): im.save(O+n+'.webp',quality=95)
def nrm_from_h(h,s=3.0):
    h=np.asarray(h,float)/255; gx=np.roll(h,-1,1)-np.roll(h,1,1); gy=np.roll(h,-1,0)-np.roll(h,1,0)
    n=np.dstack([-gx*s,gy*s,np.ones_like(h)]); n/=np.linalg.norm(n,axis=2,keepdims=True); return Image.fromarray(((n*.5+.5)*255).astype('uint8'))
# 1 · cartón: atlas 2x2 (kraft con cinta / kraft con etiqueta y flechas / caja blanca con bandas impresas genéricas / kraft oscuro gastado)
c=Image.open(R+'carton/Cardboard004_2K-JPG_Color.jpg').convert('RGB').resize((1024,1024))
a=np.asarray(c,float); L=a@[.3,.59,.11]; L/=L.mean()
def tone(col,k=.6): return Image.fromarray(np.clip(np.array(col)[None,None,:]*(L[...,None]**k),0,255).astype('uint8'))
A=Image.new('RGB',(2048,2048))
t0=tone((176,138,92)); d=ImageDraw.Draw(t0); d.rectangle([0,452,1023,572],fill=(196,170,128)); d.line([0,452,1023,452],fill=(150,128,96),width=3); d.line([0,572,1023,572],fill=(150,128,96),width=3)
t1=tone((168,130,86)); d=ImageDraw.Draw(t1); d.rectangle([90,120,470,380],fill=(238,236,228)); 
for i in range(24): x=120+i*13; d.rectangle([x,300,x+(3 if i%3 else 7),360],fill=(30,30,30))
for y in (160,200,240): d.rectangle([120,y,120+random.randint(180,320),y+18],fill=(70,70,70))
for k,x in enumerate((640,760)): d.polygon([(x,240),(x+40,170),(x+80,240),(x+55,240),(x+55,320),(x+25,320),(x+25,240)],fill=(40,36,30))
d.rectangle([600,640,960,700],fill=(40,36,30)); d.rectangle([0,452,1023,560],fill=(186,160,120))
t2=tone((226,224,218),.25); d=ImageDraw.Draw(t2); d.rectangle([0,0,1023,180],fill=(40,90,160)); d.rectangle([0,840,1023,1023],fill=(40,90,160)); d.rectangle([80,330,560,640],outline=(40,90,160),width=14); d.ellipse([650,360,930,640],fill=(220,120,40))
t3=tone((150,116,78),.8); d=ImageDraw.Draw(t3)
for i in range(30): x,y=random.randint(0,1000),random.randint(0,1000); d.ellipse([x,y,x+random.randint(20,90),y+random.randint(10,40)],fill=(132,102,70))
for i,t in enumerate((t0,t1,t2,t3)): A.paste(t,((i%2)*1024,(i//2)*1024))
save(A,'carton_atlas_diff')
cn=Image.open(R+'carton/Cardboard004_2K-JPG_NormalGL.jpg').convert('RGB').resize((1024,1024)); N=Image.new('RGB',(2048,2048))
for i in range(4): N.paste(cn,((i%2)*1024,(i//2)*1024))
save(N,'carton_atlas_norm')
# 2 · madera de pallet: pino sin tratar, claro
w=np.asarray(Image.open(R+'madera_pallet/Wood066_2K-JPG_Color.jpg').convert('RGB'),float); Lw=w@[.3,.59,.11]; Lw=Lw/Lw.mean()
save(Image.fromarray(np.clip(np.array([196,166,118])[None,None,:]*(Lw[...,None]**.55),0,255).astype('uint8')),'pino_diff')
save(Image.open(R+'madera_pallet/Wood066_2K-JPG_NormalGL.jpg').convert('RGB'),'pino_norm')
# 3 · montante perforado (tira 512x2048 = 0,9 m de alto por 8 cm): pintura blanca, perforaciones de lágrima cada 50 mm al centro y redondas a los lados
M=Image.new('L',(512,2048),235); d=ImageDraw.Draw(M); pp=2048/0.9*0.05
y=10
while y<2048:
    d.polygon([(256,y),(286,y+40),(278,y+70),(234,y+70),(226,y+40)],fill=25); d.ellipse([60,y+20,110,y+70],fill=25); d.ellipse([402,y+20,452,y+70],fill=25); y+=pp
H=M.filter(ImageFilter.GaussianBlur(2)); save(Image.merge('RGB',(M,M,M)),'montante_diff'); save(nrm_from_h(H,6),'montante_norm')
# 4 · bandeja plástica rosada de panadería (laterales con rombos) — base blanca, el color lo da el material
B=Image.new('RGB',(1024,256),(250,250,250)); d=ImageDraw.Draw(B); d.rectangle([0,0,1023,22],fill=(232,232,232)); d.rectangle([0,232,1023,255],fill=(232,232,232))
for i in range(15):
    if i==7: continue
    cx=36+i*68; cy=128; d.polygon([(cx,cy-52),(cx+22,cy),(cx,cy+52),(cx-22,cy)],fill=(110,90,100))
d.chord([432,-60,592,60],0,180,fill=(110,90,100)); save(B,'bandeja_diff')
# 5 · chapa diamante y plástico (para pallets plásticos)
save(Image.open(R+'diamante/DiamondPlate008A_2K-JPG_Color.jpg').convert('RGB'),'diamante_diff'); save(Image.open(R+'diamante/DiamondPlate008A_2K-JPG_NormalGL.jpg').convert('RGB'),'diamante_norm')
p=np.asarray(Image.open(R+'plastico/Plastic010_2K-JPG_Color.jpg').convert('L'),float); p=p/p.mean()
save(Image.fromarray(np.clip(235*(p**.5),0,255).astype('uint8')).convert('RGB'),'plastico_diff'); save(Image.open(R+'plastico/Plastic010_2K-JPG_NormalGL.jpg').convert('RGB'),'plastico_norm')
# 6 · film strech: ruido de arrugas (alfa en el material)
f=np.random.rand(256,256); f=Image.fromarray((f*255).astype('uint8')).resize((1024,1024),Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
f=ImageOps.autocontrast(f); save(Image.merge('RGB',(f,f,f)),'film_diff'); save(nrm_from_h(f,10),'film_norm')
print('ok')
