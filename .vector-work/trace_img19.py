"""Semantic architectural vector trace; source coordinates are retained."""
from pathlib import Path
from math import hypot
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NS = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', NS)
ET.register_namespace('inkscape', INK)
def tag(n): return '{' + NS + '}' + n
def num(n): return f'{n:.3f}'.rstrip('0').rstrip('.')
def pts(p): return ' '.join(f'{num(x)},{num(y)}' for x,y in p)
def el(g,t,**a): return ET.SubElement(g,tag(t),{k.replace('_','-'):str(v) for k,v in a.items()})

svg = ET.Element(tag('svg'),width='1395',height='1040',viewBox='0 0 1395 1040',version='1.1')
el(svg,'title').text='Walls, doors, accesses and stairs — img19'
el(svg,'desc').text=(
    'Editable manual architectural trace of OriginalFloorplan/img19.jpg, using its original '
    '1395 by 1040 image coordinates. Four layers contain walls and structural columns, doors '
    'and their swings, access thresholds, and three staircases. No embedded raster, room labels, '
    'furniture, fixtures, floor patterns, room colors, window swings, clearance circles or site '
    'annotations. Visible door positions, swings and wall openings were reviewed against a '
    'coordinate-aligned source overlay. Source labels conceal some short wall sections and '
    'parts of the west junction; these remain approximate. No surveyed scale or dimensional '
    'accuracy is asserted.'
)
def layer(name,**a):
    g=el(svg,'g',id=name.lower(),**a)
    g.set('{'+INK+'}groupmode','layer'); g.set('{'+INK+'}label',name)
    return g
C='#292d32'
walls=layer('Walls',fill=C,stroke=C,stroke_linejoin='miter')
stairs=layer('Stairs',fill='none',stroke=C,stroke_width='.9',stroke_linejoin='round')
accesses=layer('Accesses',fill='none',stroke=C,stroke_width='.65')
doors=layer('Doors',fill='none',stroke=C,stroke_width='1.15',stroke_linejoin='round',stroke_linecap='round')

def line(g,a,b,**kw): return el(g,'line',x1=num(a[0]),y1=num(a[1]),x2=num(b[0]),y2=num(b[1]),**kw)
def path(g,d,**kw): return el(g,'path',d=d,**kw)
def wall(p,w=5,name=None):
    return el(walls,'polyline',points=pts(p),fill='none',stroke_width=num(w),stroke_linecap='butt',**({'id':name} if name else {}))
def block(p,name=None):
    return el(walls,'polygon',points=pts(p),stroke_width='0',**({'id':name} if name else {}))
def rect(x,y,w,h,name=None): return block([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],name)
def column(x,y,r): return el(walls,'circle',cx=x,cy=y,r=r,stroke_width='0')
def threshold(a,b,name=None): return line(accesses,a,b,stroke_dasharray='3 2',**({'id':name} if name else {}))
def door(a,b,side=1,name=None):
    dx,dy=b[0]-a[0],b[1]-a[1]; r=hypot(dx,dy)
    tip=(a[0]-side*dy,a[1]+side*dx)
    g=el(doors,'g',**({'id':name} if name else {}))
    line(g,a,tip,stroke_width='1.25')
    path(g,f'M {num(b[0])},{num(b[1])} A {num(r)},{num(r)} 0 0 {int(side>0)} {num(tip[0])},{num(tip[1])}',stroke_width='.8')
def double(a,b,side=1,ratio=.5,name=None):
    m=(a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio)
    door(a,m,side,name and name+'-a'); door(b,m,-side,name and name+'-b')
def opening(a,b,side=1,name=None,paired=False,ratio=.5):
    if paired: double(a,b,side,ratio,name)
    else: door(a,b,side,name)
    threshold(a,b,name and name+'-threshold')
def sliding(a,b,name):
    g=el(doors,'g',id=name)
    dx,dy=b[0]-a[0],b[1]-a[1]; n=hypot(dx,dy)
    nx,ny=-dy/n*1.25,dx/n*1.25; m=((a[0]+b[0])/2,(a[1]+b[1])/2)
    line(g,a,b,stroke_width='.65')
    line(g,(a[0]+nx,a[1]+ny),(m[0]+nx,m[1]+ny),stroke_width='1')
    line(g,(m[0]-nx,m[1]-ny),(b[0]-nx,b[1]-ny),stroke_width='1')
    threshold(a,b)

