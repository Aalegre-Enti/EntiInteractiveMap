"""Architectural-only manual vector trace of img22.jpg."""
from pathlib import Path
from math import hypot
import xml.etree.ElementTree as E

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
E.register_namespace('', NS)
E.register_namespace('inkscape', INK)
def node(parent, tag, **attrs):
    return E.SubElement(parent, '{'+NS+'}'+tag, {k.replace('_','-'):str(v) for k,v in attrs.items()})
svg = E.Element('{'+NS+'}svg', {'width':'1395','height':'1040','viewBox':'0 0 1395 1040','version':'1.1','shape-rendering':'geometricPrecision'})
node(svg,'title').text = 'Walls, doors, accesses and stairs — img22'
node(svg,'desc').text = ('Manually traced from OriginalFloorplan/img22.jpg in the original image coordinate system. '
    'Four editable vector layers contain structural walls and piers, doors, access thresholds, and stairs. '
    'Furniture, sanitary fixtures, elevator machinery, text, room colours, glazing details and site markings are omitted. '
    'Visible architectural geometry is traced; short wall continuations beneath labels are approximate. '
    'Reviewed against enlarged source-image crops. Door widths, unequal leaves, swings, stair doors, '
    'service-room doors, bathroom partitions and doorway wall gaps have been corrected. '
    'Details hidden by the BUCS 1-7, LAB.POLI-3.02 and LAB-3.01 labels remain unverified. '
    'This is an image-based trace with no surveyed dimensions or asserted physical scale. No raster image is embedded.')
def layer(label, **attrs):
    g=node(svg,'g',id=label.lower(),**attrs)
    g.set('{'+INK+'}groupmode','layer'); g.set('{'+INK+'}label',label)
    return g
walls=layer('Walls',fill='#343a40',stroke='#343a40',stroke_linejoin='miter')
stairs=layer('Stairs',fill='none',stroke='#343a40',stroke_width='0.95',stroke_linejoin='round')
accesses=layer('Accesses',fill='none',stroke='#343a40',stroke_width='0.8')
doors=layer('Doors',fill='none',stroke='#343a40',stroke_width='1.1',stroke_linejoin='round',stroke_linecap='round')
def n(x): return f'{x:.3f}'.rstrip('0').rstrip('.')
def pts(p): return ' '.join(f'{n(x)},{n(y)}' for x,y in p)
def line(g,a,b,**kw): return node(g,'line',x1=n(a[0]),y1=n(a[1]),x2=n(b[0]),y2=n(b[1]),**kw)
def path(g,d,**kw): return node(g,'path',d=d,**kw)
def wall(p,w=5,name=None):
    kw={'id':name} if name else {}
    return node(walls,'polyline',points=pts(p),fill='none',stroke_width=n(w),stroke_linecap='butt',**kw)
def block(p,name=None):
    return node(walls,'polygon',points=pts(p),stroke_width=0,**({'id':name} if name else {}))
def rect(x,y,w,h,name=None): return block([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],name)
def circle(x,y,r): return node(walls,'circle',cx=x,cy=y,r=r,stroke_width=0)
portals=[]
def access(a,b,name=None):
    portals.append({'name':name or 'access-'+str(len(portals)+1),'a':a,'b':b})
    g=node(accesses,'g',**({'id':name} if name else {}))
    dx,dy=b[0]-a[0],b[1]-a[1]; z=hypot(dx,dy); nx,ny=-dy/z,dx/z
    line(g,a,b,stroke_dasharray='3 2')
    for p in [a,b]: line(g,(p[0]-3*nx,p[1]-3*ny),(p[0]+3*nx,p[1]+3*ny),stroke_width='1.4')
def door(a,b,side=1,name=None):
    g=node(doors,'g',**({'id':name} if name else {}))
    dx,dy=b[0]-a[0],b[1]-a[1]; r=hypot(dx,dy)
    c=(a[0]-side*dy,a[1]+side*dx)
    line(g,a,c)
    path(g,f'M {n(b[0])},{n(b[1])} A {n(r)},{n(r)} 0 0 {1 if side>0 else 0} {n(c[0])},{n(c[1])}',stroke_width='.8')
