"""Manual architectural SVG trace in the source image's coordinate system."""
from pathlib import Path
from math import hypot
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)

def tag(n): return '{' + SVG + '}' + n
def num(n): return f'{n:.3f}'.rstrip('0').rstrip('.')
def points(p): return ' '.join(f'{num(x)},{num(y)}' for x,y in p)
def el(g, kind, **attrs):
    return ET.SubElement(g, tag(kind), {k.replace('_','-'):str(v) for k,v in attrs.items()})

svg = ET.Element(tag('svg'), width='1255', height='1040', viewBox='0 0 1255 1040', version='1.1')
svg.set('shape-rendering','geometricPrecision')
el(svg,'title').text = 'Architectural trace of img25 — walls, doors, accesses and stairs'
el(svg,'desc').text = ('Reviewed editable manual vector trace of OriginalFloorplan/img25.jpg. '
    'The original image coordinate system and proportions are retained. '
    'Four layers contain walls and structural columns, door leaves and swings, '
    'access thresholds, and three staircases. No embedded image, furniture, '
    'equipment, room labels, coloured room areas, floor tiles or site annotations. '
    'Dashed facade window-swing symbols are not represented as doors. '
    'Short wall sections obscured by labels are estimated from adjacent visible lines; '
    'openings hidden by those labels cannot be verified from this source. '
    'This is an image-based architectural trace, not a measured construction drawing.')

def layer(name, **attrs):
    g=el(svg,'g', id=name.lower(), **attrs)
    g.set('{'+INK+'}groupmode','layer')
    g.set('{'+INK+'}label',name)
    return g

walls=layer('Walls',fill='#30363b',stroke='#30363b',stroke_linejoin='miter')
stairs=layer('Stairs',fill='none',stroke='#30363b',stroke_width='.9',stroke_linejoin='round')
accesses=layer('Accesses',fill='none',stroke='#30363b',stroke_width='.7')
doors=layer('Doors',fill='none',stroke='#30363b',stroke_width='1.1',stroke_linecap='round')
door_records=[]

def wall(p,w=4,id=None):
    attrs=dict(points=points(p),fill='none',stroke_width=num(w),stroke_linecap='butt')
    if id: attrs['id']=id
    return el(walls,'polyline',**attrs)
def block(p,id=None):
    return el(walls,'polygon',points=points(p),stroke_width=0,**({'id':id} if id else {}))
def rect(x,y,w,h,id=None): return block([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],id)
def col(x,y,r): return el(walls,'circle',cx=x,cy=y,r=r,stroke_width=0)
def line(g,a,b,**attrs):
    return el(g,'line',x1=num(a[0]),y1=num(a[1]),x2=num(b[0]),y2=num(b[1]),**attrs)
def path(g,d,**attrs): return el(g,'path',d=d,**attrs)
def threshold(a,b,id=None):
    return line(accesses,a,b,stroke_dasharray='2.5 2',**({'id':id} if id else {}))
def door(a,b,side=1,id=None,access=True):
    door_records.append(dict(a=a,b=b,side=side,id=id))
    dx,dy=b[0]-a[0],b[1]-a[1]
    r=hypot(dx,dy)
    tip=(a[0]-dy*side,a[1]+dx*side)
    g=el(doors,'g',**({'id':id} if id else {}))
    line(g,a,tip,stroke_width='1.15')
    path(g,f'M {num(b[0])},{num(b[1])} A {num(r)},{num(r)} 0 0 {1 if side>0 else 0} {num(tip[0])},{num(tip[1])}',stroke_width='.8')
    if access: threshold(a,b)
def double(a,b,side=1,id=None,ratio=.5):
    mid=(a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio)
    door(a,mid,side,id and id+'-a')
    door(b,mid,-side,id and id+'-b')
def sliding(a,b,id=None):
    g=el(doors,'g',**({'id':id} if id else {}))
    dx,dy=b[0]-a[0],b[1]-a[1]
    r=hypot(dx,dy)
    nx,ny=-dy/r*1.3,dx/r*1.3
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    line(g,a,b,stroke_width='.7')
    line(g,(a[0]+nx,a[1]+ny),(mid[0]+nx,mid[1]+ny),stroke_width='1')
    line(g,(mid[0]-nx,mid[1]-ny),(b[0]-nx,b[1]-ny),stroke_width='1')
    threshold((a[0]-nx*2,a[1]-ny*2),(b[0]-nx*2,b[1]-ny*2))