# Building envelope. Repeated dashed perimeter arcs in the source are window
# opening symbols and are not included in the door layer.
wall([(18,1005),(18,456),(49,335),(347,30),(1338,23)],4.5,'north-and-west-envelope')
wall([(1348,28),(970,542)],4.5,'east-envelope')
wall([(18,1005),(388,1005),(388,733)],5,'south-envelope')
block([(337,35),(347,25),(368,25),(367,32),(349,32),(341,42)])
block([(528,23),(550,23),(550,49),(528,49)],'north-pier-01')
block([(691,23),(727,22),(727,30),(715,30),(715,49),(702,49),(702,30),(691,30)])
block([(871,22),(906,21),(906,29),(897,29),(897,47),(881,47),(881,29),(871,29)])
block([(1047,19),(1087,19),(1087,27),(1075,27),(1075,43),(1059,43),(1059,27),(1047,27)])
rect(1235,19,21,23)
block([(1334,16),(1358,16),(1357,25),(1360,29),(1341,49),(1328,39),(1336,29)])
block([(245,144),(252,136),(270,150),(259,162),(247,151)])
block([(119,271),(129,262),(145,278),(133,291),(121,279)])
block([(43,333),(49,324),(58,333),(54,347),(44,347),(40,343)])
block([(16,448),(26,449),(28,459),(24,460),(25,477),(18,478)])
block([(16,546),(41,546),(41,562),(29,562),(29,576),(16,576)])
block([(15,724),(39,724),(39,740),(28,740),(28,751),(15,751)])
block([(15,898),(37,898),(37,917),(27,917),(27,931),(15,931)])
block([(15,984),(41,984),(41,1003),(53,1003),(53,1010),(15,1010)])
block([(184,994),(199,994),(199,984),(211,984),(211,995),(225,995),(225,1009),(184,1009)])
block([(365,994),(377,994),(377,983),(393,983),(393,1010),(365,1010)])
rect(369,903,21,14)
block([(1181,199),(1195,191),(1210,202),(1200,219),(1185,208)])
block([(1043,384),(1053,374),(1068,385),(1059,401)])
for x,y,r in [(354,43,6),(255,146,6.5),(131,271,6.5),(252,392,8),(377,265,8),(202,555,8),(202,734,7.5),(203,910,7.5),(711,212,7.5),(1068,207,6.5),(1196,204,7),(1059,391,6.5)]:
    column(x,y,r)
el(walls,'rect',x='520',y='207',width='26',height='13',rx='6.5',stroke_width='0')
el(walls,'rect',x='520',y='35',width='26',height='13',rx='6.5',stroke_width='0')

# Upper teaching rooms and the central entrance lobby.
wall([(619,30),(619,257)],3.5,'west-teaching-room-divider')
path(walls,'M 614,257 L 614,266 Q 614,279 628,279 L 824,279 L 824,212',fill='none',stroke_width='7',id='teaching-room-south-wall')
wall([(619,155),(824,155)],2.2,'teaching-room-internal-partition')
wall([(824,184),(824,143),(837,143)],4.5)
wall([(867,143),(869,143)],4.5)
opening((837,143),(865,143),1,'upper-teaching-room-entry',True,.32)
opening((824,184),(824,212),1,'lower-teaching-room-entry',True,.66)
wall([(870,27),(870,167),(890,167)],4.5,'north-lab-west-wall')
wall([(870,199),(889,199),(889,219),(879,219)],4.5)
rect(880,202,18,17)
column(889,210,8)
wall([(889,202),(1187,202)],3.5,'laboratory-divider')
opening((890,171),(890,198),1,'north-laboratory-entry',True,.7)
wall([(890,254),(872,254),(872,375),(903,375)],6,'south-lab-west-wall')
opening((890,220),(890,251),1,'south-laboratory-entry',True,.32)
opening((826,256),(869,256),1,'upper-lobby-access',True)
wall([(826,256),(826,267)],3)
wall([(869,256),(869,267)],3)
wall([(507,256),(579,256),(579,261)],7,'west-room-south-wall')
wall([(610,259),(614,259)],5)
opening((583,260),(610,260),1,'west-laboratory-entry',True,.34)

