from pathlib import Path
import json,xml.etree.ElementTree as E,hashlib
import numpy as np,trimesh
S=Path(__file__).resolve().parent;D=S.parents[1]/'mechanical';C=json.loads((D/'parameters.json').read_text());P=json.loads((D/'parts.json').read_text());K=json.loads((S/'config.json').read_text())
root=E.Element('mujoco',model='MANTA_V5_SimpleROV4');E.SubElement(root,'compiler',angle='radian',meshdir='meshes',inertiafromgeom='false');E.SubElement(root,'option',timestep='.002',gravity='0 0 -9.80665',density='0',viscosity='0',integrator='implicitfast')
vis=E.SubElement(root,'visual');E.SubElement(vis,'global',offwidth='1280',offheight='960');E.SubElement(vis,'headlight',ambient='.5 .5 .5',diffuse='.8 .8 .8');E.SubElement(root,'statistic',center='0 0 -1',extent='2')
asset=E.SubElement(root,'asset');E.SubElement(asset,'texture',name='checker',type='2d',builtin='checker',rgb1='.5 .7 .76',rgb2='.65 .8 .85',width='128',height='128');E.SubElement(asset,'material',name='tiles',texture='checker',texrepeat='12 12',reflectance='.1')
world=E.SubElement(root,'worldbody');E.SubElement(world,'light',pos='0 0 2',dir='0 0 -1',diffuse='.9 .9 .9');E.SubElement(world,'geom',name='pool_floor',type='plane',size='5 5 .1',pos='0 0 -3',material='tiles');E.SubElement(world,'geom',name='surface',type='plane',size='5 5 .01',pos='0 0 0',rgba='.1 .5 .65 .12',contype='0',conaffinity='0',group='2')
for x,y in [(2,0),(2,1),(2,-1)]:E.SubElement(world,'geom',type='box',size='.025 .15 .15',pos=f'{x} {y} -1',rgba='.9 .35 .12 1')
body=E.SubElement(world,'body',name='rov',pos='0 0 -1.2');E.SubElement(body,'freejoint',name='free');E.SubElement(body,'inertial',mass=str(K['assumed_dry_mass_kg']),pos=' '.join(map(str,K['assumed_CG_m'])),diaginertia=' '.join(map(str,K['assumed_inertia_kg_m2'])))
for p in P:
 if p['kind']=='HARDWARE':continue
 n=p['name'];(S/'meshes').mkdir(exist_ok=True);tm=trimesh.load_mesh(D/'assembly_meshes'/(n+'.stl'),process=False)
 if len(tm.faces)>40000:tm=tm.simplify_quadric_decimation(face_count=40000)
 tm.export(S/'meshes'/(n+'.stl'));E.SubElement(asset,'mesh',name=n,file=n+'.stl',scale='.001 .001 .001')
 col=p['color']+[1]
 if n in ('BUY_TUBE','BUY_FRONT_WINDOW'):col[-1]=.22
 E.SubElement(body,'geom',name=n,type='mesh',mesh=n,rgba=' '.join(map(str,col)),contype='0',conaffinity='0',group='1',density='0')
def proxy(n,t,pos,size,**kw):E.SubElement(body,'geom',name=n,type=t,pos=pos,size=size,rgba='.3 .8 .3 .2',group='3',density='0',**kw)
proxy('proxy_chassis','box','0 0 -.015','.105 .105 .003');proxy('proxy_pod','capsule','0 0 .022','.029 .075',quat='.70710678 0 .70710678 0')
for y in [-.097,.097]:
 proxy('proxy_skid_'+str(y),'box',f'0 {y} -.084','.105 .006 .004')
 for x in [-.08,.08]:proxy('proxy_leg_'+str(x)+'_'+str(y),'box',f'{x} {y} -.049','.008 .006 .031')
for x in [-.069,.069]:proxy('proxy_foam_'+str(x),'box',f'{x} 0 .078','.031 .08 .0175')
MY=C['thruster_half_spacing']/1000;VY=C['vertical_half_spacing']/1000;HX=C['horizontal_X']/1000;HZ=C['horizontal_Z']/1000;VZ=C['vertical_Z']/1000;cg=np.array(K['assumed_CG_m']);sites=[]
for n,p,d,sgn in [('H_LEFT',[HX,MY,HZ],[1,0,0],1),('H_RIGHT',[HX,-MY,HZ],[1,0,0],-1),('V_LEFT',[0,VY,VZ],[0,0,1],1),('V_RIGHT',[0,-VY,VZ],[0,0,1],-1)]:
 d=np.array(d);q=sgn*K['assumed_reaction_torque_per_newton_m']*d;E.SubElement(body,'site',name=n,pos=' '.join(map(str,p)),size='.003',rgba='1 .2 .1 1');sites.append(dict(name=n,position_m=p,thrust_direction=d.tolist(),reaction_m_per_N=q.tolist(),wrench_about_CG=np.r_[d,np.cross(np.array(p)-cg,d)+q].tolist()))
E.SubElement(body,'site',name='imu',pos='0 0 0',size='.002');E.SubElement(body,'camera',name='front_camera',pos='.07735 0 .022',xyaxes='0 -1 0 0 0 1',fovy='64')
act=E.SubElement(root,'actuator')
for s in sites:E.SubElement(act,'motor',name=s['name'],site=s['name'],gear=' '.join(map(str,s['thrust_direction']+s['reaction_m_per_N'])),ctrllimited='true',ctrlrange=f"{-K['assumed_reverse_limit_N']} {K['forward_limit_N']}")
sensor=E.SubElement(root,'sensor');E.SubElement(sensor,'framequat',name='attitude',objtype='body',objname='rov');E.SubElement(sensor,'gyro',name='gyro',site='imu');E.SubElement(sensor,'accelerometer',name='accel',site='imu')
E.indent(root);E.ElementTree(root).write(S/'manta_v5.xml',encoding='utf-8',xml_declaration=True)
A=np.array([s['wrench_about_CG'] for s in sites]).T;report=dict(axes='X forward,Y left,Z up; rows Fx,Fy,Fz,Mx,My,Mz; commands Newton',sites=sites,allocation_matrix=A.tolist(),controlled_rows=[0,2,3,5],rank=int(np.linalg.matrix_rank(A)),controlled_rank=int(np.linalg.matrix_rank(A[[0,2,3,5]])),passive_axes=['sway','pitch'],CAD_parameters_sha256=hashlib.sha256((D/'parameters.json').read_bytes()).hexdigest(),CAD_parts_sha256=hashlib.sha256((D/'parts.json').read_bytes()).hexdigest())
(S/'ACTUATOR_MAP.json').write_text(json.dumps(report,indent=2));print('built',report['rank'],report['controlled_rank'])