def double(a,b,side=1,name=None):
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    door(a,mid,side,name and name+'-left');door(b,mid,-side,name and name+'-right')
    access(a,b,name and name+'-threshold')
def unequal(a,b,ratio,side=1,name=None):
    mid=(a[0]+ratio*(b[0]-a[0]),a[1]+ratio*(b[1]-a[1]))
    door(a,mid,side,name and name+'-left');door(b,mid,-side,name and name+'-right')
    access(a,b,name and name+'-threshold')
def leaf(a,b,side=1,name=None):
    door(a,b,side,name); access(a,b,name and name+'-threshold')

# Exterior wall lines. Facade glazing and window swings are intentionally omitted.
wall([(20,985),(20,460),(23,433),(44,341),(348,31),(1353,20)],5,'west-north-envelope')
wall([(1353,20),(974,541)],5,'east-envelope')
wall([(974,541),(931,528)],9,'east-corner')
wall([(931,528),(743,725)],3.5,'southeast-courtyard-edge')
wall([(743,725),(745,810),(552,810)],8,'bathroom-south-east-envelope')
wall([(551,765),(551,868),(392,868)],3,'south-stair-envelope')
wall([(389,740),(389,1005),(42,1005),(42,983),(20,983)],5,'southwest-envelope')

# Structural piers and columns, treated as part of the wall layer.
for p in [
 [(341,36),(349,27),(371,27),(371,35),(354,35),(349,42)],
 [(529,25),(550,25),(550,47),(529,47)],
 [(695,24),(722,24),(722,34),(716,34),(716,48),(703,48),(703,35),(695,35)],
 [(874,23),(906,23),(906,33),(896,33),(896,47),(882,47),(882,33),(874,33)],
 [(1044,22),(1083,22),(1083,31),(1073,31),(1073,44),(1058,44),(1058,32),(1044,32)],
 [(1227,20),(1264,20),(1264,30),(1252,30),(1252,43),(1237,43),(1237,30),(1227,30)],
 [(1331,19),(1356,18),(1355,25),(1360,26),(1343,43),(1318,24)],
 [(248,138),(269,156),(257,167),(240,150)],
 [(125,264),(146,284),(132,298),(111,278)],
 [(44,333),(53,338),(48,356),(36,353)],
 [(21,427),(32,431),(31,446),(35,447),(33,462),(18,463)],
 [(18,542),(38,542),(38,562),(29,562),(29,573),(18,573)],
 [(18,714),(39,714),(39,741),(18,741)],
 [(18,894),(42,894),(42,917),(18,917)],
 [(18,982),(41,982),(41,1007),(17,1007)],
 [(184,993),(196,993),(196,984),(212,984),(212,1007),(184,1007)],
 [(370,985),(389,985),(389,1005),(362,1005),(362,997),(370,997)],
 [(236,389),(251,376),(273,397),(255,412)],
 [(1184,189),(1207,205),(1196,220),(1175,205)],
 [(1047,379),(1069,394),(1059,407),(1037,392)],
 [(880,201),(897,201),(897,218),(880,218)],
 [(186,543),(216,543),(216,569),(188,569)],
 [(365,521),(380,507),(394,521),(383,531),(383,567),(365,567)],
 [(379,698),(390,698),(390,724),(379,724)]
]: block(p)
for x,y,r in [(353,44,6),(377,265,7),(710,211,7),(1067,206,6.5)]: circle(x,y,r)
wall([(1204,209),(1211,215)],4,'northeast-pier-facade-junction')
wall([(1064,396),(1073,405)],4,'store-pier-facade-junction')
node(walls,'rect',x=519,y=35,width=26,height=12,rx=6,stroke_width=0)
node(walls,'rect',x=519,y=207,width=28,height=14,rx=7,stroke_width=0)

