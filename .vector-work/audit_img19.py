"""Check actual doorway clearances against a rendered wall-only layer."""
from pathlib import Path
import xml.etree.ElementTree as ET
from math import hypot
from PIL import Image
import json
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.vector-work/img19-review'
NS={'s':'http://www.w3.org/2000/svg'}
svg=ET.parse(ROOT/'img19-architectural.svg').getroot()
if not (OUT/'walls-only.png').exists():
    raise SystemExit('Render walls-only.svg first.')
mask=Image.open(OUT/'walls-only.png').convert('RGBA')
scale=mask.width/1395
findings=[]
for e in svg.find("s:g[@id='accesses']",NS):
    if e.tag.rsplit('}',1)[-1]!='line': continue
    a=(float(e.get('x1')),float(e.get('y1')))
    b=(float(e.get('x2')),float(e.get('y2')))
    n=hypot(b[0]-a[0],b[1]-a[1])
    margin=min(4,n*.24)
    hits=[]
    for i in range(101):
        t=(margin+(n-2*margin)*i/100)/n
        x=a[0]+(b[0]-a[0])*t; y=a[1]+(b[1]-a[1])*t
        if mask.getpixel((round(x*scale),round(y*scale)))[3]>100:
            hits.append([round(x,2),round(y,2)])
    if hits:
        findings.append({'opening':e.get('id','lift-access'), 'blocked_samples':len(hits),'first':hits[0],'last':hits[-1]})
print(json.dumps(findings,indent=2))
(OUT/'doorway-clearance-audit.json').write_text(json.dumps(findings,indent=2))
