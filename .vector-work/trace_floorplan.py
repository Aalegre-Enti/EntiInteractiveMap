"""Editable, semantic vector trace of the supplied architectural photograph."""
from pathlib import Path
from math import hypot
import xml.etree.ElementTree as ET
import json

ROOT = Path(__file__).resolve().parents[1]
SVG = 'http://www.w3.org/2000/svg'
INK = 'http://www.inkscape.org/namespaces/inkscape'
ET.register_namespace('', SVG)
ET.register_namespace('inkscape', INK)

def tag(name):
    return '{' + SVG + '}' + name

svg = ET.Element(tag('svg'), {
    'width': '1165', 'height': '1050', 'viewBox': '0 0 1165 1050',
    'version': '1.1', 'shape-rendering': 'geometricPrecision',
})
ET.SubElement(svg, tag('title')).text = 'Walls, doors, accesses and stairs — img12'
ET.SubElement(svg, tag('desc')).text = (
    'Manually traced vector drawing from OriginalFloorplan/img12.jpg. '
    'Original image coordinates and aspect ratio are preserved. '
    'Only architectural walls and columns, door leaves and swings, access '
    'thresholds and stairs are drawn. No raster image, labels, furniture, '
    'fixtures, vegetation or site annotations are included. '
    'Geometry is visually estimated from the supplied image; no physical scale is asserted.'
)

def layer(name, **attrs):
    return ET.SubElement(svg, tag('g'), {
        'id': name.lower(), '{'+INK+'}groupmode': 'layer', '{'+INK+'}label': name,
        **{k.replace('_', '-'):str(v) for k,v in attrs.items()}
    })

walls = layer('Walls', fill='#343a40', stroke='#343a40', stroke_linejoin='miter')
stairs = layer('Stairs', fill='none', stroke='#343a40', stroke_width='0.9', stroke_linejoin='round')
accesses = layer('Accesses', fill='none', stroke='#343a40', stroke_width='0.85')
doors = layer('Doors', fill='none', stroke='#343a40', stroke_width='1.1', stroke_linecap='round', stroke_linejoin='round')
door_openings = []

def num(x):
    return f'{x:.3f}'.rstrip('0').rstrip('.')

def pts(coords):
    return ' '.join(f'{num(x)},{num(y)}' for x,y in coords)

def el(group, name, **attrs):
    return ET.SubElement(group,tag(name),{k.replace('_','-'):str(v) for k,v in attrs.items()})

def wall(coords, width=5, name=None):
    attrs = {'points':pts(coords), 'fill':'none', 'stroke-width':num(width), 'stroke-linecap':'butt'}
    if name: attrs['id']=name
    return el(walls,'polyline',**attrs)

def block(coords, name=None):
    attrs = {'points':pts(coords), 'stroke-width':'0'}
    if name: attrs['id']=name
    return el(walls,'polygon',**attrs)

def rect(x,y,w,h,name=None):
    return block([(x,y),(x+w,y),(x+w,y+h),(x,y+h)],name)

def column(x,y,r):
    el(walls,'circle',cx=x,cy=y,r=r,stroke_width=0)

def line(group, a, b, **attrs):
    return el(group,'line',x1=num(a[0]),y1=num(a[1]),x2=num(b[0]),y2=num(b[1]),**attrs)

def path(group,d,**attrs):
    return el(group,'path',d=d,**attrs)

def door(a,b,side=1, name=None):
    """Hinge a; shut tip b; swing 90 degrees toward side of oriented a→b."""
    dx,dy=b[0]-a[0],b[1]-a[1]
    r=hypot(dx,dy)
    door_openings.append({'name':name or 'unnamed', 'a':a, 'b':b, 'length':r})
    tip=(a[0]-dy*side,a[1]+dx*side)
    g=el(doors,'g',**({'id':name} if name else {}))
    line(g,a,tip,stroke_width='1.35')
    path(g,f'M {num(b[0])},{num(b[1])} A {num(r)},{num(r)} 0 0 {1 if side>0 else 0} {num(tip[0])},{num(tip[1])}',stroke_width='0.85')

def double(a,b,side=1,ratio=.5,name=None):
    mid=(a[0]+(b[0]-a[0])*ratio,a[1]+(b[1]-a[1])*ratio)
    door(a,mid,side,name and name+'-a')
    door(b,mid,-side,name and name+'-b')

def threshold(a,b,name=None):
    attrs={'stroke-dasharray':'3 2','stroke-width':'0.65'}
    if name: attrs['id']=name
    line(accesses,a,b,**attrs)

