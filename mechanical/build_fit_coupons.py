from pathlib import Path
import cadquery as cq,json,trimesh
D=Path(__file__).resolve().parent;C=json.loads((D/'parameters.json').read_text());O=D/'fit_coupons';O.mkdir(exist_ok=True);a,b=C['motor_cross'];cross=[(-a/2,0),(a/2,0),(0,-b/2),(0,b/2)]
for n,h in [('H_mount_fit',5),('V_mount_fit',8)]:
 p=cq.Workplane('XY').box(30,24,h).translate((0,0,h/2)).edges('|Z').fillet(2)
 for x,y in cross:
  p=p.cut(cq.Workplane('XY').center(x,y).circle(C['M3_clearance']/2).extrude(h+2).translate((0,0,-1)))
  if n.startswith('H'):p=p.cut(cq.Workplane('XY').center(x,y).circle(3.6).extrude(.5))
 for ext in ['step','stl']:cq.exporters.export(p,str(O/(n+'.'+ext)))
 m=trimesh.load_mesh(O/(n+'.stl'));assert m.is_watertight
print('2 fit coupons, not production assembly parts')
