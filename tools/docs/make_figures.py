from pathlib import Path
import math,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager,patches
import mujoco
from PIL import Image,ImageDraw,ImageFont
R=Path(__file__).resolve().parents[2]; O=R/'docs/assets/images/assembly_guide';O.mkdir(exist_ok=True)
import os
font=os.environ.get('SROV_CJK_FONT','/System/Library/Fonts/STHeiti Light.ttc');font_manager.fontManager.addfont(font);plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'axes.unicode_minus':False,'font.size':13})
COL={'frame':'#174b56','upper':'#ed8a24','mount':'#388a91','foam':'#d8dfcf','motor':'#718087'}
def clean(ax,xlim,ylim):ax.set_xlim(*xlim);ax.set_ylim(*ylim);ax.set_aspect('equal');ax.axis('off')
def label(ax,s,x,y,sz=13,**kw):ax.text(x,y,s,fontsize=sz,color='#173a43',ha='center',va='center',**kw)
def rect(ax,xy,w,h,c,alpha=1):ax.add_patch(patches.FancyBboxPatch(xy,w,h,boxstyle=f'round,pad=0.01,rounding_size={min(3,w/4,h/4)}',facecolor=c,edgecolor='#53676d',lw=1.2,alpha=alpha))
# Actual XY layout.
f,ax=plt.subplots(figsize=(11,8));clean(ax,(-170,170),(-140,150));rect(ax,(-105,-105),210,210,'#edf3f3');rect(ax,(-75,-29),150,58,'#a8d6df',.7)
for y in [-74,74]:rect(ax,(-108,y-28.19),60,56.38,COL['motor']);ax.annotate('',xy=(-43,y),xytext=(-99,y),arrowprops=dict(arrowstyle='->',lw=2.7,color='white'))
for y in [-62,62]:ax.add_patch(patches.Circle((0,y),28.19,fc=COL['mount'],ec='white',lw=2));label(ax,'V',0,y,20,color='white') if False else ax.text(0,y,'V',ha='center',va='center',color='white',fontsize=22)
ax.add_patch(patches.Circle((72,0),9,fc='#173a43'));ax.annotate('',xy=(133,0),xytext=(90,0),arrowprops=dict(arrowstyle='->',lw=2,color='#ed8a24'));label(ax,'前 / X+',130,15)
label(ax,'H_LEFT',-78,74,10);label(ax,'H_RIGHT',-78,-74,10)
label(ax,'中央密封舱',-8,0,13)
label(ax,'左侧 / Y+',0,124);label(ax,'右侧 / Y-',0,-124)
ax.annotate('后部穿舱端盖',xy=(-78,-12),xytext=(-157,-35),fontsize=12,color='#173a43',arrowprops=dict(arrowstyle='->'))
ax.annotate('竖推：轴线垂直纸面',xy=(16,67),xytext=(46,98),fontsize=12,color='#173a43',arrowprops=dict(arrowstyle='->'))
ax.annotate('水平推进器：轴向前后',xy=(-82,-78),xytext=(-148,-109),fontsize=12,color='#173a43',arrowprops=dict(arrowstyle='->'))
f.suptitle('V5 顶视定位图（隐藏上罩、浮材；位置来自 CAD）',fontsize=17,color='#173a43');f.savefig(O/'01_顶视定位.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(f)
# Motor screw stack, schematic with actual nominal lengths.
f,axs=plt.subplots(1,2,figsize=(12,5))
for ax in axs:clean(ax,(-6,24),(-4,24))
ax=axs[0];rect(ax,(0,11),18,9,'#cad9dc');rect(ax,(0,6.5),18,4.5,COL['frame']);rect(ax,(4,6),10,.5,'#9aa5aa');rect(ax,(7.6,6),2.8,8,'#c7cdd0');rect(ax,(5.8,3),6.4,3,'#87969b');label(ax,'推进器原厂底脚',9,18);label(ax,'底架夹持区',9,9,11);label(ax,'M3×8 从下向上',9,0,12)
ax.annotate('',xy=(21,11),xytext=(21,6),arrowprops=dict(arrowstyle='<->',color='#173a43'));ax.text(22,8.5,'5 mm\n含垫片',fontsize=10,va='center');ax.annotate('',xy=(-2,14),xytext=(-2,11),arrowprops=dict(arrowstyle='<->',color='#173a43'));ax.text(-3,12.5,'3 mm\n目标啮合',ha='right',va='center',fontsize=10);ax.set_title('水平安装：每台 4 颗螺钉',fontsize=15)
ax=axs[1];rect(ax,(10,4),10,15,'#cad9dc');rect(ax,(2,4),8,15,COL['mount']);rect(ax,(1.5,8),.5,7,'#9aa5aa');rect(ax,(1.5,10),12,2.8,'#c7cdd0');rect(ax,(-1.5,8.2),3,6.4,'#87969b');label(ax,'支架 8 mm',6,17,10);label(ax,'原厂底脚',15,17,10);label(ax,'M3×12 从侧面进入',9,0,12);ax.annotate('',xy=(13.5,21),xytext=(10,21),arrowprops=dict(arrowstyle='<->',color='#173a43'));ax.text(12,22,'3.5 mm 目标啮合',ha='center',fontsize=10);ax.set_title('竖直安装：每台 4 颗螺钉',fontsize=15)
f.text(.5,.01,'连接层次示意，未画真实底脚内部。M3孔型/孔深与底脚偏距须用实物确认，不能按示意拧到底。',ha='center',fontsize=11,color='#a14b22');f.savefig(O/'02_电机螺钉层次.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(f)
# Wet/dry boundary schematic.
f,ax=plt.subplots(figsize=(12,6));clean(ax,(0,120),(0,60));rect(ax,(39,5),78,48,'#e6f1f5');label(ax,'中央密封舱：内部保持干燥',78,49,16)
for x,y,w,h,c,t in [(3,31,25,14,'#98b9bd','舱外推进器\n共4台'),(43,29,13,17,'#edc990','密封\n穿舱件'),(62,31,21,14,'#9abdc5','双向电调\n每电机1路'),(91,31,21,14,'#8eb4b9','MCU / 控制板'),(62,11,21,12,'#e5c7a0','供电与保护\n型号待定'),(91,11,21,12,'#cad4c3','相机 / 传感器\n与主机接口')]:rect(ax,(x,y),w,h,c);label(ax,t,x+w/2,y+h/2,12)
for a,b in [((28,38),(43,38)),((56,38),(62,38)),((91,38),(83,38)),((73,23),(73,31))]:ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color='#173a43',lw=1.8))
label(ax,'电机三相线',34,26,10);label(ax,'控制信号',87,27,10);label(ax,'托板 + 按板卡适配的绝缘隔柱 / 安装板',80,7,10)
label(ax,'机架与上罩可进水',17,15,13);label(ax,'边界与连接关系示意；不是已冻结的电气接线图',60,57,13)
f.savefig(O/'03_干湿边界.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(f)
# CAD-based 3D renders. Move actual visual meshes, do not invent hardware.
model=mujoco.MjModel.from_xml_path(str(R/'simulation/mujoco/manta_v5.xml'));data=mujoco.MjData(model);renderer=mujoco.Renderer(model,height=900,width=1200)
base_rgba=model.geom_rgba.copy();base_pos=model.geom_pos.copy();base_group=model.geom_group.copy()
P=json.loads((R/'mechanical/parts.json').read_text());names=[p['name'] for p in P if p['kind']!='HARDWARE']
def render(file,include,shifts=None,lookat=(0,0,0),distance=.62,elevation=-24,azimuth=135):
 model.geom_rgba[:]=base_rgba;model.geom_pos[:]=base_pos;model.geom_group[:]=5
 for n in include:
  gid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,n)
  if gid>=0:
   model.geom_group[gid]=1
   if shifts and n in shifts:model.geom_pos[gid]+=np.array(shifts[n])/1000
 if file=='08_密封舱分解.png':
  for name in ['BUY_TUBE','BUY_FRONT_FLANGE','BUY_REAR_CAP']:
   gid=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,name);model.geom_rgba[gid]=[.63,.74,.78,1]
 data.qpos[:3]=0;mujoco.mj_forward(model,data)
 opt=mujoco.MjvOption();opt.geomgroup[:]=[0,1,0,0,0,0];opt.sitegroup[:]=0
 cam=mujoco.MjvCamera();cam.lookat[:]=lookat;cam.distance=distance;cam.elevation=elevation;cam.azimuth=azimuth
 renderer.update_scene(data,cam,scene_option=opt);renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SKYBOX]=0
 renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=0
 renderer.render() # create current scene before replacing background
 image=renderer.render().copy();im=Image.fromarray(image)
 if file=='05_打印件分解.png':
  draw=ImageDraw.Draw(im);ft=ImageFont.truetype(font,28)
  cc=renderer.scene.camera;cp=(cc[0].pos+cc[1].pos)/2;fw=cc[0].forward;up=cc[0].up;right=np.cross(fw,up);near=cc[0].frustum_near;hh=(cc[0].frustum_top-cc[0].frustum_bottom)/2
  points=[(1,(70,0,-15),(55,0)),(2,(45,0,175),(55,-35)),(3,(0,152,-129),(35,35)),(4,(50,0,105),(40,0)),(5,(-40,-122,-62),(-45,10)),(6,(95,0,52),(35,35)),(7,(178,0,92),(40,-25))]
  for number,pt,offset in points:
   v=np.array(pt)/1000-cp;z=np.dot(v,fw);xx=(np.dot(v,right)*near/z)/(hh*1200/900);yy=(np.dot(v,up)*near/z-(cc[0].frustum_top+cc[0].frustum_bottom)/2)/hh
   anchor=(int((xx+1)*600),int((1-yy)*450));target=(anchor[0]+offset[0],anchor[1]+offset[1]);draw.line([anchor,target],fill='white',width=3);draw.ellipse((target[0]-20,target[1]-20,target[0]+20,target[1]+20),fill='#f29432',outline='white',width=2);draw.text(target,str(number),font=ft,anchor='mm',fill='#102c33')
 if file.startswith(('04_','05_','06_','07_','08_')):
  arr=np.asarray(im);mask=np.max(arr,axis=2)>25;ys,xs=np.where(mask);im=im.crop((max(0,int(xs.min())-28),max(0,int(ys.min())-28),min(im.width,int(xs.max())+29),min(im.height,int(ys.max())+29)))
 im.save(O/file)
