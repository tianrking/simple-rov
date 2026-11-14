"""Generate English assembly diagrams and native CAD part views."""
from pathlib import Path
import json,xml.etree.ElementTree as E
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,patches
import mujoco
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2];O=R/'docs/assets/images/assembly_guide';O.mkdir(exist_ok=True)
font=font_manager.findfont('DejaVu Sans')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.unicode_minus':False})
INK='#173d46';TEAL='#388a91';ORANGE='#ed8a24'
def finish(fig,name,title):
 fig.suptitle(title,fontsize=17,color=INK);fig.savefig(O/name,dpi=180,bbox_inches='tight',facecolor='white');plt.close(fig)
def box(ax,x,y,w,h,text,color='#e8f1f3',size=11):
 ax.add_patch(patches.FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=1',facecolor=color,edgecolor='#65818a',lw=1.1));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,color=INK)
def arrow(ax,start,end):ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',lw=1.7,color=TEAL))
# Top-layout schematic using the CAD datums.
f,ax=plt.subplots(figsize=(11,7.6));ax.set_aspect('equal');ax.axis('off');ax.set_xlim(-190,190);ax.set_ylim(-145,150)
box(ax,-105,-105,210,210,'',color='#f0f5f5');box(ax,-75,-29,150,58,'Central dry enclosure',color='#c7e0e8',size=10)
for y,label in [(74,'H_LEFT'),(-74,'H_RIGHT')]:
 box(ax,-108,y-28.19,60,56.38,'',color='#9bafb5');ax.text(-78,y+11,label,ha='center',fontsize=10,color=INK);arrow(ax,(-98,y-9),(-47,y-9))
for y,label in [(62,'V_LEFT'),(-62,'V_RIGHT')]:
 ax.add_patch(patches.Circle((0,y),28.19,facecolor=TEAL,edgecolor='white',lw=2));ax.text(0,y,label,ha='center',va='center',color='white',fontsize=9)
ax.add_patch(patches.Circle((72,0),7,fc=INK));arrow(ax,(90,0),(150,0));ax.text(153,0,'FRONT / +X',va='center',color=INK,fontsize=10)
ax.text(0,125,'LEFT / +Y',ha='center',color=INK);ax.text(0,-125,'RIGHT / -Y',ha='center',color=INK)
ax.annotate('Rear penetrator cap',xy=(-78,0),xytext=(-185,35),fontsize=10,color=INK,arrowprops=dict(arrowstyle='->',color=TEAL))
ax.text(-177,-50,'Horizontal axes: X',fontsize=10,color=INK);ax.text(67,83,'Vertical axes: Z',fontsize=10,color=INK)
finish(f,'01_top_layout.png','Top layout | Fairing hidden | Dimensions from CAD')
# Nominal motor engagement stack.
f,axs=plt.subplots(1,2,figsize=(12,5.3))
for ax in axs:ax.axis('off');ax.set_xlim(0,100);ax.set_ylim(0,100)
for ax,title,grip,screw,engage in [(axs[0],'Horizontal motor',5,8,3),(axs[1],'Vertical motor',8.5,12,3.5)]:
 ax.set_title(title,color=INK,fontsize=14);box(ax,15,52,70,30,'OEM mounting foot',color='#cbdadd');box(ax,15,31,70,21,'Frame / carrier',color=TEAL);box(ax,15,25,70,6,'Washer',color='#b1bec3',size=9);box(ax,47,25,6,40,'',color='#647e86');box(ax,37,16,26,9,'Head',color='#b1bec3',size=9)
 ax.text(50,6,f'M3 x {screw} | 4 per motor',ha='center',color=INK,fontsize=12);ax.text(50,92,f'Grip + washer: {grip:g} mm',ha='center',color=INK);ax.text(50,85,f'Target engagement: {engage:g} mm',ha='center',color=INK,fontsize=10)
f.text(.5,.005,'Nominal stack only. Measure actual hole type and blind depth; do not bottom screws.',ha='center',color='#a14b22',fontsize=11)
finish(f,'02_motor_fasteners.png','Thruster fasteners | Trial screw lengths, not verified blind depths')
# Wet/dry logical system diagram.
f,ax=plt.subplots(figsize=(12,5.7));ax.axis('off');ax.set_xlim(0,120);ax.set_ylim(0,60)
box(ax,36,4,82,48,'',color='#f0f6f8');ax.text(77,48,'CENTRAL ENCLOSURE: DRY INTERIOR',ha='center',color=INK,fontsize=13)
box(ax,2,28,26,15,'4 external\nthrusters',color='#a3bdc1');box(ax,40,28,15,15,'Cable\nseals',color='#efd2a4');box(ax,62,28,22,15,'4 bidirectional\nESCs',color='#abc8cd');box(ax,92,28,22,15,'Controller',color='#a3c3c9');box(ax,62,9,22,12,'Power and\nprotection',color='#efd2a4');box(ax,92,9,22,12,'Camera, host\nand sensors',color='#cfdbd0')
for a,b in [((28,35),(40,35)),((55,35),(62,35)),((92,35),(84,35)),((73,21),(73,28))]:arrow(ax,a,b)
ax.text(16,15,'Wet frame and cover',ha='center',color=INK,fontsize=10);ax.text(76,1,'Tray + insulated, board-specific adapters',ha='center',color=INK,fontsize=10)
finish(f,'03_wet_dry.png','Wet / dry boundary | Functional relationships, not a wiring schematic')
# CAD-based 3D renders. Move actual visual meshes, do not invent hardware.
xml=E.parse(R/'simulation/mujoco/simple_rov_with_buoyancy.xml').getroot();xml.find('compiler').set('meshdir',str(R/'simulation/mujoco/meshes'));E.SubElement(xml.find('asset'),'texture',type='skybox',builtin='gradient',rgb1='1 1 1',rgb2='1 1 1',width='512',height='3072');model=mujoco.MjModel.from_xml_string(E.tostring(xml,encoding='unicode'));data=mujoco.MjData(model);renderer=mujoco.Renderer(model,height=900,width=1200)
base_rgba=model.geom_rgba.copy();base_pos=model.geom_pos.copy();base_group=model.geom_group.copy()
P=json.loads((R/'mechanical/parts.json').read_text());names=[p['name'] for p in P if p['kind']!='HARDWARE']
def render(file,include,shifts=None,lookat=(0,0,0),distance=.62,elevation=-24,azimuth=135):
 model.geom_rgba[:]=base_rgba;model.geom_pos[:]=base_pos;model.geom_group[:]=5
 for n in include:
  gid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,n)
  if gid>=0:
   model.geom_group[gid]=1
   if shifts and n in shifts:model.geom_pos[gid]+=np.array(shifts[n])/1000
 if file=='08_enclosure.png':
  for name in ['BUY_TUBE','BUY_FRONT_FLANGE','BUY_REAR_CAP']:
   gid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,name);model.geom_rgba[gid]=[.63,.74,.78,1]
 data.qpos[:3]=0;mujoco.mj_forward(model,data)
 opt=mujoco.MjvOption();opt.geomgroup[:]=[0,1,0,0,0,0];opt.sitegroup[:]=0
 cam=mujoco.MjvCamera();cam.lookat[:]=lookat;cam.distance=distance;cam.elevation=elevation;cam.azimuth=azimuth
 renderer.update_scene(data,cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SKYBOX]=1
 renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=0
 renderer.render() # create current scene before replacing background
 image=renderer.render().copy();im=Image.fromarray(image)
 if file=='05_printed_parts.png':
  draw=ImageDraw.Draw(im);ft=ImageFont.truetype(font,28)
  cc=renderer.scene.camera;cp=(cc[0].pos+cc[1].pos)/2;fw=cc[0].forward;up=cc[0].up;right=np.cross(fw,up);near=cc[0].frustum_near;hh=(cc[0].frustum_top-cc[0].frustum_bottom)/2
  points=[(1,(70,0,-15),(55,0)),(2,(45,0,175),(55,-35)),(3,(0,152,-129),(35,35)),(4,(50,0,105),(40,0)),(5,(-40,-122,-62),(-45,10)),(6,(95,0,52),(35,35)),(7,(178,0,92),(40,-25))]
  for number,pt,offset in points:
   v=np.array(pt)/1000-cp;z=np.dot(v,fw);xx=(np.dot(v,right)*near/z)/(hh*1200/900);yy=(np.dot(v,up)*near/z-(cc[0].frustum_top+cc[0].frustum_bottom)/2)/hh
   anchor=(int((xx+1)*600),int((1-yy)*450));target=(anchor[0]+offset[0],anchor[1]+offset[1]);draw.line([anchor,target],fill='#355663',width=3);draw.ellipse((target[0]-20,target[1]-20,target[0]+20,target[1]+20),fill='#f29432',outline='white',width=2);draw.text(target,str(number),font=ft,anchor='mm',fill='#102c33')
 if file.startswith(('04_','05_','06_','07_','08_')):
  arr=np.asarray(im);mask=np.min(arr,axis=2)<220;ys,xs=np.where(mask);im=im.crop((max(0,int(xs.min())-28),max(0,int(ys.min())-28),min(im.width,int(xs.max())+29),min(im.height,int(ys.max())+29)))
 im.save(O/file)