# Perimeter and structural piers. Facade glazing patterns are omitted.
wall([(16,1006),(16,425),(30,355),(349,33),(900,28)],4.5,'west-north-envelope')
wall([(900,28),(1224,22),(1224,80)],2.2,'terrace-north-boundary')
wall([(16,1006),(386,1006),(386,734)],4,'south-east-classroom-envelope')
wall([(386,869),(548,869),(548,812),(744,812),(744,735),(926,534),(970,546)],4,'south-east-envelope')
wall([(970,546),(1240,74),(899,218)],2,'terrace-outer-edge')
wall([(899,37),(899,366)],3.2,'dining-terrace-envelope')
wall([(899,384),(973,384),(922,525),(973,544)],5.5,'east-corner-wall')
wall([(899,218),(1085,137),(1085,40),(1058,40),(1058,35),(899,35)],1.6,'terrace-upper-boundary')
wall([(899,381),(1013,381),(1239,74)],1.4,'terrace-lower-boundary')

block([(13,406),(24,409),(24,415),(38,415),(37,432),(17,432),(17,448),(12,448)])
block([(25,348),(41,351),(38,364),(32,363),(29,373),(21,371)])
block([(344,32),(353,29),(367,29),(367,42),(355,42),(355,52),(347,52)])
rect(526,26,23,14)
block([(527,35),(519,37),(515,41),(515,47),(519,50),(533,50),(538,46),(538,36)],'north-wall-column-return')
rect(688,25,27,22)
rect(873,24,25,21)
rect(12,714,22,23)
block([(12,892),(26,893),(26,905),(38,905),(38,921),(25,921),(25,935),(13,935)])
block([(13,985),(33,985),(33,997),(43,997),(43,1011),(13,1011)])
block([(181,991),(191,991),(191,986),(208,986),(208,997),(221,997),(221,1011),(181,1011)])
block([(360,998),(371,998),(371,986),(390,986),(390,1011),(360,1011)])
block([(372,906),(389,906),(389,921),(372,921)])
col(352,44,5.5)
col(252,147,7)
col(131,276,6)
col(547,57,6)
col(362,442,6.7)
col(251,395,5)
col(708,207,5.5)
col(888,213,5)

# Offices along the diagonal facade and the north row.
wall([(352,46),(379,113),(395,102),(398,102)],5,'north-west-office-divider')
wall([(416,103),(518,103),(518,49)],3.2,'professors-office-south-east')
wall([(518,103),(560,103)],3.2)
wall([(580,103),(680,103)],3.5)
wall([(700,103),(713,103)],3.5)
wall([(580,33),(580,103)],3.8,'north-office-partition')
wall([(713,44),(713,279)],5,'dining-west-partition')
wall([(244,141),(252,147),(295,197)],7,'diagonal-office-divider')
wall([(295,197),(363,131)],3.2,'second-diagonal-office-front')
obscured_return=wall([(274,218),(280,224),(273,230)],3.2,'sau-door-return-obscured-by-label')
el(obscured_return,'title').text='Estimated jamb return beneath the opaque OFICINES label; not directly verifiable in the source image.'
wall([(221,282),(273,230)],3.2,'sau-director-partition')
wall([(263,323),(317,266),(345,293)],3.2,'small-office-divider')
wall([(303,253),(317,266)],3.2,'small-office-front-visible-section')
wall([(286,237),(303,253)],3.2,'small-office-front-obscured-section')
block([(305,364),(359,307),(369,316),(318,376),(315,371),(365,316),(359,312),(309,368)],'accounts-office-north-divider')
wall([(385,331),(423,367),(441,387)],3.2)
wall([(362,419),(423,367)],3)
wall([(160,225),(163,230),(427,485)],5,'lab-office-divider')
wall([(429,483),(411,501)],5,'lab-north-east-return')
wall([(417,473),(439,452),(471,365)],7,'office-corridor-south')
wall([(483,339),(514,247),(544,257)],7,'office-corridor-north')
wall([(596,233),(635,233)],3.5,'office-service-north-west')
wall([(657,233),(713,233)],3.5,'office-service-north-east')
wall([(583,234),(571,263),(628,281),(715,281)],4,'office-service-south')
wall([(634,233),(620,275)],3)
wall([(611,233),(600,272)],2.5)
wall([(714,279),(782,279)],5,'dining-south-west')
wall([(807,279),(811,279),(811,385),(876,385)],5.5,'dining-south-east')

