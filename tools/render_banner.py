"""Render a rotating, shaded torus knot. Requires Pillow and Linux DejaVu fonts."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math
ROOT=Path(__file__).resolve().parents[1]
W,H,S=1100,430,2
T=math.tau
def font(n,b=False):
    return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans'+('-Bold' if b else '')+'.ttf',n*S)
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def sub(a,b): return add(a,mul(b,-1))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a): return mul(a,1/math.sqrt(sum(x*x for x in a)))
def center(t):
    r=1+.36*math.cos(3*t)
    return (r*math.cos(2*t),r*math.sin(2*t),.5*math.sin(3*t))
mesh=[]
for i in range(112):
    t=T*i/112;c=center(t)
    tangent=unit(sub(center(t+.001),center(t-.001)))
    n=unit(cross(tangent,(0,0,1)));b=cross(tangent,n)
    mesh.append([add(c,add(mul(n,.22*math.cos(T*j/14)),mul(b,.22*math.sin(T*j/14)))) for j in range(14)])
base=Image.new('RGB',(W*S,H*S),'#100f12');d=ImageDraw.Draw(base)
d.rounded_rectangle((S,S,(W-1)*S,(H-1)*S),radius=22*S,outline='#3e2a24',width=S)
for radius in (156,190):
    d.ellipse(((847-radius)*S,(214-radius)*S,(847+radius)*S,(214+radius)*S),outline='#332321',width=S)
d.line((48*S,49*S,79*S,49*S),fill='#ffb65b',width=3*S)
d.text((91*S,40*S),'AAYUSHTYAGI00  /  DEVELOPER',font=font(12),fill='#e5b48d')
d.text((45*S,106*S),'Aayush',font=font(65,True),fill='#fff0dd')
d.text((45*S,181*S),'Tyagi.',font=font(65,True),fill='#ffad63')
d.text((49*S,281*S),'Turning ideas into things you can use.',font=font(19),fill='#c8b9b4')
d.text((49*S,326*S),'WEB APPS   /   AI EXPLORATIONS   /   OPEN SOURCE',font=font(11),fill='#f58e79')
d.line((49*S,372*S,555*S,372*S),fill='#3e2a24',width=S)
d.text((49*S,389*S),'INDIA',font=font(10),fill='#8e807d')
d.text((399*S,389*S),'BUILD. LEARN. REPEAT.',font=font(10),fill='#8e807d')
frames=[]
for f in range(72):
    a=T*f/72
    def rotate(v):
        x,y,z=v
        x,z=x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
        return (x,y*math.cos(.45)-z*math.sin(.45),y*math.sin(.45)+z*math.cos(.45))
    verts=[[rotate(v) for v in row] for row in mesh]
    polys=[]
    for i in range(112):
        for j in range(14):
            vs=[verts[i][j],verts[(i+1)%112][j],verts[(i+1)%112][(j+1)%14],verts[i][(j+1)%14]]
            n=unit(cross(sub(vs[1],vs[0]),sub(vs[3],vs[0])))
            lum=max(0,-sum(x*y for x,y in zip(n,unit((-.5,-.7,-1)))))
            shine=lum**18
            color=tuple(min(255,int(c*(.26+.73*lum)+80*shine)) for c in (255,151+38*math.sin(T*i/112),89))
            pts=[((846+112*x/(1+z*.1))*S,(212+112*y/(1+z*.1))*S) for x,y,z in vs]
            polys.append((sum(v[2] for v in vs)/4,pts,color))
    im=base.copy();dr=ImageDraw.Draw(im)
    dr.ellipse((730*S,385*S,967*S,398*S),fill='#201717')
    for z,pts,color in sorted(polys,reverse=True,key=lambda p:p[0]): dr.polygon(pts,fill=color)
    frames.append(im.resize((W,H),Image.Resampling.LANCZOS))
frames[0].save(ROOT/'assets/banner-preview.png')
sample=Image.new('RGB',(W,H*4))
for k in range(4):sample.paste(frames[k*18],(0,H*k))
palette=sample.quantize(colors=192)
indexed=[im.quantize(palette=palette,dither=Image.Dither.NONE) for im in frames]
indexed[0].save(ROOT/'assets/hero-3d.gif',save_all=True,append_images=indexed[1:],duration=80,loop=0,optimize=True,disposal=1)
print('Rendered 72 frames: rotating shaded torus knot, 5.76-second loop.')