render('04_assembly.png',[p['name'] for p in P if p['kind']!='HARDWARE' and not p.get('optional_buoyancy')],lookat=(0,0,.005),distance=.54,azimuth=45)
prints=[p['name'] for p in P if p['kind']=='PRINT'];shifts={}
for n in prints:
 if 'UPPER' in n:shifts[n]=[0,0,125]
 elif 'SKID' in n:shifts[n]=[0,55 if n.endswith('_97') else -55,-45]
 elif 'POD_CLAMP' in n:shifts[n]=[0,0,55]
 elif 'VERTICAL' in n:shifts[n]=[-5,60 if n.endswith('_62') else -60,-20]
 elif 'MODULE' in n:shifts[n]=[100,0,45]
 elif 'CAMERA_CARRIER' in n:shifts[n]=[130,0,70]
render('05_printed_parts.png',prints,shifts,lookat=(.025,0,.04),distance=.9,elevation=-18)
include=[n for n in names if n.startswith(('V5_01','V5_03','V5_05','REF_X2'))]
render('06_frame_thrusters.png',include,lookat=(0,0,-.025),distance=.58,azimuth=45,elevation=-17)
include=['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER','BUY_CAMERA_HD_USB']
render('07_camera_tray.png',include,lookat=(.01,0,.019),distance=.30,azimuth=35,elevation=-12)
include=['BUY_TUBE','BUY_FRONT_FLANGE','BUY_FRONT_WINDOW','BUY_REAR_CAP','V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER','BUY_CAMERA_HD_USB']
shifts={'BUY_FRONT_FLANGE':[45,0,0],'BUY_FRONT_WINDOW':[80,0,0],'BUY_REAR_CAP':[-45,0,0],'V5_06_MODULE_TRAY':[0,-80,-25],'V5_07_CAMERA_CARRIER':[0,-80,-25],'BUY_CAMERA_HD_USB':[0,-80,-25]}
render('08_enclosure.png',include,shifts,lookat=(.01,-.015,.015),distance=.58,azimuth=45,elevation=-20)
renderer.close();print('FIGURES',len(list(O.glob('*.png'))))

