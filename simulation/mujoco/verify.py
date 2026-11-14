from pathlib import Path
import json,hashlib
import numpy as np,mujoco
from environment import ROV,S
results={};e=ROV();A=np.array(e.map['allocation_matrix']);got=[]
for i in range(4):
 e.reset();e.data.ctrl[:]=0;e.data.ctrl[i]=1;mujoco.mj_forward(e.model,e.data);jp=np.zeros((3,e.model.nv));jr=np.zeros_like(jp);mujoco.mj_jacBodyCom(e.model,e.data,jp,jr,e.bid);J=np.vstack([jp,jr]);w=np.linalg.solve(J.T,e.data.qfrc_actuator);got.append(w)
err=float(np.max(np.abs(np.array(got).T-A)));assert err<1e-8,err
results['physical_site_wrench_matches_CAD_map_max_error']=err;results['allocation_rank']=int(np.linalg.matrix_rank(A));assert results['allocation_rank']==4
for name,u,idx in [('forward',(2,0,0,0),0),('reverse',(-2,0,0,0),0),('up',(0,2,0,0),2),('down',(0,-2,0,0),2),('yaw',(0,0,0,.04),5),('roll',(0,0,.04,0),3)]:
 e.reset();p0,r0,_,_=e.state();cmd=e.allocate(*u)
 for _ in range(1000):p,r,_,_=e.step(cmd)
 delta=np.r_[p-p0,r-r0][idx];desired=1 if name not in ('reverse','down') else -1;assert desired*delta>.005,(name,delta);results[name]={'signed_change':float(delta),'unit':'m' if idx<3 else 'rad'}
e.reset()
for _ in range(10000):p,r,_,_=e.step(e.controller())
results['hover_20s']={'depth_error_m':float(-p[2]-1.2),'roll_rad':float(r[0]),'pitch_rad':float(r[1])};assert abs(-p[2]-1.2)<.01
for _ in range(4000):p,r,_,_=e.step(e.controller(depth=.9))
results['depth_step']={'target_m':.9,'final_m':float(-p[2])};assert abs(-p[2]-.9)<.02
e.reset(roll=.2)
for _ in range(4000):p,r,_,_=e.step(e.controller())
results['roll_recovery']={'initial_rad':.2,'final_rad':float(r[0])};assert abs(r[0])<.02
e.reset(roll=.2,yaw=1.0)
for _ in range(4000):p,r,_,_=e.step(e.controller(yaw=1.0))
results['roll_recovery_at_rotated_heading']={'initial_roll_rad':.2,'target_yaw_rad':1.0,'final_roll_rad':float(r[0]),'final_yaw_rad':float(r[2])};assert abs(r[0])<.02 and abs(r[2]-1)<.02
results['scope']='Functional checks under assumed uncalibrated mass/CG/CB/thrust/drag. Does not validate a physical robot, pressure depth, structure or optical performance.'
results['source_sha256']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [S/'config.json',S/'manta_v5.xml',S/'ACTUATOR_MAP.json',S/'environment.py']};results['passed']=True;(S/'SIMULATION_CHECKS.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