def sliding(a,b,name=None):
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=hypot(dx,dy)
    nx,ny=-dy/length*1.5,dx/length*1.5
    g=el(doors,'g',**({'id':name} if name else {}))
    line(g,a,b,stroke_width='.75')
    mid=((a[0]+b[0])/2,(a[1]+b[1])/2)
    line(g,(a[0]+nx,a[1]+ny),(mid[0]+nx,mid[1]+ny),stroke_width='.75')
    line(g,(mid[0]-nx,mid[1]-ny),(b[0]-nx,b[1]-ny),stroke_width='.75')

# Building envelope. Glazing mullions are deliberately not traced.
wall([(34,576),(37,493),(79,331),(365,35),(567,34)],4.5,'west-and-north-envelope')
wall([(36,613),(36,919)],4.5,'west-lower-envelope')
wall([(617,34),(1075,30),(1105,30)],4.5,'auditorium-north-envelope')
wall([(1105,28),(1129,28)],3)
wall([(1163,27),(1163,126)],4)
wall([(1162,142),(1007,347)],5.5,'east-envelope')
wall([(1007,347),(987,386),(968,456),(976,459)],11,'east-stair-exterior-wall')
wall([(1020,473),(1026,476),(962,536)],6)

# Structural piers along the perimeter.
block([(356,45),(367,33),(390,33),(390,41),(382,41),(381,55),(367,55),(366,49),(360,54)])
rect(532,32,32,22,'north-west-pier')
block([(264,136),(280,151),(273,160),(259,146),(252,152),(246,146)])
block([(147,261),(159,272),(168,278),(156,291),(144,280),(137,287),(130,280)])
block([(76,327),(85,329),(87,339),(79,341),(74,359),(68,357)])
block([(33,534),(46,534),(46,549),(55,549),(55,565),(45,565),(45,576),(33,576)])
block([(33,718),(46,718),(46,728),(55,728),(55,745),(46,745),(46,757),(33,757)])
block([(33,881),(43,881),(43,904),(33,904)])
rect(711,31,35,10)
rect(722,40,14,11)
rect(889,29,37,10)
rect(899,36,16,7)
block([(1069,28),(1104,28),(1104,46),(1077,46),(1077,37),(1069,37)])
block([(1088,197),(1101,205),(1084,230),(1072,221)])
column(1079,398,7)

# Upper teaching rooms and corridor.
wall([(561,52),(561,213)],8,'room-01-east-wall')
wall([(548,218),(560,218)],14)
column(548,218,7)
column(560,218,7)
wall([(545,222),(498,373)],10)
wall([(615,32),(616,302)],6,'passage-east-wall')
wall([(570,33),(570,57)],3)
wall([(573,301),(544,391),(574,400),(575,410)],10,'passage-south-wall')
wall([(539,376),(536,388),(553,393),(548,415)],7)
block([(550,385),(562,389),(559,401),(547,397)])
block([(565,391),(576,395),(573,405),(562,402)])
wall([(531,452),(522,480)],10)
wall([(276,152),(468,339)],5,'room-01-divider')
column(397,270,8.5)
wall([(468,339),(461,339),(438,362)],4.5)
wall([(408,391),(402,397)],5)
wall([(149,282),(258,399),(267,390)],5,'room-02-divider')
wall([(276,394),(342,455)],5)
wall([(273,388),(266,395)],13)
column(266,395,6.5)
wall([(314,421),(353,384)],4)
wall([(316,423),(342,448)],4)

# Lower teaching rooms and circulation walls.
wall([(49,557),(295,557)],6,'room-03-south-divider')
column(222,558,7.5)
wall([(284,557),(284,566)],5)
wall([(284,598),(284,600),(93,600),(93,613),(38,613)],5,'room-04-north-wall')
wall([(267,600),(267,601)],4)
wall([(267,633),(284,633),(284,739),(48,739)],6,'room-04-east-and-south-wall')
column(222,737,7.5)
wall([(284,739),(298,739)],5)
wall([(327,739),(333,739)],5)
block([(34,877),(224,877),(224,902),(231,902),(231,914),(389,914),
       (389,901),(401,901),(401,765),(388,765),(388,718),(408,718),
       (408,921),(34,921)],'room-05-south-and-east-wall')
wall([(332,722),(332,763),(389,763)],5)
wall([(332,722),(337,722),(337,717)],4)
wall([(383,717),(389,717)],4)
wall([(333,598),(333,655),(341,655)],4)
wall([(367,655),(407,655),(407,599)],3.5,'small-room-enclosure')