# Lab south edge, west offices and the meeting room.
wall([(33,422),(215,480),(215,522),(223,522)],5,'lab-south-west-partition')
wall([(251,522),(362,522),(362,649),(341,649)],6,'meeting-room-north-east')
wall([(265,522),(265,647),(275,647)],3.8,'meeting-room-west')
wall([(299,647),(362,647)],3.8)
wall([(215,522),(215,563)],3.6)
wall([(215,594),(215,739)],4.2,'west-office-corridor-partition')
wall([(79,437),(79,626)],3.3,'west-office-spine')
wall([(79,670),(79,727)],3.3)
wall([(16,647),(79,647)],4)
wall([(16,727),(215,727)],5,'classroom-north-partition')
wall([(104,595),(215,595)],3.6)
wall([(79,595),(83,595)],3.2)
wall([(215,739),(215,742)],3.7)
wall([(215,774),(215,778),(282,778)],4,'classroom-entry-west-return')
wall([(313,777),(313,699),(337,699)],5,'classroom-entry-east-return')
wall([(363,699),(386,699),(386,716)],5)
wall([(313,738),(319,738)],3)
wall([(368,738),(386,738)],4)
rect(374,728,14,16)
wall([(362,649),(362,653)],5)
wall([(337,699),(343,695),(362,695)],5)
wall([(200,987),(200,801)],2.1,'classroom-internal-partition')
path(walls,'M 200,801 Q 200,778 220,778',fill='none',stroke_width='2.1')
wall([(200,986),(200,1006)],2.1)

# The corridor return beside the lab access and first plant room.
block([(360,521),(366,527),(366,555),(386,555),(386,526),(430,483),(424,478),(380,520),(374,517)])
wall([(359,489),(389,519)],4,'lab-door-south-jamb')
wall([(365,613),(382,613)],4.5)
wall([(419,613),(430,613)],4.5)
wall([(430,645),(430,539)],5.5,'lift-core-west')
wall([(430,539),(434,535)],5)
wall([(447,522),(457,516)],5)
wall([(474,499),(485,484)],5)
wall([(451,519),(470,537),(504,504)],4.5,'plant-room-entry-return')
wall([(431,573),(542,573),(561,554)],5.5,'plant-room-south')
wall([(486,484),(561,554)],6)

# Triangular light wells: their surrounding walls only.
wall([(485,484),(529,446),(692,503),(601,596)],5.5,'west-lightwell')
wall([(494,485),(531,454),(682,506),(601,587),(494,485)],1.2,'west-lightwell-inner-edge')
wall([(645,630),(785,486),(925,532),(740,727)],5.5,'east-lightwell')
wall([(652,627),(787,495),(916,535),(737,718)],1.2,'east-lightwell-inner-edge')
wall([(486,485),(743,735)],7.5,'diagonal-core-envelope')

# North lift bank and accessible-room enclosure, without lift machinery or fixtures.
wall([(430,574),(430,641),(452,641)],6,'north-lift-west')
wall([(482,641),(501,641)],6)
wall([(531,641),(561,641)],5)
wall([(490,575),(490,635)],5)
wall([(539,575),(539,641)],5.5)
wall([(442,578),(483,578),(483,634),(442,634),(442,578)],1.8)
wall([(494,578),(531,578),(531,634),(494,634),(494,578)],1.8)
wall([(540,633),(560,633)],3.5)
wall([(579,619),(600,595)],3.5)
wall([(578,623),(609,656)],4)
wall([(633,635),(638,630)],3.2)
wall([(552,712),(589,676)],5,'south-service-corridor')
wall([(609,656),(615,650)],4)

# South lift bank and bathroom partitions (no plumbing fixtures or tile grid).
wall([(386,714),(393,714)],5)
wall([(423,714),(451,714)],6)
wall([(480,714),(499,714)],6)
wall([(528,714),(552,714),(552,772)],6,'south-lift-east')
wall([(427,714),(427,767),(550,767)],6,'south-lift-south')
wall([(489,716),(489,762)],5)
wall([(438,720),(480,720),(480,760),(438,760),(438,720)],1.8)
wall([(495,720),(532,720),(532,760),(495,760),(495,720)],1.8)
wall([(552,771),(552,812),(744,812)],7,'bathroom-south-envelope')
wall([(552,714),(631,714)],4,'bathroom-upper-west')
wall([(612,665),(637,686)],3.3)
wall([(637,710),(637,717)],3.3)
wall([(669,663),(669,714),(717,714)],4)
wall([(638,738),(638,807)],7,'bathroom-central-spine-west')
wall([(652,738),(652,810)],6,'bathroom-central-spine-east')
for y in [742,765,786,808]:
    wall([(597,y),(638,y)],2.2)
    wall([(653,y),(695,y)],2.2)
