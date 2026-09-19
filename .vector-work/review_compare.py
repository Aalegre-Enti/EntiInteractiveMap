from PIL import Image, ImageDraw
from pathlib import Path
p=Path(__file__).resolve().parent
source=Image.open(p.parent/'OriginalFloorplan/img12.jpg').convert('RGB')
vector=Image.open(p/'review-current.png').convert('RGB')
regions={
 'passage':(477,20,642,459),
 'auditorium':(613,242,915,470),
 'central':(310,374,522,665),
 'classrooms':(252,328,480,752),
 'lower':(288,687,778,920),
 'east':(761,308,1034,550),
 'spine':(437,470,672,652),
}
for name,box in regions.items():
 w,h=box[2]-box[0],box[3]-box[1]
 scale=3 if w<340 else 2
 canvas=Image.new('RGB',((w*2+14)*scale,(h+20)*scale),'#ffffff')
 draw=ImageDraw.Draw(canvas)
 for i,im in enumerate((source,vector)):
  xx=i*(w+14)*scale
  canvas.paste(im.crop(box).resize((w*scale,h*scale)),(xx,20*scale))
  draw.text((xx+5,1), ('SOURCE' if i==0 else 'SVG')+f'  {box}',fill='#333333')
  for x in range((box[0]//20+1)*20,box[2],20):
   px=xx+(x-box[0])*scale
   draw.line((px,12*scale,px,20*scale),fill='#448899')
   draw.text((px-6,7*scale),str(x),fill='#004455')
  for y in range((box[1]//20+1)*20,box[3],20):
   py=(y-box[1]+20)*scale
   draw.line((xx,py,xx+8,py),fill='#008899')
   draw.text((xx+1,py),str(y),fill='#006677')
 canvas.save(p/f'review-{name}.png')
print('Comparison images rendered')