# North-west teaching rooms and recording wing.
wall([(549,31),(549,244),(521,244)],6,'northwest-room-east-wall')
path(walls,'M 521,244 Q 510,244 507,255 L 495,290 L 475,310 L 477,312',fill='none',stroke_width=7)
wall([(263,154),(453,336)],2.5,'northwest-classroom-divider')
wall([(453,336),(473,363),(460,402),(428,435),(431,439)],7,'west-classroom-corridor-wall')
wall([(411,458),(428,484),(423,489)],6,'diagonal-service-enclosure')
wall([(407,503),(390,520),(378,505)],6)
wall([(391,452),(411,458)],5)
wall([(358,485),(378,505)],5)
wall([(132,271),(249,388),(262,394),(374,507),(363,521),(362,646),(309,646),(309,640)],6,'recording-storage-boundary')
wall([(306,442),(306,618)],6,'recording-storage-divider')
wall([(27,450),(27,540),(280,540)],6,'recording-room-south-wall')
wall([(299,540),(306,540)],6)
wall([(28,544),(192,544)],3)
wall([(215,544),(257,544),(257,665)],6,'control-room-east-wall')
wall([(257,686),(257,690),(26,690),(26,566)],6,'control-room-south-wall')
wall([(260,658),(337,658)],2.2,'distribution-room-north-wall')
wall([(336,695),(387,695),(388,738),(372,738)],7,'south-service-enclosure')
wall([(323,738),(322,738),(322,707),(336,707),(336,695)],7)
wall([(362,650),(362,653),(341,653)],3)
wall([(361,693),(341,693)],3)

# The central distributor and service passage.
wall([(365,568),(365,597),(385,597)],5,'distributor-west-wall')
wall([(422,597),(431,597),(431,543),(434,540)],5,'distributor-east-wall')
wall([(451,523),(455,518)],5)
wall([(452,519),(472,534),(502,503)],5,'diagonal-access-recess')
wall([(488,480),(533,431)],7,'northwest-corridor-edge')
wall([(543,401),(543,406)],5)
wall([(530,447),(490,487),(604,599)],7,'west-courtyard-boundary')
wall([(498,487),(530,453),(687,502),(607,585),(498,487)],2.5,'west-courtyard-inner-edge')
wall([(534,443),(696,497),(610,591)],3,'west-courtyard-outer-edge')
wall([(503,501),(557,553),(543,568),(432,568)],6,'central-void-south-boundary')
wall([(613,599),(647,632),(793,482)],3.5,'east-courtyard-west-edge')
wall([(651,629),(794,490),(923,532)],2.2,'east-courtyard-north-edge')
wall([(651,629),(742,717),(923,532)],2.2,'east-courtyard-inner-edge')
wall([(488,480),(604,596)],6,'diagonal-core-divider')
wall([(637,628),(744,732)],7,'bathroom-diagonal-envelope')

# Northern rooms, laboratory and lobby.
wall([(550,244),(554,244),(554,247)],5)
path(walls,'M 583,247 L 609,247 L 609,263 Q 609,278 626,278 L 803,278 L 803,259 L 815,259',fill='none',stroke_width=7)
wall([(802,26),(802,204),(815,204)],4,'north-classroom-divider')
wall([(802,203),(802,260)],4)
wall([(844,203),(1183,203)],4,'northeast-room-south-wall')
wall([(855,259),(873,259),(873,375)],7,'laboratory-west-wall')
wall([(873,252),(891,252)],4)
wall([(891,217),(891,222)],3)
wall([(873,341),(903,341)],3)
wall([(872,375),(901,375)],6)
wall([(903,341),(903,382),(954,382),(954,341),(951,341)],5,'laboratory-service-enclosure')
wall([(904,341),(906,341)],4)
wall([(956,385),(1022,385)],6,'laboratory-store-divider')
wall([(1040,385),(1044,385)],5)
wall([(967,361),(967,384),(926,523)],6,'store-west-wall')
wall([(930,530),(966,541),(976,539)],7)

# Two diagonal stair enclosures and the small rooms between them.
wall([(542,297),(716,351)],7,'north-stair-north-wall')
wall([(716,351),(686,445),(516,394)],7,'north-stair-east-and-south-walls')
wall([(543,297),(544,302)],5)
wall([(537,325),(526,357)],6,'north-stair-west-wall')
wall([(516,379),(513,390),(543,399)],6)
rect(517,382,10,10);rect(537,388,10,10)
wall([(716,351),(721,338),(729,341)],6)
wall([(764,354),(775,358),(775,360)],6)
wall([(774,358),(741,463),(708,452)],6,'middle-service-east-wall')
wall([(702,389),(756,406)],4,'middle-service-divider')
wall([(716,351),(690,430)],5,'middle-service-west-wall')
rect(706,399,11,7);block([(710,448),(720,451),(717,461),(706,457)])
wall([(814,373),(849,373)],6)
wall([(814,373),(810,387),(951,433)],7,'east-stair-north-wall')
wall([(741,463),(746,465)],7,'east-stair-south-west-jamb')
wall([(770,473),(927,523)],7,'east-stair-south-wall')
wall([(926,523),(952,433)],6)