# Diagonal room divisions and the enclosed recording area.
wall([(255,155),(377,266)],3,'northwest-room-divider')
wall([(377,255),(478,255)],3)
wall([(497,255),(507,255)],3)
opening((497,255),(478,255),-1,'recording-room-entry')
wall([(377,270),(471,367)],3,'recording-room-diagonal-wall')
wall([(507,256),(458,405),(428,434)],7,'west-laboratory-corridor-wall')
wall([(129,284),(363,518)],5,'west-classroom-diagonal-wall')
wall([(32,549),(270,549),(270,556)],5,'west-classroom-south-wall')
wall([(302,556),(362,556)],5)
opening((272,556),(302,556),1,'west-classroom-entry',True,.66)

# Small enclosure at the junction of the west rooms.
wall([(397,455),(427,486)],5,'west-service-enclosure-north')
wall([(410,503),(380,530),(364,516)],5,'west-service-enclosure-south')
# The shaft's northwest face is a double access, partly hidden by the label.
# Its inner rectangular equipment outline is not an architectural wall.
wall([(363,516),(363,650)],7,'west-distributor-east-wall')
wall([(383,528),(383,555),(365,555)],4)
opening((407,457),(428,434),1,'west-lab-corridor-entry',True,.68)
opening((364,488),(397,454),-1,'west-service-double-access',True)
wall([(363,488),(363,516)],5)
# The smaller corridor door is in the southeast face, opening toward the lobby.
opening((427,486),(410,503),-1,'west-service-entry')

# Diagonal link between the lift lobby and the west distributor.
wall([(484,480),(501,497)],5)
wall([(457,515),(456,519),(471,533),(501,502)],5,'diagonal-access-return')
wall([(440,532),(430,543),(430,569)],4)
opening((456,513),(438,531),1,'diagonal-lobby-outer-door')
opening((457,513),(484,486),-1,'diagonal-lobby-inner-access',True)
wall([(364,597),(384,597)],4)
wall([(423,597),(430,597)],4)
opening((384,597),(423,597),-1,'distributor-inner-access',True)
opening((364,650),(364,690),-1,'lift-lobby-west-access',True)
wall([(364,690),(387,690),(387,709)],6)

# West lower classrooms and service closet.
wall([(270,556),(270,690),(250,690),(250,696)],5,'middle-classroom-east-wall')
wall([(250,724),(250,725),(32,725)],5,'middle-classroom-south-wall')
opening((250,696),(250,724),-1,'middle-classroom-entry',True,.66)
wall([(250,725),(250,742),(268,742)],4)
wall([(250,773),(272,773)],5)
opening((250,773),(250,742),1,'southwest-classroom-entry',True,.66)
wall([(314,772),(314,700),(338,700),(338,695),(386,695)],5,'lower-service-room-north-wall')
wall([(319,702),(369,702),(369,738)],3.5)
wall([(319,702),(319,738)],3.5)
opening((320,738),(368,738),1,'lower-service-closet',True)
wall([(384,734),(384,1002)],7,'southeast-classroom-east-wall')
wall([(272,773),(284,773)],4)
wall([(313,773),(313,761)],4)
opening((284,773),(313,773),-1,'southeast-classroom-entry',True,.34)
path(walls,'M 252,776 L 230,776 Q 208,776 208,798 L 208,996',fill='none',stroke_width='4',id='lower-classroom-divider')
rect(376,726,15,15)

# North stair enclosure and adjacent rooms.
wall([(542,298),(712,350),(718,339),(728,342)],7,'north-stair-north-wall')
wall([(542,298),(541,303)],5)
wall([(533,327),(523,357)],6,'north-stair-west-wall')
wall([(516,390),(513,397),(683,448),(687,446)],7,'north-stair-south-wall')
wall([(711,351),(683,444)],6,'north-stair-east-wall')
opening((541,303),(533,327),-1,'north-stair-upper-access')
opening((514,382),(523,357),1,'north-stair-lower-access')
block([(512,381),(528,385),(525,399),(509,394)])
block([(530,387),(545,391),(541,404),(526,399)])
wall([(527,431),(523,443),(488,477),(494,483)],6)
opening((535,405),(527,431),1,'west-stair-corridor-door')
wall([(706,389),(754,405),(774,362),(763,358)],5,'north-service-room-east-wall')
wall([(763,358),(762,352)],4)
opening((728,342),(762,352),-1,'north-service-double-door',True,.48)
wall([(706,454),(739,464),(756,406)],6,'north-service-south-wall')
opening((687,448),(706,454),-1,'north-service-south-entry')
rect(710,449,11,11)

