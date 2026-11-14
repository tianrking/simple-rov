from pathlib import Path
import json,csv,hashlib,importlib.metadata,re
import cadquery as cq,trimesh,numpy as np
D=Path(__file__).resolve().parents[1];C=json.loads((D/'mechanical/parameters.json').read_text());P=json.loads((D/'mechanical/parts.json').read_text());B=json.loads((D/'mechanical/bolt_locations.json').read_text());G=json.loads((D/'mechanical/GEOMETRY_CHECKS.json').read_text())
assert not G['interferences'] and not G['blocked_drivers'] and len(G['driver_checks'])==48
for n,h in G['source_sha256'].items():assert hashlib.sha256((D/'mechanical'/n).read_bytes()).hexdigest()==h,n
report=[]
for p in P:
 if p['kind']!='PRINT':continue
 n=p['name'];m=trimesh.load_mesh(D/'mechanical/stl'/(n+'.stl'));s=cq.importers.importStep(str(D/'mechanical/step_parts'/(n+'.step')));delta=abs(s.val().Volume()-p['volume_mm3']);tol=max(.05,p['volume_mm3']*1e-5);bb=s.val().BoundingBox();bd=max(abs(v-u) for v,u in zip([bb.xmin,bb.xmax,bb.ymin,bb.ymax,bb.zmin,bb.zmax],p['bounds']));ok=bool(m.is_watertight and len(m.split())==1 and s.val().isValid() and len(s.solids().vals())==1 and delta<tol and bd<.005 and max(m.extents[:2])<=220 and abs(m.bounds[0,2])<.001);report.append(dict(part=n,passed=ok,STL_watertight=bool(m.is_watertight),STL_components=len(m.split()),print_dimensions_mm=m.extents.tolist(),STEP_valid=s.val().isValid(),STEP_roundtrip_volume_difference_mm3=delta,tolerance_mm3=tol,STEP_bounding_box_difference_mm=bd,STEP_bounding_box_tolerance_mm=.005));assert ok,n