for lo,hi in [(742,745),(763,767),(784,788),(805,810)]:
    wall([(597,lo),(597,hi)],2.2)
    wall([(695,lo),(695,hi)],2.2)
wall([(633,738),(633,735)],2.4)
wall([(633,714),(633,717)],2.4)
wall([(669,714),(669,717)],2.4)
wall([(669,735),(669,740)],2.4)
wall([(597,740),(633,740)],2.4)
wall([(669,740),(695,740)],2.4)

# Central stair and two adjoining services closets.
wall([(539,298),(719,355)],7,'central-stair-north')
wall([(539,298),(537,307)],5,'central-stair-north-jamb')
wall([(533,327),(522,361)],5,'central-stair-entry-jambs')
wall([(514,386),(510,392),(682,447),(712,355)],7,'central-stair-west-south-east')
rect(514,389,17,13)
block([(536,397),(547,400),(543,411),(532,408)])
wall([(514,400),(511,405)],4)
wall([(504,429),(512,434),(515,441),(511,448),(488,473)],5,'central-corridor-return')
wall([(711,355),(724,359)],4.5)
wall([(753,368),(763,372),(733,464),(708,456)],5,'central-services-east')
wall([(700,395),(751,411)],4,'central-services-divider')
wall([(733,464),(742,467)],5)
wall([(765,476),(923,527),(951,432),(807,386)],7,'east-stair-enclosure')
wall([(807,386),(807,379)],5)
wall([(788,391),(789,386)],4)
block([(701,451),(714,454),(711,464),(698,460)])

# Internal door leaves and quarter-circle swings.
door((398,103),(416,103),-1,'north-office-01')
door((580,103),(560,103),1,'north-office-02')
door((700,103),(680,103),1,'north-office-03')
door((379,113),(363,131),1,'diagonal-office-01')
door((295,197),(274,218),1,'diagonal-office-02')
double((471,365),(483,339),-1,'office-main-access',ratio=.65)
door((359,307),(345,293),-1,'small-office-02')
door((369,316),(385,331),1,'accounts-office')
door((457,402),(441,387),-1,'it-office')
double((544,257),(583,234),-1,'office-east-access')
door((635,233),(657,233),1,'office-service-door')
door((807,279),(782,279),-1,'dining-west-access')
door((899,385),(876,385),1,'dining-east-access')
double((223,522),(251,522),1,'laboratory-south-access',ratio=.65)
double((359,489),(394,455),-1,'laboratory-east-access')
double((215,563),(215,591),1,'west-office-main-door',ratio=.36)
door((83,595),(104,595),1,'west-office-south-door')
door((79,647),(79,626),-1,'west-office-middle-door')
door((79,647),(79,670),1,'west-office-lower-door')
door((275,647),(299,647),-1,'meeting-room-door')
double((362,653),(362,695),1,'south-corridor-access')
double((382,613),(419,613),-1,'lift-lobby-west-access')
door((447,522),(434,535),1,'plant-room-main-access')
door((457,516),(474,499),-1,'plant-room-small-access')
door((578,623),(562,639),-1,'accessible-room-north')
door((609,656),(589,676),1,'bathroom-main-door')
threshold((615,650),(633,635),'bathroom-lobby-access')
door((637,710),(637,686),1,'bathroom-accessible-door')
door((633,735),(633,717),-1,'bathroom-west-entry')
door((669,735),(669,717),1,'bathroom-east-entry')
for i,(y1,y2) in enumerate([(745,763),(767,784),(788,805)]):
    door((597,y2),(597,y1),1,f'west-cubicle-{i+1}')
    door((695,y2),(695,y1),-1,f'east-cubicle-{i+1}')
double((215,742),(215,772),-1,'classroom-03-entry',ratio=1/3)
double((282,778),(313,778),-1,'classroom-04-entry',ratio=.4)
double((319,738),(368,738),1,'classroom-service-access')
door((423,716),(393,716),-1,'south-stair-entry')
sliding((452,638),(482,638),'north-lift-door-1')
sliding((501,638),(531,638),'north-lift-door-2')
sliding((451,717),(480,717),'south-lift-door-1')
sliding((499,717),(528,717),'south-lift-door-2')

door((540,306),(533,327),-1,'central-stair-north-door')
door((514,386),(522,361),1,'central-stair-south-door')
door((511,405),(504,429),-1,'central-corridor-door')
double((724,359),(753,368),-1,'central-services-north-access')
double((762,373),(807,386),1,'east-stair-corridor-access')
door((684,448),(700,453),-1,'central-services-south-access')
door((742,467),(765,476),-1,'east-stair-door')