# East stair, its approach corridor and the small storage room.
wall([(774,362),(778,363)],4)
wall([(815,376),(812,386),(952,433)],7,'east-stair-north-wall')
wall([(815,376),(847,376)],5)
opening((778,363),(815,376),1,'east-stair-north-access',True)
opening((868,374),(847,374),1,'east-laboratory-south-access')
wall([(739,464),(744,466)],5)
opening((744,466),(770,474),-1,'east-stair-south-access')
wall([(770,474),(972,540)],8,'east-stair-south-wall')
wall([(969,383),(925,523)],7,'east-stair-east-wall')
wall([(903,341),(903,384),(969,384),(969,341),(951,341)],5,'east-service-enclosure')
wall([(873,341),(904,341)],3)
wall([(952,341),(952,381)],3)
opening((905,339),(952,339),-1,'east-service-double-door',True)
wall([(966,475),(1010,489)],3.5,'storage-room-north-wall')
opening((946,469),(966,475),-1,'storage-room-door')

# The two triangular openings have perimeter walls only. The source's dashed
# diagonal construction/void marks are deliberately omitted.
wall([(523,443),(693,499),(601,591),(491,484),(523,443)],5,'west-triangular-void')
wall([(529,449),(684,503),(601,584),(500,482),(529,449)],1.5,'west-void-inner-edge')
wall([(789,487),(928,531),(743,726),(644,630),(789,487)],5,'east-triangular-void')
wall([(790,494),(919,533),(743,718),(651,630),(790,494)],1.5,'east-void-inner-edge')

# Lift shaft walls and sliding access doors. Cab interiors are omitted.
wall([(430,570),(540,569),(558,550)],6,'upper-lift-shaft-north-wall')
wall([(430,570),(430,640),(452,640)],6)
wall([(538,570),(538,638),(524,638)],6)
wall([(488,570),(488,638)],5)
wall([(483,638),(495,638)],6)
sliding((452,637),(483,637),'upper-west-lift-door')
sliding((495,637),(524,637),'upper-east-lift-door')
wall([(426,713),(549,713),(549,766),(426,766),(426,714)],6,'lower-lift-shafts')
wall([(486,713),(486,764)],5)
# Accesses in the north face are represented as real gaps in this boundary.
for node in list(walls):
    if node.get('id')=='lower-lift-shafts': walls.remove(node)
wall([(426,713),(426,766),(549,766),(549,713),(531,713)],6,'lower-lift-shafts')
wall([(426,713),(443,713)],6)
wall([(475,713),(493,713)],6)
sliding((443,712),(475,712),'lower-west-lift-door')
sliding((493,712),(531,712),'lower-east-lift-door')
opening((424,716),(392,716),-1,'lower-stair-lobby-door')
wall([(388,710),(391,710),(391,716)],4)

# Accessible compartments between the lift lobby and the diagonal outer wall.
wall([(539,638),(562,638)],5)
wall([(559,552),(603,595)],6)
line(walls,(603,595),(636,627),fill='none',stroke_width='1.5',stroke_dasharray='5 3',id='accessible-room-upper-boundary')
wall([(583,616),(589,610)],4)
opening((583,616),(562,638),-1,'upper-accessible-room-door')
wall([(581,625),(609,653)],3.5,'accessible-room-divider')
opening((611,655),(594,673),1,'lower-accessible-room-door')
wall([(611,655),(620,648)],4)
wall([(636,633),(746,736),(746,812),(555,812),(555,713),(594,673)],6,'lower-bathroom-shell')
wall([(557,713),(581,713),(581,693)],3.5)
wall([(581,713),(632,713),(632,718)],3.5)
wall([(613,666),(632,685),(632,691)],3)
wall([(670,665),(670,717)],3.5,'bathroom-upper-east-divider')
wall([(670,682),(688,682)],3)
wall([(696,717),(696,713),(722,713)],3)
opening((632,711),(632,691),1,'accessible-bathroom-entry')
opening((696,717),(674,717),1,'upper-east-bathroom-entry')
wall([(670,717),(674,717)],3)
opening((632,737),(632,718),-1,'bathroom-west-access')
opening((670,737),(670,718),1,'bathroom-east-access')
wall([(632,737),(632,741)],3)
wall([(670,737),(670,741)],3)
for y in (741,764,788):
    wall([(600,y),(643,y)],3)
    wall([(654,y),(696,y)],3)
