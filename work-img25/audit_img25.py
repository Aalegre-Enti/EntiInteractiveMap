"""Check that manually positioned internal door openings are not filled by walls."""
from pathlib import Path
from math import hypot
import runpy, json

base=Path(__file__).resolve().parent
m=runpy.run_path(str(base/'trace_img25.py'))
walls=m['walls']; doors=m['door_records']
def pts(n):return [tuple(map(float,v.split(','))) for v in n.attrib['points'].split()]
def distance(p,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1]
    ll=vx*vx+vy*vy
    t=max(0,min(1,((p[0]-a[0])*vx+(p[1]-a[1])*vy)/ll)) if ll else 0
    return hypot(p[0]-a[0]-t*vx,p[1]-a[1]-t*vy)
def butt_stroke_hit(p,a,b,width):
    vx,vy=b[0]-a[0],b[1]-a[1]
    ll=vx*vx+vy*vy
    if not ll:return False
    t=((p[0]-a[0])*vx+(p[1]-a[1])*vy)/ll
    if t<0 or t>1:return False
    return abs(vx*(p[1]-a[1])-vy*(p[0]-a[0]))/ll**.5<width/2-.2
def inside(p,poly):
    yes=False
    for a,b in zip(poly,poly[1:]+poly[:1]):
        if (a[1]>p[1]) != (b[1]>p[1]):
            x=(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0]
            if p[0]<x:yes=not yes
    return yes
def hit(p,n):
    kind=n.tag.rsplit('}',1)[-1]
    if kind=='polygon':return inside(p,pts(n))
    if kind=='polyline':
        width=float(n.attrib.get('stroke-width',1))
        vs=pts(n)
        return any(butt_stroke_hit(p,a,b,width) for a,b in zip(vs,vs[1:]))
    if kind=='circle':
        return hypot(p[0]-float(n.attrib['cx']),p[1]-float(n.attrib['cy']))<float(n.attrib['r'])-.2
    return False
issues=[]
def gap(p,n):
    kind=n.tag.rsplit('}',1)[-1]
    if kind=='polygon':
        v=pts(n)
        return 0 if inside(p,v) else min(distance(p,a,b) for a,b in zip(v,v[1:]+v[:1]))
    if kind=='polyline':
        v=pts(n); w=float(n.attrib.get('stroke-width',1))
        return max(0,min(distance(p,a,b) for a,b in zip(v,v[1:]))-w/2)
    if kind=='circle':
        return max(0,hypot(p[0]-float(n.attrib['cx']),p[1]-float(n.attrib['cy']))-float(n.attrib['r']))
    return float('inf')
jamb_issues=[]
for d in doors:
    a,b=d['a'],d['b']
    blocked=[]
    for i in range(17):
        t=.2+i*.6/16
        p=(a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t)
        overlap=[n.attrib.get('id',n.attrib.get('points','unnamed')) for n in walls if hit(p,n)]
        if overlap:blocked.append((p,overlap))
    if blocked:
        issues.append(dict(door=d['id'],samples=len(blocked),walls=sorted(set(s for p,ns in blocked for s in ns))))
    for label,p in [('hinge',a)]+([] if d['id'].endswith(('-a','-b')) else [('opposite_jamb',b)]):
        near=min((gap(p,n),n.attrib.get('id',n.attrib.get('points','unnamed'))) for n in walls)
        if near[0]>2:
            jamb_issues.append(dict(door=d['id'],end=label,point=p,gap=round(near[0],2),wall=near[1]))
report={'door_leaves_checked':len(doors),'wall_crossings':issues,'detached_jambs':jamb_issues}
(base/'review/door-opening-audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
