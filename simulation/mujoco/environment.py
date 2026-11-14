"""Fully submerged, still-water rigid-body demonstrator with explicit uncalibrated buoyancy/drag.
No CFD, added mass, waves, free surface, tether, ESC electrical model or optical refraction.
"""
from pathlib import Path
import json,numpy as np,mujoco,math
S=Path(__file__).resolve().parent
class ROV:
 def __init__(self,configuration="base"):
  if configuration not in ('base','with-buoyancy'):raise ValueError('Unknown assembly configuration: '+configuration)
  self.configuration=configuration
  self.k=json.loads((S/'config.json').read_text());self.map=json.loads((S/'ACTUATOR_MAP.json').read_text());self.model=mujoco.MjModel.from_xml_path(str(S/('simple_rov_with_buoyancy.xml' if configuration=='with-buoyancy' else 'simple_rov.xml')));self.data=mujoco.MjData(self.model);self.bid=mujoco.mj_name2id(self.model,mujoco.mjtObj.mjOBJ_BODY,'rov');self.A=np.array(self.map['allocation_matrix'])[[0,2,3,5]];self.force=np.zeros(4);self.reset()
 def reset(self,roll=0,yaw=0):
  mujoco.mj_resetData(self.model,self.data);self.data.qpos[3:7]=[np.cos(yaw/2)*np.cos(roll/2),np.cos(yaw/2)*np.sin(roll/2),np.sin(yaw/2)*np.sin(roll/2),np.sin(yaw/2)*np.cos(roll/2)];self.force[:]=0;mujoco.mj_forward(self.model,self.data)
 def state(self):
  R=self.data.xmat[self.bid].reshape(3,3);jp=np.zeros((3,self.model.nv));jr=np.zeros_like(jp);mujoco.mj_jacBodyCom(self.model,self.data,jp,jr,self.bid)
  rpy=np.array([math.atan2(R[2,1],R[2,2]),math.asin(np.clip(-R[2,0],-1,1)),math.atan2(R[1,0],R[0,0])]);return self.data.xpos[self.bid].copy(),rpy,jp@self.data.qvel,jr@self.data.qvel
 def allocate(self,surge_N,heave_N,roll_Nm,yaw_Nm):return np.linalg.solve(self.A,np.array([surge_N,heave_N,roll_Nm,yaw_Nm]))
 def controller(self,depth=1.2,surge_N=0,yaw=0,roll=0):
  p,rpy,v,w=self.state();R=self.data.xmat[self.bid].reshape(3,3);net=9.80665*(self.k['water_density_kg_m3']*self.k['assumed_displaced_volume_m3']-self.k['assumed_dry_mass_kg']);heave=(12*(-depth-p[2])-8*v[2]-net-R[2,0]*surge_N)/max(.3,R[2,2]);wb=R.T@w;err=math.atan2(math.sin(yaw-rpy[2]),math.cos(yaw-rpy[2]));return self.allocate(surge_N,heave,.6*(roll-rpy[0])-.18*wb[0],.35*err-.15*wb[2])
 def step(self,forces):
  k=self.k;d=self.data;m=self.model;dt=m.opt.timestep;target=np.clip(np.array(forces,dtype=float),-k['assumed_reverse_limit_N'],k['forward_limit_N']);self.force+=(target-self.force)*(1-np.exp(-dt/k['assumed_motor_time_constant_s']));d.ctrl[:]=self.force;d.qfrc_applied[:]=0
  R=d.xmat[self.bid].reshape(3,3);_,_,v,w=self.state();vb=R.T@v;wb=R.T@w;f=-np.array(k['assumed_linear_drag'])*vb-np.array(k['assumed_quadratic_drag'])*np.abs(vb)*vb;t=-np.array(k['assumed_angular_linear_drag'])*wb-np.array(k['assumed_angular_quadratic_drag'])*np.abs(wb)*wb
  mujoco.mj_applyFT(m,d,R@f,R@t,d.xipos[self.bid],self.bid,d.qfrc_applied)
  buoy=k['water_density_kg_m3']*9.80665*k['assumed_displaced_volume_m3'];cb=d.xpos[self.bid]+R@np.array(k['assumed_CB_m']);mujoco.mj_applyFT(m,d,np.array([0.,0.,buoy]),np.zeros(3),cb,self.bid,d.qfrc_applied)
  mujoco.mj_step(m,d)
  if not np.isfinite(d.qpos).all():raise RuntimeError('Nonfinite simulation state')
  if d.xpos[self.bid,2]>-.12:raise RuntimeError('Fully-submerged model used too close to surface; reduce target depth command')
  return self.state()