# Enclosure relationship schematic; not a seal cross-section.
f,ax=plt.subplots(figsize=(12,5));ax.axis('off');ax.set_xlim(-175,210);ax.set_ylim(-115,100)
box(ax,-75,-29,150,58,'150 mm tube',color='#c7e0e8');box(ax,-137,-32,25,64,'',color='#7d969e');box(ax,109,-32,25,64,'',color='#7d969e');box(ax,171,-29,7,58,'',color='#c7e0e8')
for x,tx,label in [(-124,-125,'Rear cap / ports'),(120,112,'Front flange'),(175,177,'Clear window')]:
 ax.annotate(label,xy=(x,32),xytext=(tx,68),ha='center',color=INK,fontsize=11,arrowprops=dict(arrowstyle='->',color=TEAL))
box(ax,-50,-83,100,5,'',color=TEAL);box(ax,43,-78,5,30,'',color=TEAL);box(ax,49,-74,15,22,'',color='#a3c3c9');arrow(ax,(0,-72),(0,-32));ax.text(-110,-93,'Tray + camera module',color=INK,ha='center',fontsize=11);ax.text(55,-108,'Assemble outside; final retention and wiring remain pending',color=INK,ha='center',fontsize=9)
finish(f,'08_enclosure.png','Pressure-enclosure relationships | Seals and locking parts omitted')
import runpy
runpy.run_path(str(Path(__file__).with_name('render_gallery.py')),run_name='__main__')
