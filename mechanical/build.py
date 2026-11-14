"""Original MANTA V5 mechanical design. Supplier solids remain unscaled references."""
from pathlib import Path
import cadquery as cq, math,json,csv,hashlib
import numpy as np,trimesh
D=Path(__file__).resolve().parent
C=json.loads((D/'parameters.json').read_text());parts=[];bolts=[]
MY=C['thruster_half_spacing'];VY=C['vertical_half_spacing'];HX=C['horizontal_X'];HZ=C['horizontal_Z'];VZ=C['vertical_Z'];CLR=C['M3_clearance'];A,B=C['motor_cross'];CROSS=[(-A/2,0),(A/2,0),(0,-B/2),(0,B/2)]
def box(a,b,c,x=0,y=0,z=0):return cq.Workplane('XY').box(a,b,c).translate((x,y,z))
def cyl(r,h,x=0,y=0,z=0,axis='z'):
 p=cq.Workplane('XY').circle(r).extrude(h).translate((0,0,-h/2))
 if axis=='x':p=p.rotate((0,0,0),(0,1,0),90)
 if axis=='y':p=p.rotate((0,0,0),(1,0,0),90)
 return p.translate((x,y,z))
def rr(a,b,t,r,x=0,y=0,z=0):return box(a,b,t,x,y,z).edges('|Z').fillet(r)
def add(n,p,kind='PRINT',color=(.06,.18,.22),pose=None):
 assert p.val().isValid(),n
 if kind=='PRINT':assert len(p.solids().vals())==1,(n,len(p.solids().vals()))
 parts.append(dict(name=n,p=p,kind=kind,color=color,pose=pose))
def hole(p,x,y,z,h=30,diam=CLR,axis='z'):return p.cut(cyl(diam/2,h,x,y,z,axis))
L=C['frame_length'];W=C['frame_width']
# Closed perimeter, connected rear beam, forward beam, two saddle rails and central keel.
frame=rr(L,W,6,22,z=-15).cut(rr(L-24,W-24,10,14,z=-15))
for x,w in [(HX,16),(-38,30),(50,16)]:frame=frame.union(box(w,W-12,6,x,0,-15))
for y,w in [(-36,14),(36,14),(0,24)]:frame=frame.union(box(L-12,w,6,0,y,-15))
# Full-height rim is interrupted at motor ports, never a pressure seal.
rim=rr(L,W,6,22,z=-9).cut(rr(L-12,W-12,12,16,z=-8))
Hports=cyl(32,260,0,MY,HZ,'x').union(cyl(32,260,0,-MY,HZ,'x'))
Vports=cyl(32,220,0,VY,0).union(cyl(32,220,0,-VY,0))
lip=rr(L-6,W-6,2,19,z=-5).cut(rr(L-12,W-12,6,16,z=-5))
for xx in (-101,101):
 for yy in (-18,18):lip=lip.cut(box(8,12,6,xx,yy,-5))
frame=frame.union(rim).union(lip).cut(Hports).cut(Vports)
# OEM tangent mount at Z=-13; recessed underside washers leave nominal 3mm motor engagement.
for cy in (-MY,MY):
 frame=frame.union(box(32,26,6,HX,cy,-15)).cut(box(26,20,1.2,HX,cy,-12.4))
 for dx,dy in CROSS:frame=hole(frame,HX+dx,cy+dy,-15).cut(cyl(3.6,.5,HX+dx,cy+dy,-17.75))
# Two lower pod saddles and four hard-stop clamp feet.
for x in (-50,50):
 p=cyl(34,12,x,0,22,'x').cut(cyl(C['pod_bore']/2,16,x,0,22,'x')).intersect(box(16,90,50,x,0,-3))
 p=p.union(box(12,72,8,x,0,-8))
 for y in (-38,38):p=hole(p.union(box(12,12,6,x,y,19)),x,y,19)
 p=p.cut(cyl(C['pod_bore']/2,16,x,0,22,'x'));frame=frame.union(p)