# Central sanitary-room shell; sanitary fixtures are omitted.
wall([(333,598),(333,462),(400,396)],10,'central-bathroom-shell')
wall([(400,396),(475,465)],15,'central-bathroom-north-wall')
wall([(335,501),(392,501),(417,525)],7)
wall([(406,560),(406,596),(333,596)],7)
block([(404,514),(418,526),(406,538),(406,543),(401,543),
       (398,537),(386,525),(394,517)])
wall([(359,505),(359,526)],3)
wall([(359,543),(359,548)],3)
wall([(338,548),(359,548),(359,552)],3)
wall([(359,569),(359,593)],3)
wall([(441,494),(475,462)],6)
wall([(428,431),(398,462),(394,458)],4,'central-stall-divider-1')
wall([(449,447),(418,478),(421,481)],5,'central-stall-divider-2')
wall([(369,431),(381,443)],3)
wall([(418,478),(412,476)],3)
wall([(435,491),(440,495)],3)

# Auditorium shell and vestibule connections.
wall([(622,35),(623,262),(789,262)],7,'auditorium-west-and-front')
wall([(789,262),(789,252),(795,252)],4)
wall([(791,253),(791,275)],4)
wall([(823,257),(823,252),(869,252),(869,257)],5)
wall([(903,276),(903,252),(908,252),(908,270),(961,270),(1079,118),(1079,45)],6,'auditorium-east-and-front')
line(walls,(853,36),(853,235),fill='none',stroke_width='1.2',stroke_dasharray='4 2',id='auditorium-operable-partition')

# Upper sanitary-room partitions and the first stair enclosure.
wall([(619,300),(619,317),(732,352),(704,448),(615,422)],8,'north-stair-enclosure')
wall([(623,266),(789,266)],3)
wall([(652,267),(652,281)],2.5)
wall([(674,266),(674,275),(686,275),(686,266)],3)
wall([(689,266),(689,274)],3)
wall([(689,299),(689,307),(684,335)],4)
wall([(690,308),(707,308)],4)
wall([(724,307),(758,307)],4)
wall([(783,307),(790,307)],4)
wall([(733,309),(733,398)],2.5,'north-accessible-stall-partition')
wall([(790,265),(790,276)],4)
wall([(790,300),(790,360),(786,362),(774,399),(722,399)],6,'north-bathroom-east-wall')
wall([(775,399),(764,436)],5)
wall([(758,458),(756,465),(705,449)],8,'north-service-room-wall')
wall([(776,406),(781,408),(778,413)],6)
wall([(809,414),(815,416)],8)

# East service enclosure and stair.
wall([(827,380),(881,380)],6)
wall([(905,379),(905,345),(919,345)],5,'east-service-room')
wall([(969,345),(1007,345)],5)
wall([(905,385),(987,385)],9)
wall([(918,346),(918,378),(906,378)],3)
wall([(971,346),(971,382)],3)
wall([(827,380),(795,483)],9,'east-stair-west-wall')
wall([(831,391),(971,434)],8)
wall([(830,499),(962,536)],9,'east-stair-south-wall')

# Diagonal structural spine and upper lift enclosures.
block([(521,478),(667,617),(650,634),(641,619),(623,601),
       (617,605),(605,594),(611,587),(574,551),(513,497)],'diagonal-structural-spine')
wall([(449,549),(458,540)],5)
wall([(479,518),(490,530),(526,496)],5)
wall([(449,549),(449,716)],4,'lift-lobby-west-wall')
wall([(449,569),(555,569),(575,550)],8)
wall([(558,574),(558,639),(545,639)],7)
wall([(449,639),(472,639)],7)
wall([(503,639),(519,639)],7)
wall([(559,575),(577,557)],5)
wall([(560,635),(609,635),(609,618)],5)
wall([(609,635),(628,635)],5)

# Lower lift bank, service rooms and stairs.
wall([(448,717),(470,717)],8)
wall([(500,717),(517,717)],8)
wall([(548,715),(679,713),(685,719)],8)
wall([(450,719),(450,771),(709,771)],8)
wall([(570,716),(570,772)],10)
rect(573,714,22,57)
wall([(619,716),(619,732)],4)
wall([(619,757),(619,771)],4)
wall([(702,733),(705,736),(705,771)],5)
wall([(734,771),(766,771),(766,749),(737,719)],11,'main-entrance-south-pier')
wall([(737,719),(742,711)],6)
wall([(572,775),(572,815),(769,815),(769,776)],8,'lower-east-stair-enclosure')
wall([(573,774),(708,774)],3)
wall([(735,774),(741,774)],3)
wall([(741,801),(741,815)],3)
wall([(411,719),(446,719)],2)
wall([(409,754),(414,754)],5)
wall([(444,753),(450,753)],5)
wall([(408,813),(410,813)],6)
wall([(443,813),(531,813)],7)
wall([(445,813),(445,909)],5,'lower-exit-stair-wall')

