from PIL import Image, ImageDraw, ImageOps
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
im=Image.open(ROOT/'OriginalFloorplan/img25.jpg').convert('RGB')
dest=ROOT/'work-img25/review'
dest.mkdir(exist_ok=True)
boxes={'north':(330,15,915,150),'northwest':(145,70,405,300),'office':(210,235,525,500),'labpassage':(195,440,500,660),'west':(5,410,275,785),'south':(5,725,400,1020),'core':(420,545,755,825),'stairs':(475,265,980,550)}
for name,b in {'passage-door':(390,480,485,550),'office-door':(180,545,230,603),'classroom-door':(205,732,250,784)}.items():
    o=im.crop(b).resize(((b[2]-b[0])*7,(b[3]-b[1])*7))
    d=ImageDraw.Draw(o)
    for x in range((b[0]//10+1)*10,b[2],10):
        px=(x-b[0])*7
        d.line((px,0,px,o.height),fill='#68cbd5')
        d.text((px+1,1),str(x),fill='#002863')
    for y in range((b[1]//10+1)*10,b[3],10):
        py=(y-b[1])*7
        d.line((0,py,o.width,py),fill='#68cbd5')
        d.text((1,py+1),str(y),fill='#002863')
    o.save(dest/(name+'.png'))
for name, box in boxes.items():
    crop=im.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3))
    crop.save(dest/(name+'-source.png'))
    d=ImageDraw.Draw(crop)
    for x in range(((box[0]+24)//25)*25,box[2],25):
        xx=(x-box[0])*3
        d.line((xx,0,xx,crop.height),fill='#63bdd0',width=1)
        d.text((xx+2,2),str(x),fill='#005f99')
    for y in range(((box[1]+24)//25)*25,box[3],25):
        yy=(y-box[1])*3
        d.line((0,yy,crop.width,yy),fill='#63bdd0',width=1)
        d.text((2,yy+2),str(y),fill='#005f99')
    crop.save(dest/(name+'-grid.png'))

preview=ROOT/'work-img25/preview.png'
if preview.exists():
    trace=Image.open(preview).convert('RGB').resize(im.size)
    mask=ImageOps.invert(trace.convert('L')).point(lambda x:int(x*.72))
    overlay=Image.composite(Image.new('RGB',im.size,'#e40035'),im,mask)
    for name,box in boxes.items():
        overlay.crop(box).resize(((box[2]-box[0])*3,(box[3]-box[1])*3)).save(dest/(name+'-overlay.png'))