# Side fork grooves capture only the metal flange's external side lobes.
# Acrylic OD58 passes through bore58.6; slot7.2 accommodates metal flange thickness6 with clearance.
for x in (-78,78):
 for y in (-30,30):
  stop=box(14,12,34,x,y,5).cut(cyl(29.3,18,x,0,22,'x')).cut(cyl(32.5,7.2,x,0,22,'x'))
  frame=frame.union(stop)
# Lid feet outside endcaps and clear of motor/tool paths.
for x in (-95,95):
 for y in (-18,18):frame=hole(frame.union(cyl(5.5,6,x,y,-9)),x,y,-12)
# Structural skid connections and four-bolt feet for each gusseted vertical module.
for x in (-80,80):
 for y in (-97,97):frame=hole(frame.union(box(16,16,6,x,y,-15)),x,y,-15).cut(cyl(4,10,x,y,-7))
for cy in (-VY,VY):
 for x in (-44,-30):
  for y in (cy-21,cy+21):frame=hole(frame,x,y,-15)
# Ballast slots and broad foam-strap slots connect to the actual load-bearing frame.
for x in (-20,20):frame=frame.cut(cq.Workplane('XY').center(x,0).slot2D(12,3.4).extrude(12).translate((0,0,-21)))
for x in (-101,-35,35,101):
 for y in (-32.5,32.5):frame=frame.cut(rr(3,7,32,1,x,y,-10))
# Dedicated tether eye, connected to perimeter and keel. Do not lift by fairing or motor leads.
eye=box(20,10,20,-94,0,-2).edges('|Y').fillet(3).cut(cyl(3,16,-96,0,0,'y'))
frame=frame.union(eye)
for y in (-8,8):frame=frame.cut(cyl(2,20,-86,y,-15))
add('V5_01_LOAD_CHASSIS',frame)
# Split upper shell: free-flooded protective fairing with four unobstructed motor passages.
outer=rr(L,W,66,22,z=27).edges('>Z').fillet(5)
inner=rr(L-4.8,W-4.8,68,19.6,z=23.6).edges('>Z').fillet(4)
cover=outer.cut(inner).cut(Hports).cut(Vports)
# Delete lower side skirts severed by the motor arches; no loose slivers in the print.
for yy in (-107,107):cover=cover.cut(box(260,24,24,0,yy,0))
cover=cover.cut(box(35,60,46,102,0,27)).cut(box(35,46,38,-102,0,25)).cut(box(20,16,22,-104,0,-3))
for x in (-95,95):
 for y in (-18,18):
  ear=box(13,10,4,math.copysign(98.5,x),y,-4).union(cyl(5,4,x,y,-4))
  cover=hole(cover.union(ear),x,y,-4,h=14).cut(cyl(4,100,x,y,48))
# Shallow lip locates the fairing; shell is deliberately free-flooded.
for x in (-65,65):
 for y in (-30,0,30):cover=cover.cut(cyl(2.5,15,x,y,60))
for xx in (-101,-35,35,101):
 for yy in (-32.5,32.5):cover=cover.cut(rr(3,7,100,1,xx,yy,40))
cover=cover.cut(cq.Workplane('XY').text('V5',11,.7).translate((-8,0,59.4)))
arrow=cq.Workplane('XY').polyline([(25,-2),(39,-2),(39,-5),(48,0),(39,5),(39,2),(25,2)]).close().extrude(.7).translate((0,0,59.4));cover=cover.cut(arrow)
add('V5_02_UPPER_FAIRING',cover,color=(.98,.5,.04),pose='flip')
# Side skids: deep roots, floor fillets; nut slots remain side-loadable.
for y in (-97,97):
 p=rr(210,12,8,3,0,y,-84)
 for x in (-80,80):
  p=p.union(box(16,12,62,x,y,-49))
  # Triangular in-plane braces shorten the unsupported leg near the runner.
  for sg in (-1,1):
   rib=cq.Workplane('XZ').polyline([(x+sg*8,-80),(x+sg*23,-80),(x+sg*8,-60)]).close().extrude(12).translate((0,y+6,0));p=p.union(rib)
  p=hole(p,x,y,-23,h=16)
  pocket=cq.Workplane('XY').polygon(6,5.7/math.cos(math.pi/6)).extrude(2.8).translate((x,y,-25));p=p.cut(pocket).cut(box(6.8,16,2.8,x,y,-23.6))
 add('V5_03_SKID_'+str(y),p,pose='side_y')