render('04_完整总装.png',names,lookat=(0,0,.005),distance=.54,azimuth=45)
prints=[p['name'] for p in P if p['kind']=='PRINT'];shifts={}
for n in prints:
 if 'UPPER' in n:shifts[n]=[0,0,125]
 elif 'SKID' in n:shifts[n]=[0,55 if n.endswith('_97') else -55,-45]
 elif 'POD_CLAMP' in n:shifts[n]=[0,0,55]
 elif 'VERTICAL' in n:shifts[n]=[-5,60 if n.endswith('_62') else -60,-20]
 elif 'MODULE' in n:shifts[n]=[100,0,45]
 elif 'CAMERA_CARRIER' in n:shifts[n]=[130,0,70]
render('05_打印件分解.png',prints,shifts,lookat=(.025,0,.04),distance=.9,elevation=-18)
include=[n for n in names if n.startswith(('V5_01','V5_03','V5_05','REF_X2'))]
render('06_底架推进器.png',include,lookat=(0,0,-.025),distance=.58,azimuth=45,elevation=-17)
include=['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER','BUY_CAMERA_HD_USB']
render('07_相机托板.png',include,lookat=(.01,0,.019),distance=.30,azimuth=35,elevation=-12)
include=['BUY_TUBE','BUY_FRONT_FLANGE','BUY_FRONT_WINDOW','BUY_REAR_CAP','V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER','BUY_CAMERA_HD_USB']
shifts={'BUY_FRONT_FLANGE':[45,0,0],'BUY_FRONT_WINDOW':[80,0,0],'BUY_REAR_CAP':[-45,0,0],'V5_06_MODULE_TRAY':[0,-80,-25],'V5_07_CAMERA_CARRIER':[0,-80,-25],'BUY_CAMERA_HD_USB':[0,-80,-25]}
render('08_密封舱分解.png',include,shifts,lookat=(.01,-.015,.015),distance=.58,azimuth=45,elevation=-20)
renderer.close();print('FIGURES',len(list(O.glob('*.png'))))
# High-contrast pressure-pod relationship drawing for printed instructions.
f,ax=plt.subplots(figsize=(12,5));clean(ax,(-160,195),(-110,95))
rect(ax,(-75,-29),150,58,'#c7e0e8');rect(ax,(-129,-32),21.5,64,'#7d969e');rect(ax,(104.5,-32),21.5,64,'#7d969e');rect(ax,(161,-29),6.35,58,'#b9e2e9')
for x,tx,t in [(-118,-130,'后盖 / 穿舱口'),(0,0,'150 mm 管体'),(115,105,'前法兰'),(164,175,'透明端盖')]:
 ax.annotate(t,xy=(x,32),xytext=(tx,68),ha='center',fontsize=13,color='#173a43',arrowprops=dict(arrowstyle='->',color='#537079'))
rect(ax,(-50,-84),100,5,COL['mount']);rect(ax,(43,-79),5,30,COL['mount']);rect(ax,(49,-75),15,22,'#8cafad');ax.annotate('内部托板 + 相机模块',xy=(0,-80),xytext=(-90,-101),fontsize=13,ha='center',color='#173a43',arrowprops=dict(arrowstyle='->'))
ax.annotate('',xy=(0,-31),xytext=(0,-70),arrowprops=dict(arrowstyle='->',lw=2,color='#ed8a24'));label(ax,'在舱外装好后放入；最终锁止与电气布局待补',80,-99,10)
f.suptitle('密封舱结构关系示意（非密封槽截面或加工图）',fontsize=17,color='#173a43');f.savefig(O/'08_密封舱分解.png',dpi=180,bbox_inches='tight',facecolor='white');plt.close(f)