# Elevator shaft walls; only shaft boundaries and access openings are retained.
wall([(433,636),(433,570),(540,570),(540,636)],7,'upper-lift-enclosure')
wall([(490,572),(490,636)],5,'upper-lift-divider')
for a,b in [(433,448),(479,498),(528,540)]: wall([(a,636),(b,636)],6)
wall([(427,712),(553,712),(553,765),(428,765),(428,712)],7,'lower-lift-enclosure')
wall([(493,713),(493,763)],5,'lower-lift-divider')
# Lift doorway gaps in the north edge are implemented by separate wall segments below.
for a,b in [(449,479),(499,529)]:
    access((a,636),(b,636))
    line(doors,(a,633),(b,633));line(doors,((a+b)/2,633),((a+b)/2,639))
# The continuous upper edge is replaced later by doorway gaps in the generated SVG.
for a,b in [(449,478),(500,529)]:
    access((a,712),(b,712))
    line(doors,(a,715),(b,715));line(doors,((a+b)/2,710),((a+b)/2,715))
wall([(388,713),(395,713)],5)
wall([(422,713),(429,713)],5)
wall([(391,743),(391,869)],3,'south-stair-west-wall')

# Upper and lower bathroom partitions. Tile-grid lines are not walls.
wall([(544,570),(558,556),(597,595)],4,'upper-bathroom-northeast-wall')
wall([(545,570),(545,635),(564,635)],5,'upper-bathroom-west-wall')
wall([(579,620),(592,607),(604,596)],4)
wall([(579,620),(610,654)],4,'accessible-lobby-divider')
wall([(556,712),(594,672)],5,'bathroom-corridor-boundary')
wall([(610,656),(618,648)],5)
wall([(633,634),(637,630)],4)
wall([(557,712),(583,712)],3)
wall([(583,712),(583,684)],3,'bathroom-accessible-cubicle-west')
wall([(610,657),(610,664),(631,685)],3,'bathroom-accessible-cubicle-northeast')
wall([(583,712),(631,712)],3)
wall([(631,708),(631,714)],3)
wall([(631,735),(631,739)],3)
wall([(674,681),(674,714)],3,'bathroom-northeast-room-west-wall')
wall([(674,681),(687,681)],3)
wall([(674,736),(674,739)],3)
wall([(557,714),(557,810)],6)
wall([(638,738),(638,808)],6,'west-toilet-service-wall')
wall([(654,738),(654,808)],6,'east-toilet-service-wall')
for y in [741,763,785,807]:
    wall([(598,y),(637,y)],2)
    wall([(656,y),(698,y)],2)
for y in [741,763,785]:
    wall([(598,y+19),(598,y+22)],2)
    wall([(698,y+19),(698,y+22)],2)

# Recording booths and the southern laboratory.
wall([(27,695),(119,695),(119,747)],5,'booth-row-west-divider')
wall([(27,695),(27,716),(40,716),(40,744),(91,744)],5)
wall([(113,744),(119,744)],4)
wall([(121,695),(192,695),(192,744),(151,744)],5,'booth-row-east-divider')
wall([(120,744),(128,744)],4)
wall([(196,695),(256,695),(256,744)],5,'instrument-room-wall')
wall([(197,719),(213,719),(213,744),(197,744)],3)
wall([(257,765),(257,790),(287,790)],5)
wall([(319,739),(319,790)],5,'south-lab-entry-west-wall')
wall([(319,790),(315,790)],5)
wall([(24,747),(91,747)],4,'booth-corridor-north-wall')
wall([(113,747),(128,747)],4)
wall([(151,747),(207,747)],4)
wall([(24,751),(24,896),(42,896),(42,914),(64,914)],5,'booth-west-wall')
wall([(85,799),(85,892)],4,'booth-corridor-west-divider')
wall([(25,829),(85,829)],5,'booth-middle-divider')
wall([(25,836),(83,836)],2)
wall([(146,803),(146,916),(153,916)],5,'booth-corridor-east-divider')
wall([(150,825),(204,825),(204,910),(172,910)],5,'east-booth-enclosure')
wall([(206,827),(206,813)],5)
path(walls,'M 207,815 Q 207,791 234,791 L 257,791',fill='none',stroke_width=5)
wall([(23,922),(40,922),(40,981),(44,981),(44,999),(115,999),(115,921)],5,'southwest-booth-enclosure')
wall([(44,921),(90,921)],4)
wall([(112,921),(115,921)],4)
wall([(120,921),(124,921)],4)
wall([(146,921),(205,921),(205,980),(198,980),(198,999),(120,999),(120,921)],5,'southeast-booth-enclosure')
wall([(211,928),(211,1002)],4,'south-lab-west-wall')
wall([(376,741),(376,736),(370,736)],3)