wall([(643,741),(643,809)],3.5,'bathroom-west-stall-back')
wall([(654,741),(654,809)],3.5,'bathroom-east-stall-back')
for i,(y,h) in enumerate([(741,23),(764,24),(788,21)]):
    wall([(600,y),(600,y+4)],2.5)
    wall([(696,y),(696,y+4)],2.5)
    opening((600,y+h),(600,y+4),1,f'west-stall-{i+1}')
    opening((696,y+h),(696,y+4),-1,f'east-stall-{i+1}')

# Stair treads, landings and circulation arrows, without room text.
def flight(a,b,depth,count,side=1):
    dx,dy=b[0]-a[0],b[1]-a[1]; n=hypot(dx,dy)
    nx,ny=-dy/n*depth*side,dx/n*depth*side
    for i in range(count+1):
        t=i/count; p=(a[0]+dx*t,a[1]+dy*t)
        line(stairs,p,(p[0]+nx,p[1]+ny))
    line(stairs,a,b,stroke_width='1.2')
    line(stairs,(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),stroke_width='1.2')
def arrow(p):
    el(stairs,'polyline',points=pts(p),stroke_width='1')
    a,b=p[-2:]; dx,dy=b[0]-a[0],b[1]-a[1]; n=hypot(dx,dy); ux,uy=dx/n,dy/n
    el(stairs,'polyline',points=pts([(b[0]-5*ux+2.5*uy,b[1]-5*uy-2.5*ux),b,(b[0]-5*ux-2.5*uy,b[1]-5*uy+2.5*ux)]),stroke_width='1')

flight((595,319),(676,343),35,13)
flight((568,405),(649,430),35,13,-1)
line(stairs,(585,353),(696,387),stroke_width='1.4')
line(stairs,(579,370),(691,404),stroke_width='1.4')
path(stairs,'M 595,319 C 555,307 520,390 568,405',stroke_width='1.1')
arrow([(569,387),(657,414),(673,365),(586,338)])
line(stairs,(632,331),(604,359),stroke_width='1.1')
line(stairs,(639,333),(611,361),stroke_width='1.1')

flight((840,401),(921,426),35,13)
flight((813,489),(894,514),35,13,-1)
line(stairs,(829,436),(941,470),stroke_width='1.4')
line(stairs,(824,452),(936,486),stroke_width='1.4')
path(stairs,'M 840,401 C 800,389 765,474 813,489',stroke_width='1.1')
arrow([(816,471),(902,497),(918,449),(833,422)])
line(stairs,(879,413),(851,444),stroke_width='1.1')
line(stairs,(886,415),(858,446),stroke_width='1.1')

# Bottom U-return staircase and its enclosing edges.
wall([(391,739),(391,868),(550,868),(550,766)],3.5,'south-stair-enclosure')
flight((432,769),(510,769),37,13)
flight((432,866),(510,866),37,13,-1)
line(stairs,(432,806),(510,806),stroke_width='1.5')
line(stairs,(432,829),(510,829),stroke_width='1.5')
line(stairs,(510,806),(510,829),stroke_width='1.5')
line(stairs,(510,813),(548,813))
line(stairs,(510,823),(548,823))
path(stairs,'M 432,769 C 378,770 378,865 432,866',stroke_width='1.1')
path(stairs,'M 510,769 C 563,775 563,861 510,866',stroke_width='1.1')
arrow([(435,788),(530,788),(530,847),(433,847)])
line(stairs,(473,769),(484,806),stroke_width='1.2')
line(stairs,(478,769),(489,806),stroke_width='1.2')

ET.indent(svg,space='  ')
out=ROOT/'img19-architectural.svg'
ET.ElementTree(svg).write(out,encoding='utf-8',xml_declaration=True)
print(out)
print('Vector geometry elements:',sum(n.tag.rsplit('}',1)[-1] in {'line','path','polygon','polyline','rect','circle'} for n in svg.iter()))
