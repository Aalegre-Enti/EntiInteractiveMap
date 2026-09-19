from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.vector-work/img19-review'
OUT.mkdir(exist_ok=True)
zones={
 'north':(800,130,904,283),
 'west-junction':(340,425,505,565),
 'north-stair':(500,285,782,477),
 'east-stair':(739,310,1018,550),
 'classrooms':(242,545,434,790),
 'bathrooms':(537,545,751,815),
 'envelope':(0,0,1395,1040),
}
src=Image.open(ROOT/'OriginalFloorplan/img19.jpg').convert('RGBA')
vec=Image.open(OUT/'red-vector.png').convert('RGBA')
alpha=vec.getchannel('A').point(lambda x:int(x*.62))
vec.putalpha(alpha)
overlay=Image.alpha_composite(src,vec)
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',14)
for name,box in zones.items():
 scale=1 if name=='envelope' else 4
 for kind,im in [('source',src),('overlay',overlay)]:
  view=im.crop(box).resize(((box[2]-box[0])*scale,(box[3]-box[1])*scale))
  if scale>1:
   frame=Image.new('RGB',(view.width+42,view.height+32),'white')
   frame.paste(view,(42,32)); d=ImageDraw.Draw(frame)
   for x in range((box[0]//10+1)*10,box[2],10):
    px=(x-box[0])*scale+42
    d.text((px-12,8),str(x),font=font,fill='#17669a')
    d.line((px,28,px,frame.height),fill='#a9c7ce',width=1)
   for y in range((box[1]//10+1)*10,box[3],10):
    py=(y-box[1])*scale+32
    d.text((4,py-8),str(y),font=font,fill='#17669a')
    d.line((38,py,frame.width,py),fill='#a9c7ce',width=1)
   view=frame
  view.save(OUT/f'{name}-{kind}.png')