# Door leaves, swings, and thresholds, traced independently of wall geometry.
unequal((453,336),(477,312),2/3,1,'northwest-classroom-entry')
unequal((411,458),(431,439),2/3,1,'west-classroom-entry')
unequal((554,247),(583,247),1/3,1,'north-centre-classroom-entry')
unequal((815,204),(844,204),2/3,1,'northeast-classroom-entry')
double((815,259),(855,259),1,'northeast-distributor-entry')
leaf((891,252),(891,222),-1,'laboratory-entry')
leaf((873,375),(849,375),1,'east-stair-lobby-door')
double((906,341),(951,341),-1,'laboratory-service-access')
double((729,341),(764,354),-1,'middle-service-access')
double((775,360),(814,373),1,'east-stair-access')
leaf((687,445),(708,452),-1,'middle-small-room-door')
leaf((746,465),(770,473),-1,'east-stair-south-door')
leaf((544,302),(537,325),-1,'north-stair-north-door')
leaf((519,382),(526,357),1,'north-stair-west-door')
leaf((543,406),(533,431),1,'north-stair-lobby-door')
double((358,485),(391,452),-1,'diagonal-service-north-access')
leaf((423,489),(407,503),-1,'diagonal-service-south-door')
double((454,519),(486,487),-1,'central-diagonal-access')
leaf((451,523),(434,540),1,'central-diagonal-south-door')
leaf((1040,385),(1022,385),-1,'laboratory-store-door')
double((385,597),(422,597),-1,'central-distributor-access')
leaf((299,540),(280,540),1,'recording-room-door')
leaf((309,640),(309,618),1,'storage-door')
leaf((257,686),(257,665),-1,'control-room-door')
double((341,653),(341,693),-1,'central-distribution-access')
leaf((113,744),(91,744),1,'booth-1-door')
leaf((128,744),(151,744),-1,'booth-2-door')
leaf((256,744),(256,765),1,'instrument-room-door')
unequal((287,790),(319,790),1/3,-1,'southern-laboratory-entry')
double((323,739),(372,739),1,'southern-service-access')
leaf((85,914),(64,914),1,'west-lower-booth-door')
leaf((151,910),(172,910),-1,'east-lower-booth-door')
leaf((112,921),(90,921),-1,'southwest-booth-door')
leaf((124,921),(146,921),1,'southeast-booth-door')
leaf((422,713),(395,713),-1,'south-stair-north-entry')
leaf((579,620),(564,635),-1,'upper-bathroom-door')
leaf((610,656),(594,672),1,'bathroom-lobby-door')
access((604,596),(637,628),'accessible-lobby-northeast-opening')
access((618,648),(633,634),'accessible-lobby-southeast-opening')
leaf((631,708),(631,685),1,'accessible-bathroom-door')
leaf((631,735),(631,714),-1,'bathroom-west-passage')
leaf((674,736),(674,714),1,'bathroom-northeast-door')
for y in [741,763,785]:
    leaf((598,y),(598,y+19),-1)
    leaf((698,y),(698,y+19),1)