(D/'mechanical/EXPORT_CHECKS.json').write_text(json.dumps(report,indent=2)+'\n')
with (D/'bom/PRINT_MANIFEST.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['part','quantity','material','print_dimensions_mm','STL','editable_STEP','print_pose','support_note'])
 for r in report:
  p=next(p for p in P if p['name']==r['part']);n=r['part'];w.writerow([n,1,'PETG; structural regions solid',' x '.join(f'{x:.2f}' for x in r['print_dimensions_mm']),'../mechanical/stl/'+n+'.stl','../mechanical/step_parts/'+n+'.step',p['print_pose'] or 'base_down','Verify supports in slicer; camera/fairing and flange ears need local support.'])
groups={}
for p in P:
 if p['kind']!='HARDWARE':continue
 n=p['name']
 if '_M3x' in n:key='ISO4762 M3x'+n.split('_M3x')[-1]+' A4-70'
 elif '_M2x' in n:key='ISO4762 M2x'+n.split('_M2x')[-1]+' SS316'
 elif n.startswith('CAMERA_') and '_NUT' in n:key='M2 nut AF4 t1.6 SS316'
 elif n.startswith('CAMERA_'):key='M2 washer OD5 ID2.2 t0.3 SS316'
 elif '_NUT' in n:key='M3 nut AF5.5 t2.4 A4'
 else:key='M3 washer OD7 ID3.2 t0.5 A4'
 groups[key]=groups.get(key,0)+1
with (D/'bom/BOM_FASTENERS.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['specification','installed_quantity','note'])
 for k,v in sorted(groups.items()):
  note='Installed quantity; excludes spares.'
  if 'M3x8 ' in k or 'M3x12 ' in k:note+=' Motor blind-depth must be verified; carrier/tray bolts use same stock lengths.'
  if 'M2x10 ' in k:note+=' Includes6 OEM acrylic endcap screws and4 camera screws; kit contents must not be double-ordered.'
  w.writerow([k,v,note])
with (D/'bom/FASTENER_INSTANCES.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['name','length_mm','metric','axis','direction','head_seat_X','head_seat_Y','head_seat_Z'])
 for b in B:w.writerow([b['name'],b['length'],b['metric'],b['axis'],b['sign'],*b['point']])
rows=[['APISQUEEN X2',4,'2CW+2CCW; one opposite pair per propulsion axis','Official drawing reference only; verify all four M3/depth/cables before buying full set','https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters'],['BR50mm 150mm tube',1,'CAD BR-106277-150 RevB','Current compatible complete kit','https://bluerobotics.com/learn/technical-reference/'],['BR50mm RAILS front flange',1,'CAD BR-102922-998 RevB','O-rings/locking cord per manufacturer','https://bluerobotics.com/learn/technical-reference/'],['BR50mm transparent endcap',1,'BR-100094 / WTE2-P-END-CAP-R2;6OEM M2x10','Factory seal assembly; do not add unapproved washer stack','https://bluerobotics.com/wp-content/uploads/2025/02/WTE-DATASHEET-RevC.2-FEB2025.pdf'],['BR50mm rear flange cap',1,'CAD BR-102922-009 RevC;1M10+8M6','Penetrators/plugs not yet selected; capacity is not a sealed harness','https://bluerobotics.com/learn/technical-reference/'],['Blue Robotics low-light HD USB camera',1,'32x32 PCB;28x28 holes;native STEP','Install PCB rotated180 degrees; correct image in capture pipeline','https://bluerobotics.com/store/sensors-cameras/cameras/cam-usb-low-light-r1/'],['Suitable closed-cell buoyancy foam',2,'Cut62x160x35mm;4D12 tool reliefs total','Grade/depth rating/density to select; actual buoyancy trim unverified',''],['Releasable retention strap',4,'Approx450x4.8mm;band thickness<=1.2mm','Slots3x7;place lockheads on top; wet retention trial required',''],['Closed-cell EPDM saddle liner',2,'1mm thick x12mm width;trim approximate185mm length','Butt joint without overlap; nominal compressed radial gap0.8mm',''],['Closed-cell tray foot pads',2,'Thin liner cut to actual fit','Nominal radial gap0.8mm at R24.2 feet; physical retention unknown',''],['O-rings/locking cords/window factory fasteners',1,'Complete compatible supplier kit','Use supplier kit BOM and assembly instructions; additional seal parts not modeled',''],['Cable penetrators and unused-port plugs',0,'TBD after actual motor cable/host selection','Loose wires/bundles cannot assume single-cable compression seal; do not claim harness complete',''],['Ballast',0,'TBD after weighing;2M3 slots12x3.4','No ballast load or completed trim claimed','']]
with (D/'bom/BOM_PURCHASED.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['item','quantity','optional_quantity','configuration','specification','note','source'])
 for row in rows:
  optional=row[0] in ('Suitable closed-cell buoyancy foam','Releasable retention strap')
  w.writerow([row[0],0 if optional else row[1],row[1] if optional else 0,'optional buoyancy' if optional else 'base',*row[2:]])
I={'revision':'V5-01','units':'mm','axes':'Xforward,Yleft,Zup','thrusters':{},'cover_bolts_XY':[[x,y] for x in (-95,95) for y in (-18,18)],'skid_mounts_XY':[[x,y] for x in (-80,80) for y in (-97,97)],'pod_axis':[0,0,22],'pod_clamps_X':[-50,50],'foam_strap_slots_XY':[[x,y] for x in (-101,-35,35,101) for y in (-32.5,32.5)],'strap_slot_size_XY':[3,7],'camera_board_plane_X':54,'camera_holes_YZ':[[y,z] for y in (-14,14) for z in (8,36)],'camera_mount_print_clearance':2.2,'camera_OEM_hole':2.44,'camera_board_rotation_deg_about_optical_axis':180,'tether_eye':{'center':[-96,0,0],'diameter':6,'axis':'Y','load_rating':'UNTESTED'},'module_slots_XY':[[x,y] for x in (-40,-20,0,20) for y in (-10,10)],'module_slot_size':[8,3.4],'pressure_ports':'1M10+8M6; no penetrator selection frozen','physical_tested':False}
a,b=C['motor_cross'];cross=[(-a/2,0),(a/2,0),(0,-b/2),(0,b/2)]
for name,y in [('H_LEFT',C['thruster_half_spacing']),('H_RIGHT',-C['thruster_half_spacing'])]:I['thrusters'][name]={'axis_position':[C['horizontal_X'],y,C['horizontal_Z']],'positive_thrust':[1,0,0],'mount_plane_Z':-13,'holes':[[dx+C['horizontal_X'],y+dy,-13] for dx,dy in cross],'clearance':3.4,'trial_bolt':'M3x8','trial_engagement':3.0}
for name,y in [('V_LEFT',C['vertical_half_spacing']),('V_RIGHT',-C['vertical_half_spacing'])]:I['thrusters'][name]={'axis_position':[0,y,C['vertical_Z']],'positive_thrust':[0,0,1],'mount_plane_X':-31,'holes':[[-31,y+dy,C['vertical_Z']+dz] for dz,dy in cross],'clearance':3.4,'trial_bolt':'M3x12','trial_engagement':3.5}
(D/'mechanical/INTERFACES.json').write_text(json.dumps(I,ensure_ascii=False,indent=2)+'\n')
with (D/'bom/KEY_HOLES.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f,lineterminator="\n");w.writerow(['group','axis','x_mm','y_mm','z_mm','diameter_mm','note'])
 for k,v in I['thrusters'].items():
  for xyz in v['holes']:w.writerow([k,'Z' if k.startswith('H') else 'X',*xyz,3.4,'OEM all4M3/depth/axial datum unverified'])
 for b in B:w.writerow([b['name'],b['axis'],*b['point'],3.4 if b['metric']==3 else 2.2,'Bolt seat coordinates;see assembly source for actual clearance location'])
F=2.1*9.80665;A=32*8;Z=32*8**2/6;screen={'revision':'V5-01','scope':'Main vertical wall only; ideal full-solid rectangular section, NOT FEA or a safety factor','wall_mm':[32,8],'load_N':F,'eccentricity_mm':35,'nominal_service_MPa':F/A+F*35/Z,'nominal_3x_analysis_load_MPa':3*(F/A+F*35/Z),'not_included':['gusset stiffness','root/hole stress concentrations','joint prying/bolt preload','wet anisotropic FDM strength','creep/fatigue/impact','complete chassis simultaneous thrust loads'],'physical_tested':False,'judgment':'REQUIRES PHYSICAL LOAD AND FIT TEST; no certified load or depth rating'}
(D/'mechanical/STRENGTH_SCREEN.json').write_text(json.dumps(screen,indent=2)+'\n')
for output,names in [('requirements/cad.txt',['cadquery','numpy','trimesh']),('requirements/sim.txt',['mujoco','numpy','Pillow','imageio','imageio-ffmpeg','trimesh','fast-simplification','glfw'])]:
 (D/output).write_text('\n'.join(n+'=='+importlib.metadata.version(n) for n in names)+'\n')
status={'revision':'V5-01','status':'ENGINEERING_PROTOTYPE_DIGITAL_CHECKS_ONLY','original_design':['chassis','fairing','skids','pod mounts and stops','vertical carriers','tray','camera carrier','hydrodynamic demonstrator/controller code'],'purchased_references':['4commercial X2 thrusters','Blue Robotics pressure hardware/camera'],'Onshape_assembly':'https://cad.onshape.com/documents/256f9be06adfdc472f7aac06/w/aefb43ce726d3d5c24877f23/e/1186baa4f5bb2c01f6be971a','printed_assembly_parts':10,'optional_fit_coupons':2,'modeled_metal_fasteners':sum(groups.values()),'modeled_straps':0,'optional_buoyancy_straps':4,'default_configuration':'base','nominal_size_mm':[213,210,148],'size_with_buoyancy_mm':[213,210,184.7],'geometry_interferences':len(G['interferences']),'blocked_driver_paths':len(G['blocked_drivers']),'driver_paths':len(G['driver_checks']),'physical_tested':False,'PCB_in_scope':False,'motor_internal_thread_depth_verified':False,'electrical_payload_and_penetrators_frozen':False}
previous_status=json.loads((D/'STATUS.json').read_text()) if (D/'STATUS.json').exists() else {}
status={**previous_status,**status}
(D/'STATUS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n')
source={'original_design':'MANTA V5 mechanical parts and simulation sources authored for this project; not a copy of a complete ROV CAD','standard_layout':'https://ardupilot.org/sub/docs/sub-frames.html','sources':[{'name':'X2 official product/dimension drawing','url':'https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters','CAD_status':'dimension-reconstructed reference; no OEM X2 solid'},{'name':'Blue Robotics native pressure/camera CAD','url':'https://bluerobotics.com/learn/technical-reference/','CAD_status':'unaltered supplier solids; rigid transforms including locking-entry alignment and window hole phase'},{'name':'Original acrylic endcap CAD attribution','url':'https://bluerobotics.com/our-original-watertight-enclosure-designs-are-now-open-source/','attribution':'Blue Robotics; supplier distributes original endcap designs under CC BY4.0; no blanket license claim for all modern supplier CAD'},{'name':'MuJoCo XML reference','url':'https://mujoco.readthedocs.io/en/stable/XMLreference.html'}],'supplier_SHA256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((D/'mechanical/supplier').glob('*'))},'sim_meshes':'Derived simplified visual meshes only; native STEP and printing STL remain separate. Collision proxies are approximate.'}
previous_sources=json.loads((D/'SOURCES.json').read_text()) if (D/'SOURCES.json').exists() else {}
source={**previous_sources,**source}
(D/'SOURCES.json').write_text(json.dumps(source,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(status,ensure_ascii=False,indent=2));print('PRINT_EXPORT_CHECKS',len(report),'PASS')