for x in (-50,50):
 p=cyl(33.5,12,x,0,22,'x').cut(cyl(C['pod_bore']/2,16,x,0,22,'x')).intersect(box(16,90,40,x,0,42))
 for y in (-38,38):p=hole(p.union(box(12,12,4,x,y,24)),x,y,24)
 add('V5_04_POD_CLAMP_'+str(x),p,color=(.1,.35,.38),pose='end_x')
# Original 8mm gusseted two-row, four-bolt vertical carriers replace V4's single thin wall.
for cy in (-VY,VY):
 t=C['vertical_bracket_thickness'];bw=C['vertical_bracket_width']
 p=box(t,bw,48,-31-t/2,cy,-42).union(box(30,52,8,-38,cy,-22).cut(cyl(32,12,0,cy,-22)))
 for yy in (cy-15,cy+15):
  rib=cq.Workplane('XZ').polyline([(-51,-26),(-39,-26),(-39,-64)]).close().extrude(4).translate((0,yy+2,0));p=p.union(rib)
 for x in (-44,-30):
  for y in (cy-21,cy+21):p=hole(p,x,y,-35,h=45)
 for dz,dy in CROSS:p=hole(p,-35,cy+dy,VZ+dz,h=30,axis='x')
 add('V5_05_VERTICAL_CARRIER_'+str(cy),p,color=(.1,.35,.38),pose='end_x')
# Native, rigidly transformed commercial pressure hardware. No scaling/seal redesign.
tube=cq.importers.importStep(str(D/'supplier/BR-106277-150_RevB.STEP')).translate((75,0,22))
front=cq.importers.importStep(str(D/'supplier/BR-102922-998_RevB.step')).rotate((0,0,0),(0,1,0),90).translate((59.5,0,22)).rotate((0,0,22),(1,0,22),270)
window=cq.importers.importStep(str(D/'supplier/WTE2-P-END-CAP-R2.STEP')).rotate((0,0,0),(0,0,1),30).rotate((0,0,0),(0,1,0),90).translate((81,0,22)).rotate((0,0,22),(1,0,22),270)
rear=cq.importers.importStep(str(D/'supplier/BR-102922-009_RevC.step')).rotate((0,0,0),(0,1,0),-90).translate((-59.5,0,22)).rotate((0,0,22),(1,0,22),270)
for n,p,col in [('TUBE',tube,(.55,.68,.72)),('FRONT_FLANGE',front,(.3,.4,.43)),('FRONT_WINDOW',window,(.65,.85,.9)),('REAR_CAP',rear,(.3,.4,.43))]:add('BUY_'+n,p,'SUPPLIER',col)
cam=cq.importers.importStep(str(D/'supplier/LOW-LIGHT-HD-USB-CAMERA-R1.STEP')).rotate((0,0,0),(0,0,1),-90).translate((54,16,38)).rotate((0,0,22),(1,0,22),180);add('BUY_CAMERA_HD_USB',cam,'SUPPLIER',(.14,.45,.22))
# Generic module tray and mechanically screwed camera carrier.
tray=rr(100,35,2,3,x=-5,z=7)
for x in (-40,-20,0,20):
 for y in (-10,10):tray=tray.cut(cq.Workplane('XY').center(x,y).slot2D(8,3.4).extrude(8).translate((0,0,3)))