# Stair treads, landing outlines, central gaps and travel arrows.
def stair_arrow(points):
    node(stairs,'polyline',points=pts(points),stroke_width='.8')
    a,b=points[-2:]; dx,dy=b[0]-a[0],b[1]-a[1]; z=hypot(dx,dy); ux,uy=dx/z,dy/z
    node(stairs,'polyline',points=pts([(b[0]-5*ux+2*uy,b[1]-5*uy-2*ux),b,(b[0]-5*ux-2*uy,b[1]-5*uy+2*ux)]),stroke_width='.8')
def stair(origin, direction, run, width, landing, steps, name, round_west=0, round_east=False):
    g=node(stairs,'g',id=name)
    ux,uy=direction; z=hypot(ux,uy); ux,uy=ux/z,uy/z; vx,vy=-uy,ux
    def p(u,v): return (origin[0]+ux*u+vx*v,origin[1]+uy*u+vy*v)
    def ln(a,b,**kw): return line(g,p(*a),p(*b),**kw)
    flight=(width-14)/2
    if name=='south-stair': flight=(width-22)/2
    for lo,hi in [(0,flight),(width-flight,width)]:
        node(g,'polyline',points=pts([p(0,lo),p(run,lo),p(run,hi),p(0,hi),p(0,lo)]),stroke_width='1.25')
        for i in range(1,steps):
            u=run*i/steps
            ln((u,lo),(u,hi))
    node(g,'polyline',points=pts([p(run,0),p(run+landing,0),p(run+landing,width),p(run,width)]),stroke_width='1.2')
    ln((0,flight),(run+landing,flight),stroke_width='1.25')
    ln((0,width-flight),(run+landing,width-flight),stroke_width='1.25')
    if round_west:
        a=p(0,0);b=p(-round_west,0);c=p(-round_west,width);d=p(0,width)
        path(g,f'M {n(a[0])},{n(a[1])} C {n(b[0])},{n(b[1])} {n(c[0])},{n(c[1])} {n(d[0])},{n(d[1])}',stroke_width='1.1')
    if round_east:
        for aa,bb,cc in [((run,0),(run+landing,0),(run+landing,flight)),((run+landing,width-flight),(run+landing,width),(run,width))]:
            a,b,c=p(*aa),p(*bb),p(*cc)
            path(g,f'M {n(a[0])},{n(a[1])} Q {n(b[0])},{n(b[1])} {n(c[0])},{n(c[1])}')
    stair_arrow([p(6,width-flight/2),p(run+landing/2,width-flight/2),p(run+landing/2,flight/2),p(6,flight/2)])
    # Conventional break in the ascending flight.
    for delta in [0,3]:
        ln((run*.52+delta,0),(run*.41+delta,flight),stroke_width='1.3')
stair((596,318),(1,.31),89,86,25,14,'north-stair',round_west=51)
stair((840,402),(1,.32),87,82,26,14,'east-stair',round_west=52)
stair((432,770),(1,0),78,96,37,12,'south-stair',round_west=54,round_east=True)

# Replace the lift wall edge with real doorway openings, without white masks.
for el in list(walls):
    if el.get('id')=='lower-lift-enclosure':
        walls.remove(el)
wall([(428,712),(428,765),(553,765),(553,712),(529,712)],7,'lower-lift-enclosure')
wall([(428,712),(449,712)],7)
wall([(478,712),(500,712)],7)

E.indent(svg,space='  ')
out=ROOT/'img22-architectural.svg'
E.ElementTree(svg).write(out,encoding='utf-8',xml_declaration=True)
assert not list(svg.iter('{'+NS+'}image'))
assert not list(svg.iter('{'+NS+'}text'))
ids=[x.get('id') for x in svg.iter() if x.get('id')]
assert len(ids)==len(set(ids)), 'Duplicate SVG ids'
print(out)
print('Vector shapes:',sum(x.tag.split('}')[-1] in {'path','line','polyline','polygon','rect','circle'} for x in svg.iter()))
import json
(ROOT/'.vector-img22'/'portals.json').write_text(json.dumps(portals,indent=2))
# A wall-only rendering is used to check for solid walls across doorway thresholds.
wall_svg=E.Element('{'+NS+'}svg',dict(svg.attrib))
import copy
wall_svg.append(copy.deepcopy(walls))
E.ElementTree(wall_svg).write(ROOT/'.vector-img22'/'walls-only.svg',encoding='utf-8',xml_declaration=True)
