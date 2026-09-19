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
el(svg,'desc').text = ('Editable manual vector trace of OriginalFloorplan/img25.jpg. '
    'The original image coordinate system and proportions are retained. '
    'Four layers contain walls and structural columns, door leaves and swings, '
    'access thresholds, and three staircases. No embedded image, furniture, '
    'equipment, room labels, coloured room areas, floor tiles or site annotations. '
    'Short wall sections obscured by labels are estimated from adjacent visible lines. '
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
    dx,dy=b[0]-a[0],b[1]-a[1]
    r=hypot(dx,dy)
    tip=(a[0]-dy*side,a[1]+dx*side)
    g=el(doors,'g',**({'id':id} if id else {}))
    line(g,a,tip,stroke_width='1.15')
    path(g,f'M {num(b[0])},{num(b[1])} A {num(r)},{num(r)} 0 0 {1 if side>0 else 0} {num(tip[0])},{num(tip[1])}',stroke_width='.8')
    if access: threshold(a,b)
def double(a,b,side=1,id=None):
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
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
wall([(16,1006),(386,1006),(386,985)],5,'south-envelope')
wall([(386,936),(386,734)],5,'classroom-east-envelope')
wall([(386,869),(548,869),(548,812),(744,812),(744,735),(926,534),(970,546)],4,'south-east-envelope')
wall([(970,546),(1240,74),(899,218)],2,'terrace-outer-edge')
wall([(899,37),(899,93)],4)
wall([(899,136),(899,285)],4)
wall([(899,326),(899,366)],4)
wall([(899,384),(973,384),(922,525),(973,544)],5.5,'east-corner-wall')
wall([(899,218),(1085,137),(1085,40),(1058,40),(1058,35),(899,35)],1.6,'terrace-upper-boundary')
wall([(899,381),(1013,381),(1239,74)],1.4,'terrace-lower-boundary')
wall([(899,218),(899,381)],1.2)

block([(13,406),(24,409),(24,415),(38,415),(37,432),(17,432),(17,448),(12,448)])
block([(25,348),(41,351),(38,364),(32,363),(29,373),(21,371)])
block([(344,32),(353,29),(367,29),(367,42),(355,42),(355,52),(347,52)])
rect(526,26,23,14)
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
wall([(353,48),(385,111),(393,106)],6,'north-west-office-divider')
wall([(414,102),(518,102),(518,49)],3.2,'professors-office-south-east')
wall([(518,102),(558,102)],3.2)
wall([(581,102),(684,102)],3.5)
wall([(706,102),(715,102)],3.5)
wall([(581,33),(581,104)],3.8,'north-office-partition')
wall([(715,44),(715,278)],5,'dining-west-partition')
wall([(254,151),(293,191),(362,130)],3.6,'second-diagonal-office')
wall([(254,151),(287,190),(299,201)],5)
wall([(188,255),(244,194)],3.5)
wall([(166,230),(212,276),(251,236)],3.2)
wall([(217,285),(272,230)],3.2)
wall([(255,323),(315,263),(346,292)],3.4)
wall([(300,248),(315,263)],3.2)
block([(292,362),(360,305),(371,316),(305,380),(301,375),(365,316),(360,312),(297,367)],'accounts-office-north-divider')
wall([(385,331),(421,364),(441,385)],3.2)
wall([(348,433),(421,364)],3)
wall([(163,230),(392,463)],5,'lab-office-divider')
wall([(420,490),(429,482),(392,445)],4.5,'lab-north-east-return')
wall([(416,472),(441,449),(471,365)],7,'office-corridor-south')
wall([(483,339),(514,247),(544,257)],7,'office-corridor-north')
wall([(597,233),(713,233)],3.5,'office-service-north')
wall([(583,234),(571,263),(628,281),(715,281)],4,'office-service-south')
wall([(634,233),(620,275)],3)
wall([(606,237),(596,269)],2.5)
wall([(714,279),(782,279)],5,'dining-south-west')
wall([(807,279),(811,279),(811,385),(876,385)],5.5,'dining-south-east')

# Lab south edge, west offices and the meeting room.
wall([(33,422),(215,480),(215,522),(222,522)],5,'lab-south-west-partition')
wall([(251,522),(362,522),(362,649),(341,649)],6,'meeting-room-north-east')
wall([(265,522),(265,647),(275,647)],3.8,'meeting-room-west')
wall([(299,647),(362,647)],3.8)
wall([(215,522),(215,563),(207,563)],3.6)
wall([(215,594),(215,739)],4.2,'west-office-corridor-partition')
wall([(79,437),(79,627)],3.3,'west-office-spine')
wall([(79,668),(79,725)],3.3)
wall([(16,647),(79,647)],4)
wall([(16,730),(215,730)],5,'classroom-north-partition')
wall([(104,597),(215,597)],3.6)
wall([(79,597),(79,603)],3.2)
wall([(16,561),(79,561)],2.7,'west-office-label-obscured-divider')
wall([(215,741),(215,748)],3.7)
wall([(215,774),(215,778),(282,778)],4,'classroom-entry-west-return')
wall([(313,777),(313,698),(386,698),(386,716)],5,'classroom-entry-east-return')
wall([(313,738),(319,738)],3)
wall([(368,738),(386,738)],4)
rect(374,728,14,16)
wall([(313,700),(335,700)],5)
wall([(362,649),(362,653)],5)
wall([(338,695),(362,695)],5)
wall([(200,987),(200,801)],2.1,'classroom-internal-partition')
path(walls,'M 200,801 Q 200,778 220,778',fill='none',stroke_width='2.1')
wall([(200,986),(200,1006)],2.1)

# The corridor return beside the lab access and first plant room.
block([(360,522),(368,526),(368,556),(389,556),(389,534),(418,505),(412,500),(381,531),(379,521),(372,516)])
wall([(365,613),(382,613)],4.5)
wall([(419,613),(430,613)],4.5)
wall([(430,645),(430,539)],5.5,'lift-core-west')
wall([(430,539),(439,530)],5)
wall([(479,489),(486,482)],6)
wall([(444,526),(470,537),(504,504)],4.5,'plant-room-entry-return')
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
wall([(540,633),(559,633)],3.5)
wall([(582,614),(600,595)],3.5)
wall([(576,637),(601,662)],4)
wall([(626,635),(633,628)],3.2)
wall([(552,712),(582,685)],5,'south-service-corridor')
wall([(603,665),(607,661)],4)

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
wall([(552,714),(621,714)],4,'bathroom-upper-west')
wall([(599,669),(628,698),(628,710)],3.8)
wall([(669,663),(669,714),(717,714)],4)
wall([(638,738),(638,807)],7,'bathroom-central-spine-west')
wall([(652,738),(652,810)],6,'bathroom-central-spine-east')
wall([(595,740),(637,740)],3)
wall([(653,740),(696,740)],3)
wall([(595,740),(595,744)],2.4)
wall([(595,764),(637,764)],2.4)
wall([(595,784),(637,784)],2.4)
wall([(595,803),(595,810)],2.4)
wall([(595,764),(595,767)],2.4)
wall([(595,784),(595,787)],2.4)
wall([(695,740),(695,744)],2.4)
wall([(652,764),(695,764)],2.4)
wall([(652,784),(695,784)],2.4)
wall([(695,764),(695,767)],2.4)
wall([(695,784),(695,787)],2.4)
wall([(695,803),(695,810)],2.4)
wall([(625,737),(625,734)],2.4)
wall([(625,714),(625,717)],2.4)
wall([(672,714),(672,717)],2.4)
wall([(672,734),(672,738)],2.4)
wall([(621,737),(626,737)],2.4)
wall([(666,737),(674,737)],2.4)

# Central stair and two adjoining services closets.
wall([(539,298),(719,355)],7,'central-stair-north')
wall([(534,320),(521,359)],5,'central-stair-entry-jambs')
wall([(513,383),(510,392),(682,447),(712,355)],7,'central-stair-west-south-east')
rect(514,389,17,13)
block([(536,397),(547,400),(543,411),(532,408)])
wall([(514,400),(511,405)],4)
wall([(504,429),(512,434),(515,441),(511,448),(488,473)],5,'central-corridor-return')
wall([(711,355),(724,359)],4.5)
wall([(751,368),(763,372),(733,464),(707,456)],5,'central-services-east')
wall([(697,430),(691,445)],4)
wall([(700,395),(751,411)],4,'central-services-divider')
wall([(735,466),(741,468)],5)
wall([(763,476),(923,527),(951,432),(807,386)],7,'east-stair-enclosure')
wall([(807,386),(807,379)],5)
wall([(751,412),(765,372)],5)
wall([(781,392),(788,389)],5)
block([(701,451),(714,454),(711,464),(698,460)])

# Internal door leaves and quarter-circle swings.
door((414,102),(393,102),1,'north-office-01')
door((581,102),(558,102),1,'north-office-02')
door((706,102),(684,102),1,'north-office-03')
door((384,112),(363,132),1,'diagonal-office-01')
door((293,198),(272,218),1,'diagonal-office-02')
door((251,236),(270,217),-1,'diagonal-office-03')
door((300,248),(286,234),-1,'small-office-01')
door((360,306),(346,292),-1,'small-office-02')
door((371,316),(385,331),1,'accounts-office')
door((460,402),(441,385),-1,'it-office')
double((471,365),(483,339),-1,'office-main-access')
double((544,257),(583,234),-1,'office-east-access')
door((634,233),(657,233),1,'office-service-door')
door((807,279),(782,279),-1,'dining-west-access')
door((899,385),(876,385),1,'dining-east-access')
double((899,93),(899,136),1,'dining-terrace-north')
double((899,285),(899,326),1,'dining-terrace-south')

double((222,522),(251,522),1,'laboratory-south-access')
double((352,513),(392,473),-1,'laboratory-east-access')
door((215,594),(215,565),-1,'west-office-main-door')
door((80,597),(104,597),1,'west-office-south-door')
door((79,647),(79,627),1,'west-office-middle-door')
door((79,647),(79,668),-1,'west-office-lower-door')
door((275,647),(299,647),-1,'meeting-room-door')
double((362,653),(362,695),1,'south-corridor-access')
double((382,613),(419,613),-1,'lift-lobby-west-access')
double((439,530),(479,489),-1,'plant-room-access')
door((420,491),(401,510),-1,'lab-service-door')
door((578,623),(562,639),-1,'accessible-room-north')
door((601,662),(622,641),-1,'accessible-room-south')
door((601,667),(581,686),-1,'bathroom-main-door')
door((628,710),(628,690),1,'bathroom-accessible-door')
door((625,734),(625,717),-1,'bathroom-west-entry')
door((672,734),(672,717),1,'bathroom-east-entry')
for i,y in enumerate([744,767,787]):
    door((595,y+17),(595,y),1,f'west-cubicle-{i+1}')
    door((695,y+17),(695,y),-1,f'east-cubicle-{i+1}')
door((215,773),(215,749),-1,'classroom-03-entry')
double((282,778),(313,778),-1,'classroom-04-entry')
double((319,738),(368,738),1,'classroom-service-access')
door((423,716),(393,716),-1,'south-stair-entry')
sliding((452,638),(482,638),'north-lift-door-1')
sliding((501,638),(531,638),'north-lift-door-2')
sliding((451,717),(480,717),'south-lift-door-1')
sliding((499,717),(528,717),'south-lift-door-2')

door((540,306),(533,327),-1,'central-stair-north-door')
door((513,386),(521,361),1,'central-stair-south-door')
door((511,405),(504,429),-1,'central-corridor-door')
double((724,359),(751,368),-1,'central-services-north-access')
double((762,373),(807,386),1,'east-stair-corridor-access')
door((710,457),(690,451),1,'central-services-south-access')
door((742,466),(765,473),-1,'east-stair-door')

# Exterior door / opening symbols visible along the lower facade.
for i,y in enumerate([744,780,815,850]):
    door((17,y+35),(17,y),1,f'west-classroom-opening-{i+1}')
for i,y in enumerate([937,962]):
    door((17,y+24),(17,y),1,f'west-lower-opening-{i+1}')
double((386,936),(386,985),1,'classroom-east-exit')
for i,(x1,x2) in enumerate([(44,80),(80,115),(115,150),(150,181),(221,255),(255,290),(290,325),(325,360)]):
    door((x1,1004),(x2,1004),-1,f'south-opening-{i+1}')

# Facade access leaves at the dining room; no frames, blind patterns or glazing hatch.
for i,(a,b) in enumerate([((728,31),(761,31)),((761,31),(795,31)),((796,30),(830,30)),((832,30),(864,30))]):
    door(a,b,1,f'dining-north-opening-{i+1}')

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