for x in (-50,32):tray=tray.union(box(8,35,9,x,0,1.7).intersect(cyl(24.2,8,x,0,22,'x')))
for y in (-10,10):tray=hole(tray,42,y,7,h=12)
add('V5_06_MODULE_TRAY',tray,color=(.15,.4,.43))
# YZ plane outer ring, positive feet on tray; four 28x28 M2 camera holes.
carrier=box(4,34,34,48,0,22).cut(box(8,26,22,49,0,22))
for yy in (-12,12):carrier=carrier.union(box(8,10,4,42,yy,10))
for yy in (-15,15):
 rib=cq.Workplane('XZ').polyline([(44,12),(50,12),(50,18)]).close().extrude(4).translate((0,yy+2,0));carrier=carrier.union(rib)
carrier=carrier.cut(box(18,13,8,45,-4.5,36))
for y in (-14,14):
 for z in (8,36):carrier=hole(carrier.union(cyl(2.5,4,52,y,z,'x')),52,y,z,h=20,diam=2.2,axis='x')
for yy in (-14,14):carrier=carrier.cut(cyl(2.8,2.8,45.4,yy,8,'x'))
for yy in (-14,14):
 for zz in (8,36):
  pocket=cq.Workplane('YZ').center(yy,zz).polygon(6,4.2/math.cos(math.pi/6)).extrude(2.6).translate((45.8,0,0)).rotate((0,yy,zz),(1,yy,zz),30);carrier=carrier.cut(pocket)
for y in (-10,10):carrier=hole(carrier,42,y,10,h=12)
add('V5_07_CAMERA_CARRIER',carrier,color=(.15,.4,.43),pose='end_x')
# Commercial X2 references reconstructed from the drawing only; do not print.
def x2():
 p=cyl(28.19,60,axis='x').cut(cyl(25,64,axis='x')).union(box(20,12,3,0,0,-29.5))
 for aa in (0,120,240):p=p.union(box(3,27,3,-26,13.5,0).rotate((0,0,0),(1,0,0),aa))
 p=p.union(cyl(9,25,axis='x'))
 # Connect blades to hub so the reference imports as one solid; illustrative geometry.
 for aa in (0,120,240):p=p.union(box(2,21,5,12,10.5,0).rotate((0,0,0),(1,0,0),aa))
 return p
for name,cy in [('H_LEFT',MY),('H_RIGHT',-MY)]:add('REF_X2_'+name,x2().translate((HX,cy,HZ)),'DRAWING_REFERENCE',(.28,.32,.34))
for name,cy in [('V_LEFT',VY),('V_RIGHT',-VY)]:add('REF_X2_'+name,x2().rotate((0,0,0),(0,1,0),90).translate((0,cy,VZ)),'DRAWING_REFERENCE',(.28,.32,.34))
for x in (-69,69):
 foam=rr(C['foam_length'],C['foam_width'],C['foam_height'],5,x,0,60+C['foam_height']/2+.5)
 for yy in (-18,18):foam=foam.cut(cyl(6,60,math.copysign(95,x),yy,80))
 add('BUY_TRIM_FOAM_'+str(x),foam,'FOAM',(.85,.87,.81))
# Four longitudinal straps avoid every thruster, pod end and lid bolt.
for side in (-1,1):
 lo,hi=(-101,-35) if side<0 else (35,101);fl,fh=(-100,-38) if side<0 else (38,100)
 for yy in (-32.5,32.5):
  outer=[(lo-.6,-19.2),(hi+.6,-19.2),(hi+.6,60),(fh+.6,96.7),(fl-.6,96.7),(lo-.6,60)]
  inner=[(lo+.6,-18),(hi-.6,-18),(hi-.6,60),(fh,95.5),(fl,95.5),(lo+.6,60)]
  tie=cq.Workplane('XZ').polyline(outer).close().extrude(4.8).cut(cq.Workplane('XZ').polyline(inner).close().extrude(8).translate((0,1,0))).translate((0,yy+2.4,0))
  add(f'BUY_FOAM_STRAP_{side}_{yy}',tie,'SOFT_HARDWARE',(.09,.1,.11))
# Purchased hardware modeled as nominal solids, not modeled thread helices.
def align(p,point,axis='z',sgn=1):
 if axis=='x':p=p.rotate((0,0,0),(0,1,0),90*sgn)
 elif sgn<0:p=p.rotate((0,0,0),(1,0,0),180)
 return p.translate(point)