# Repeated dashed facade symbols denote openable windows, not verified doors.
# Their swings are omitted consistently on every side of the building.

# Three staircases. Treads and landings are true vector linework.
def stair_arrow(g,p):
    el(g,'polyline',points=points(p),stroke_width='.75')
    a,b=p[-2:]
    dx,dy=b[0]-a[0],b[1]-a[1]
    r=hypot(dx,dy); ux,uy=dx/r,dy/r
    left=(b[0]-ux*6-uy*3,b[1]-uy*6+ux*3)
    right=(b[0]-ux*6+uy*3,b[1]-uy*6-ux*3)
    el(g,'polyline',points=points([left,b,right]),stroke_width='.9')

def turn_stair(id,origin,ux,uy,length,width,flight_width,run,steps=13):
    """Local u follows the tread run; local v spans both parallel flights."""
    g=el(stairs,'g',id=id)
    def p(u,v):return(origin[0]+ux*u-uy*v,origin[1]+uy*u+ux*v)
    def ln(a,b,**attrs):line(g,p(*a),p(*b),**attrs)
    el(g,'polyline',points=points([p(0,0),p(length,0),p(length,width),p(0,width),p(0,0)]),stroke_width='1.4')
    for v1,v2 in [(0,flight_width),(width-flight_width,width)]:
        for i in range(steps+1):
            u=run*i/steps
            if not (v1==0 and i in [8]):ln((u,v1),(u,v2))
        ln((0,v2),(run,v2),stroke_width='1.2')
    ln((run,flight_width),(run,width-flight_width),stroke_width='1.1')
    # Narrow well between flights; landing remains clear.
    ln((0,flight_width),(run,flight_width),stroke_width='1.4')
    ln((0,width-flight_width),(run,width-flight_width),stroke_width='1.4')
    ln((run,flight_width),(length,flight_width))
    ln((run,width-flight_width),(length,width-flight_width))
    # The break across the upper flight is a conventional stair break.
    cut=run*.61
    el(g,'polyline',points=points([p(cut-3,0),p(cut+3,flight_width),p(cut+6,flight_width),p(cut,0)]),stroke_width='1.15')
    stair_arrow(g,[p(4,flight_width/2),p(run-2,flight_width/2)])
    stair_arrow(g,[p(run-2,width-flight_width/2),p(4,width-flight_width/2)])
    stair_arrow(g,[p(length-10,flight_width/2),p(length-10,width-flight_width/2)])
    return g

# Same slight rotation as the source drawing.
turn_stair('central-staircase',(594,319),.952,.306,112,90,34,82,13)
turn_stair('east-staircase',(838,405),.953,.303,110,86,32,81,13)

g=el(stairs,'g',id='south-staircase')
el(g,'polyline',points='390,770 547,770 547,869 390,869 390,770',stroke_width='1.5')
for y1,y2 in [(770,810),(830,869)]:
    for i in range(12):
        x=429+i*7
        if not(y1==770 and i==7):line(g,(x,y1),(x,y2))
    line(g,(429,y1),(506,y1),stroke_width='1.2')
    line(g,(429,y2),(506,y2),stroke_width='1.2')
line(g,(429,770),(429,869),stroke_width='1.2')
line(g,(506,770),(506,869),stroke_width='1.2')
line(g,(506,810),(547,810))
line(g,(506,830),(547,830))
el(g,'polyline',points='474,770 479,810 482,810 477,770',stroke_width='1.15')
path(g,'M 429,770 C 377,770 377,869 429,869',stroke_width='1')
path(g,'M 506,770 C 560,770 560,869 506,869',stroke_width='1')
stair_arrow(g,[(433,790),(506,790)])
stair_arrow(g,[(503,849),(430,849)])
stair_arrow(g,[(527,811),(527,829)])

ET.indent(svg,space='  ')
out=ROOT/'img25-architectural.svg'
ET.ElementTree(svg).write(out,encoding='utf-8',xml_declaration=True)
print(out)
print('Vector primitives:',sum(n.tag.rsplit('}',1)[-1] in {'line','polyline','path','polygon','circle'} for n in svg.iter()))
assert not any(n.tag.rsplit('}',1)[-1] in {'image','text','foreignObject'} for n in svg.iter())
ids=[n.attrib['id'] for n in svg.iter() if 'id' in n.attrib]
assert len(ids)==len(set(ids))