# Porch structural elements visible in the original crop.
rect(80,992,150,24,'porch-wall')
column(42,1004,6)

# Door leaves and swings, including uneven pairs.
double((572,57),(611,57),-1,name='north-passage-entrance')
double((575,301),(614,301),-1,name='passage-fire-doors')
double((503,368),(536,378),-1,.63,'passage-west-doors')
double((468,340),(498,350),1,.30,'classroom-01-doors')
double((408,389),(438,363),1,.65,'classroom-02-doors')
double((352,385),(380,411),-1,.50,'classroom-02-service-doors')
double((298,559),(327,559),1,.32,'classroom-03-doors')
double((284,566),(284,598),1,.73,'classroom-03-west-door')
double((267,601),(267,632),-1,.75,'classroom-04-doors')
double((298,740),(327,740),-1,.33,'classroom-05-doors')
double((35,577),(35,612),1,name='west-exit')
double((339,717),(383,717),-1,name='south-service-doors')
door((341,655),(367,655),-1,'small-room-door')
door((405,541),(405,559),1,'central-bathroom-entry')
door((358,543),(358,526),-1,'central-lower-stall-1')
door((358,552),(358,569),1,'central-lower-stall-2')
door((416,524),(441,498),-1,'central-upper-bathroom-entry')
door((394,458),(381,443),1,'central-upper-stall-1')
door((399,463),(412,476),-1,'central-upper-stall-2')
door((435,491),(421,478),1,'central-upper-stall-3')
door((479,519),(459,540),1,'central-stair-lower-door')
double((500,498),(476,475),1,.65,'central-stair-upper-doors')
double((549,417),(534,453),-1,name='west-vestibule-doors')
double((576,410),(613,422),1,name='north-stair-doors')
double((795,258),(823,258),1,.69,'auditorium-west-doors')
double((870,258),(899,258),1,.31,'auditorium-east-doors')
door((791,276),(791,300),1,'north-bathroom-entry')
door((689,275),(689,299),-1,'north-west-stall-door')
door((724,307),(707,307),-1,'north-middle-stall-door')
door((758,457),(765,435),-1,'north-service-door')
door((777,413),(807,422),1,'east-corridor-door')
door((903,379),(881,379),1,'east-service-door')
double((919,343),(968,343),-1,name='east-service-access')
double((799,486),(834,497),1,.50,'east-stair-doors')
double((974,457),(1022,473),-1,name='east-exit-doors')
door((624,601),(609,617),-1,'upper-service-inner-door')
door((641,618),(626,634),-1,'upper-service-outer-door')
sliding((472,642),(503,642),'upper-lift-door-west')
sliding((519,642),(545,642),'upper-lift-door-east')
sliding((470,716),(500,716),'lower-lift-door-west')
sliding((517,716),(548,716),'lower-lift-door-east')
door((685,716),(702,733),-1,'lower-service-entry')
double((620,732),(620,756),-1,name='lower-service-cupboard')
door((734,772),(709,772),1,'lower-east-stair-door')
door((741,778),(765,778),1,'lower-east-exit')
door((413,756),(443,756),1,'lower-west-stair-door')
double((410,813),(442,813),1,name='lower-west-exit')

# Access thresholds. Existing door gaps remain open in the wall layer.
for a,b,name in [
    ((572,57),(611,57),'north-access'),
    ((35,577),(35,612),'west-access'),
    ((974,457),(1022,473),'east-access'),
    ((741,778),(765,778),'south-east-access'),
    ((410,813),(442,813),'south-west-access'),
]:
    threshold(a,b,name)

# Main entrance screen, revolving door and conventional exit leaves.
# The closely spaced diagonal lines are retained as the entrance threshold.
g=el(accesses,'g',id='main-entrance-threshold')
for i in range(12):
    t=i/11
    line(g,(741+29*t,706+28*t),(920+40*t,525+13*t),stroke_width='.65')