def screw(n,L,point,axis='z',sgn=-1,m=3):
 r=m/2;hr=2.75 if m==3 else 1.9;hh=m
 p=cyl(r,L,z=L/2).union(cyl(hr,hh,z=-hh/2));add(n,align(p,point,axis,sgn),'HARDWARE',(.7,.72,.74));bolts.append(dict(name=n,length=L,point=point,axis=axis,sign=sgn,metric=m))
def washer(n,point,axis='z',sgn=1,m=3):
 r,ir,h=(3.5,1.6,.5) if m==3 else (2.5,1.1,.3)
 add(n,align(cyl(r,h,z=h/2).cut(cyl(ir,2,z=h/2)),point,axis,sgn),'HARDWARE',(.7,.72,.74))
def nut(n,point,axis='z',sgn=1,m=3):
 af,h=(5.5,2.4) if m==3 else (4,1.6)
 p=cq.Workplane('XY').polygon(6,af/math.cos(math.pi/6)).extrude(h).cut(cyl(m/2-.25,6,z=h/2));add(n,align(p,point,axis,sgn),'HARDWARE',(.7,.72,.74))
def joint(n,L,x,y,top,bottom,skid=False):
 screw(n+'_M3x'+str(L),L,(x,y,top+.5));washer(n+'_W_TOP',(x,y,top))
 if skid:nut(n+'_NUT',(x,y,-24.8))
 else:washer(n+'_W_BOTTOM',(x,y,bottom),sgn=-1);nut(n+'_NUT',(x,y,bottom-.5),sgn=-1)
for x in (-95,95):
 for y in (-18,18):joint(f'COVER_{x}_{y}',25,x,y,-2,-18)
for x in (-80,80):
 for y in (-97,97):joint(f'SKID_{x}_{y}',16,x,y,-12,-18,True)
for x in (-50,50):
 for y in (-38,38):joint(f'CLAMP_{x}_{y}',16,x,y,26,16)
for cy in (-VY,VY):
 for x in (-44,-30):
  for y in (cy-21,cy+21):
   n=f'VFOOT_{x}_{y}';screw(n+'_M3x20',20,(x,y,-26.5),sgn=1);washer(n+'_W_BOTTOM',(x,y,-26.5));washer(n+'_W_TOP',(x,y,-12));nut(n+'_NUT',(x,y,-11.5))
for name,cy in [('LEFT',MY),('RIGHT',-MY)]:
 for j,(dx,dy) in enumerate(CROSS):screw(f'HMOTOR_{name}_{j}_M3x8',8,(HX+dx,cy+dy,-18),sgn=1);washer(f'HMOTOR_{name}_{j}_W',(HX+dx,cy+dy,-18))
for name,cy in [('LEFT',VY),('RIGHT',-VY)]:
 for j,(dz,dy) in enumerate(CROSS):screw(f'VMOTOR_{name}_{j}_M3x12',12,(-39.5,cy+dy,VZ+dz),'x',1);washer(f'VMOTOR_{name}_{j}_W',(-39.5,cy+dy,VZ+dz),'x')
for y in (-10,10):joint(f'CAMFOOT_{y}',12,42,y,12,6)
for y in (-14,14):
 for z in (8,36):
  n=f'CAMERA_{y}_{z}';screw(n+'_M2x10',10,(55.9,y,z),'x',-1,m=2);washer(n+'_W_FRONT',(55.6,y,z),'x',m=2);nut(n+'_NUT',(46.8,y,z),'x',m=2)
# Factory-specified six M2x0.4-10 endcap screws, no added washer stack.
for j in range(6):
 a=math.radians(300+j*60);screw(f'OEM_WINDOW_{j}_M2x10',10,(87.35,25.4*math.sin(a),22-25.4*math.cos(a)),'x',-1,m=2)
