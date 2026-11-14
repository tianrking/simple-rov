from pathlib import Path
import runpy,json,itertools,hashlib
import cadquery as cq,numpy as np,trimesh
D=Path(__file__).resolve().parent;ns=runpy.run_path(str(D/'build.py'),run_name='cad_review');P=ns['parts'];issues=[];tests=0
bounds=lambda p:p.val().BoundingBox()
def overlap(a,b):
 aa,bb=bounds(a),bounds(b)
 return min(min(getattr(aa,k+'max'),getattr(bb,k+'max'))-max(getattr(aa,k+'min'),getattr(bb,k+'min')) for k in 'xyz')>.0001
for a,b in itertools.combinations(P,2):
 if a['kind']!='PRINT' and b['kind']!='PRINT' and not (a['kind']==b['kind']=='SUPPLIER') and 'SOFT_HARDWARE' not in (a['kind'],b['kind']) and set([a['kind'],b['kind']])!={'HARDWARE','SUPPLIER'}:continue
 if not overlap(a['p'],b['p']):continue
 tests+=1;v=a['p'].val().intersect(b['p'].val()).Volume()
 if v>.03:issues.append(dict(a=a['name'],b=b['name'],volume_mm3=v));print('CLASH',issues[-1],flush=True)
toolchecks=[];blocked=[]
for b in ns['bolts']:
 n=b['name'];axis=b['axis'];sg=-b['sign'];q=list(b['point']);j='xyz'.index(axis);q[j]+=sg*b['metric'];exclude=set();condition='assembled'
 if n.startswith(('CLAMP','SKID')):
  condition='fairing/foam/retention straps removed'
  exclude={p['name'] for p in P if p['kind'] in ('FOAM','SOFT_HARDWARE')}|{'V5_02_UPPER_FAIRING'}
  if n.startswith('SKID'):condition+='; horizontal thrusters removed';exclude|={'REF_X2_H_LEFT','REF_X2_H_RIGHT'}
 if n.startswith('CAMERA_'):
  condition='camera module assembled outside pod before tray attachment';exclude={p['name'] for p in P if p['kind'] in ('SUPPLIER','FOAM','DRAWING_REFERENCE') and p['name']!='BUY_CAMERA_HD_USB'}|{p['name'] for p in P if p['kind']=='PRINT' and p['name']!='V5_07_CAMERA_CARRIER'}
 if n.startswith('CAMFOOT_'):
  condition='tray/camera assembled outside pressure pod';exclude={p['name'] for p in P if p['kind'] in ('SUPPLIER','FOAM','DRAWING_REFERENCE') and p['name']!='BUY_CAMERA_HD_USB'}|{p['name'] for p in P if p['kind']=='PRINT' and p['name'] not in ('V5_07_CAMERA_CARRIER','V5_06_MODULE_TRAY')}
 if n.startswith('OEM_WINDOW_'):
  condition='endcap assembled on flange before installation in chassis';exclude={p['name'] for p in P if p['kind'] in ('PRINT','FOAM','DRAWING_REFERENCE')}
 shaft=ns['cyl'](1.5 if b['metric']==3 else 1,90,z=45).union(ns['cyl'](3.3,65,z=57.5));tool=ns['align'](shaft,q,axis,sg);hits=[]
 for r in P:
  if r['name']==n or r['name'] in exclude:continue
  if not overlap(tool,r['p']):continue
  v=tool.val().intersect(r['p'].val()).Volume()
  if v>.03:hits.append(dict(part=r['name'],mm3=v))
 rec=dict(bolt=n,condition=condition,hits=hits);toolchecks.append(rec)
 if hits:blocked.append(rec);print('TOOL',rec,flush=True)
# Visible axial camera rays and vertical inlet/outlet corridors, excluding its own commercial thruster.
flow=[]
for cy in (-ns['VY'],ns['VY']):
 passage=ns['cyl'](27,260,0,cy,-10);hits=[]
 for r in P:
  if r['kind'] not in ('PRINT','SUPPLIER','FOAM'):continue
  if not overlap(passage,r['p']):continue
  v=passage.val().intersect(r['p'].val()).Volume()
  if v>.03:hits.append(dict(part=r['name'],mm3=v))
 flow.append(dict(axis_y_mm=cy,clear_54mm_diameter_corridor_Z_mm=[-140,120],hits=hits))
rays=[]
for h in (-40,0,40):
 for v in (-32,0,32):
  end=np.array([130, np.tan(np.deg2rad(h))*(130-77.35),22+np.tan(np.deg2rad(v))*(130-77.35)]);start=np.array([77.35,0,22]);vec=end-start;wire=cq.Edge.makeLine(cq.Vector(*start),cq.Vector(*end));hits=[]
  for r in P:
   if r['kind']!='PRINT':continue
   if sum(e.Length() for e in r['p'].val().intersect(wire).Edges())>.01:hits.append(r['name'])
  rays.append(dict(horizontal_deg=h,vertical_deg=v,blocked_by_prints=hits))
report=dict(revision='V5-01',geometry_tests=tests,interferences=issues,driver_checks=toolchecks,blocked_drivers=blocked,vertical_corridors=flow,camera_rays=rays,physical_tested=False,scope='Nominal geometry: prints versus all parts, suppliers versus suppliers, hardware versus suppliers, straps versus all parts. Metal-to-metal thread engagement is not an interference test; no OEM X2 internal solid is available. Boolean volume reporting threshold0.03mm3. Not strength, physical fit, manufacturing process, sealing or CFD validation.')
report['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [D/'build.py',D/'parameters.json']}
(D/'GEOMETRY_CHECKS.json').write_text(json.dumps(report,indent=2));print('RESULT',len(issues),len(blocked),'tools',len(toolchecks),'flow',flow,'camera',rays,flush=True)
if issues or blocked or any(f['hits'] for f in flow) or any(r['blocked_by_prints'] for r in rays):raise SystemExit(1)