el(doors,'circle',id='revolving-entrance',cx='856',cy='634',r='35.5',stroke_width='1.8')
line(doors,(820.5,634),(891.5,634),stroke_width='1.7')
line(doors,(856,598.5),(856,669.5),stroke_width='1.7')
double((768,728),(811,685),1,name='main-entrance-exit-doors')

# Stair geometry utilities; flights are drawn with individual vector treads.
def flight(a,b,depth,count,side=1,dashed=False):
    """a→b is the run; the cross-flight dimension is depth."""
    dx,dy=b[0]-a[0],b[1]-a[1]
    length=hypot(dx,dy)
    nx,ny=-dy/length*depth*side,dx/length*depth*side
    st={'stroke-dasharray':'3 2'} if dashed else {}
    for i in range(count+1):
        t=i/count
        p=(a[0]+dx*t,a[1]+dy*t)
        line(stairs,p,(p[0]+nx,p[1]+ny),**st)
    line(stairs,a,b,**st)
    line(stairs,(a[0]+nx,a[1]+ny),(b[0]+nx,b[1]+ny),**st)

def stair_arrow(coords):
    el(stairs,'polyline',points=pts(coords),stroke_width='1')
    a,b=coords[-2],coords[-1]
    dx,dy=b[0]-a[0],b[1]-a[1]
    n=hypot(dx,dy)
    ux,uy=dx/n,dy/n
    p=(b[0]-6*ux+2.2*uy,b[1]-6*uy-2.2*ux)
    q=(b[0]-6*ux-2.2*uy,b[1]-6*uy+2.2*ux)
    el(stairs,'polygon',points=pts([b,p,q]),fill='#343a40',stroke_width='0')

# Northern U-return stair.
flight((613,323),(694,347),37,13,1)
flight((588,405),(670,429),37,13,-1,True)
el(stairs,'polyline',points=pts([(694,347),(725,357),(700,439),(670,429)]))
line(stairs,(603,359),(715,392),stroke_width='1.5')
line(stairs,(600,368),(712,402),stroke_width='1.5')
stair_arrow([(604,391),(685,415),(698,374),(622,351)])

# Eastern U-return stair.
flight((844,399),(929,426),40,14,1)
flight((819,486),(904,513),40,14,-1,True)
el(stairs,'polyline',points=pts([(929,426),(964,437),(940,524),(904,513)]))
line(stairs,(832,438),(953,476),stroke_width='1.5')
line(stairs,(829,447),(950,485),stroke_width='1.5')
stair_arrow([(835,475),(918,501),(931,460),(852,435)])

# Short central diagonal flight between the two distributors.
flight((439,505),(475,468),43,7,1)
line(stairs,(446,518),(482,481),stroke_width='1.1')
stair_arrow([(481,482),(449,514)])

# Lower stair groups.
flight((415,722),(415,748),29,4,-1)
stair_arrow([(429,721),(429,740)])
flight((474,777),(527,777),33,9,1)
stair_arrow([(520,790),(480,790)])
flight((581,779),(681,779),29,15,1)
line(stairs,(681,779),(737,779))
line(stairs,(681,808),(737,808))
stair_arrow([(581,793),(681,793)])
flight((411,856),(411,903),32,7,-1)
stair_arrow([(426,858),(426,902)])

# North-east external stair and its landing door.
flight((1083,48),(1160,48),64,22,1)
line(stairs,(1081,114),(1162,114),stroke_width='1.5')
double((1130,44),(1161,44),-1,name='north-east-exit')
threshold((1130,44),(1161,44),'north-east-access')

# Small auditorium stair between the two front entries.
flight((846,235),(846,248),20,4,-1)

# Partially visible exterior stair at the lower edge of the source image.
g=el(stairs,'g',id='south-exterior-stair')
el(g,'polyline',points=pts([(814,1004),(828,1050)]))
el(g,'polyline',points=pts([(850,994),(866,1050)]))
for i in range(9):
    y=1001+i*6
    x=824+(y-1001)*.29
    if y+1.7<=1050:
        line(g,(x,y+7),(x+26,y-1))

ET.indent(svg,space='  ')
out=ROOT/'img12-architectural.svg'
ET.ElementTree(svg).write(out,encoding='utf-8',xml_declaration=True)
(ROOT/'.vector-work'/'door-openings.json').write_text(json.dumps(door_openings),encoding='utf-8')
print(out)
print('Vector elements:',sum(1 for node in svg.iter() if node.tag.rsplit('}',1)[-1] in {'path','polyline','polygon','circle','line'}))