# Export boundary: verification executes only the definitions above.
if __name__=='__main__':
 for folder in ['stl','step_parts','assembly_meshes']:
  (D/folder).mkdir(exist_ok=True)
  for old in (D/folder).glob('*'):old.unlink()
 ass=cq.Assembly(name='SimpleROV_Base');option=cq.Assembly(name='SimpleROV_WithBuoyancy');full=cq.Assembly(name='SimpleROV_BaseWithFasteners');optional_full=cq.Assembly(name='SimpleROV_WithBuoyancyAndFasteners');hg=cq.Assembly(name='Fasteners');manifest=[]
 for it in parts:
  n,p=it['name'],it['p'];b=p.val().BoundingBox();optional=it['kind'] in ('FOAM','SOFT_HARDWARE')
  if it['kind']=='HARDWARE':hg.add(p,name=n,color=cq.Color(*it['color']))
  else:
   option.add(p,name=n,color=cq.Color(*it['color']))
   if not optional:ass.add(p,name=n,color=cq.Color(*it['color']))
  if it['kind']=='PRINT':
   cq.exporters.export(p,str(D/'step_parts'/(n+'.step')));q=p
   if it['pose']=='flip':q=q.rotate((0,0,0),(1,0,0),180)
   if it['pose']=='side_y':q=q.rotate((0,0,0),(1,0,0),90)
   if it['pose']=='end_x':q=q.rotate((0,0,0),(0,1,0),90)
   bb=q.val().BoundingBox();q=q.translate((-(bb.xmin+bb.xmax)/2,-(bb.ymin+bb.ymax)/2,-bb.zmin))
   cq.exporters.export(q,str(D/'stl'/(n+'.stl')),tolerance=.08);m=trimesh.load_mesh(D/'stl'/(n+'.stl'));m.apply_translation([0,0,-float(m.bounds[0,2])]);m.export(D/'stl'/(n+'.stl'));assert m.is_watertight and len(m.split())==1,n
  if it['kind']!='HARDWARE':cq.exporters.export(p,str(D/'assembly_meshes'/(n+'.stl')),tolerance=.15)
  manifest.append(dict(name=n,kind=it['kind'],color=it['color'],bounds=[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax],volume_mm3=p.val().Volume(),solids=len(p.solids().vals()),print_pose=it['pose'],optional_buoyancy=optional))
 folder=D/'assemblies';folder.mkdir(exist_ok=True)
 ass.export(str(folder/'simple-rov.step'));option.export(str(folder/'simple-rov-with-buoyancy.step'))
 full.add(ass,name='Robot');full.add(hg,name='Fasteners');full.export(str(folder/'simple-rov-with-fasteners.step'))
 optional_full.add(option,name='Robot');optional_full.add(hg,name='Fasteners');optional_full.export(str(folder/'simple-rov-buoyancy-with-fasteners.step'))
 (D/'parts.json').write_text(json.dumps(manifest,indent=2));(D/'bolt_locations.json').write_text(json.dumps(bolts,indent=2))
 configurations={'default':'base','units':'mm','base':{'label':'Standard assembly','optional_buoyancy':False,'step':'assemblies/simple-rov.step'},'with-buoyancy':{'label':'Optional buoyancy module fitted','optional_buoyancy':True,'step':'assemblies/simple-rov-with-buoyancy.step'}}
 for key in ('base','with-buoyancy'):
  selection=[x for x in manifest if x['kind']!='HARDWARE' and (key=='with-buoyancy' or not x['optional_buoyancy'])]
  bounds=[v for j in range(3) for v in (min(x['bounds'][2*j] for x in selection),max(x['bounds'][2*j+1] for x in selection))]
  configurations[key]['bounds_mm']=bounds;configurations[key]['dimensions_mm']=[round(bounds[2*j+1]-bounds[2*j],2) for j in range(3)]
  configurations[key]['included_parts']=[x['name'] for x in selection]
 (D/'configurations.json').write_text(json.dumps(configurations,indent=2)+'\n')
 print('EXPORTED',len(parts),'prints',sum(i['kind']=='PRINT' for i in parts),'default: base, optional: with-buoyancy',flush=True)
