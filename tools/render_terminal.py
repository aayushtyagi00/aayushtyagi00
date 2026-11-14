"""Render a quiet, looping terminal text animation. Requires Pillow."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W,H=1100,82
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',17)
small=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',12)
messages=['Building web apps that solve real problems.','Exploring AI, one project at a time.','Always learning. Always building.']
frames=[];durations=[]
for msg in messages:
    for length in list(range(0,len(msg)+1,2))+[len(msg)]:
        im=Image.new('RGB',(W,H),'#0b171c');d=ImageDraw.Draw(im)
        d.line((0,0,W,0),fill='#244047',width=1)
        d.text((24,14),'aayush@github:~',font=small,fill='#7b9ba3')
        d.text((24,40),'❯ ',font=font,fill='#64d5cd')
        d.text((51,40),msg[:length],font=font,fill='#f2e6cf')
        x=51+d.textlength(msg[:length],font=font)
        d.rectangle((x+3,42,x+11,59),fill='#ffbd80')
        frames.append(im);durations.append(65)
    for visible in (False,True,False,True):
        im=frames[-1].copy();d=ImageDraw.Draw(im)
        d.rectangle((x+3,42,x+11,59),fill='#ffbd80' if visible else '#0b171c')
        frames.append(im);durations.append(400)
frames[0].save(ROOT/'assets/terminal.gif',save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=True,disposal=1)
print('Rendered terminal typing animation.')
