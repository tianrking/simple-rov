"""Render a CAD-backed studio gallery with consistent views and configuration labels."""
from pathlib import Path
import hashlib,json,os,xml.etree.ElementTree as E
import numpy as np
import mujoco
from PIL import Image,ImageDraw,ImageFont

R=Path(__file__).resolve().parents[2]
S=R/'simulation/mujoco';OUT=R/'docs/assets/gallery';OUT.mkdir(exist_ok=True)
font_path=os.environ.get('SROV_CJK_FONT','/System/Library/Fonts/STHeiti Light.ttc')
if not Path(font_path).is_file():font_path='/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc'
font=lambda size:ImageFont.truetype(font_path,size)
xml=E.parse(S/'simple_rov_with_buoyancy.xml').getroot()
xml.find('compiler').set('meshdir',str(S/'meshes'))
xml.find('visual/global').set('offwidth','2400');xml.find('visual/global').set('offheight','1800')
head=xml.find('visual/headlight');head.set('ambient','.65 .65 .65');head.set('diffuse','.65 .65 .65');head.set('specular','.12 .12 .12')
asset=xml.find('asset')
E.SubElement(asset,'texture',type='skybox',builtin='gradient',rgb1='.97 .98 .985',rgb2='.90 .94 .95',width='512',height='3072')
world=xml.find('worldbody')
for node in list(world):
    if node.tag in ('geom','light'):world.remove(node)
E.SubElement(world,'light',pos='.3 -.4 .6',dir='-.3 .4 -.6',diffuse='.6 .6 .6',specular='.1 .1 .1',directional='true',castshadow='true')
E.SubElement(world,'geom',name='studio_floor',type='plane',size='2 2 .01',pos='0 0 -.090',rgba='.95 .97 .98 1',group='0',contype='0',conaffinity='0')
world.find('body').set('pos','0 0 0')
model=mujoco.MjModel.from_xml_string(E.tostring(xml,encoding='unicode'));data=mujoco.MjData(model);mujoco.mj_forward(model,data)
renderer=mujoco.Renderer(model,height=1600,width=2400)
original_groups=model.geom_group.copy();original_rgba=model.geom_rgba.copy()
optional=[i for i in range(model.ngeom) if (mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_GEOM,i) or '').startswith(('BUY_TRIM_FOAM','BUY_FOAM_STRAP','proxy_foam'))]
configurations=json.loads((R/'mechanical/configurations.json').read_text());records=[]

def render(name,title,azimuth,elevation,with_buoyancy=False,interior=False,ortho=False,distance=.47,floor=True):
    model.geom_group[:]=original_groups;model.geom_rgba[:]=original_rgba
    if not with_buoyancy:
        for i in optional:model.geom_group[i]=5
    for i in optional:
        n=mujoco.mj_id2name(model,mujoco.mjtObj.mjOBJ_GEOM,i) or ''
        if n.startswith('BUY_TRIM_FOAM'):model.geom_rgba[i]=[.62,.72,.65,1]
    # Opaque display finish avoids sorting artifacts through overlapping clear OEM surfaces.
    # The dedicated interior view explicitly removes the tube and window instead.
    for n in ['BUY_TUBE','BUY_FRONT_WINDOW','BUY_FRONT_FLANGE','BUY_REAR_CAP']:
        i=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,n)
        if i>=0:model.geom_rgba[i]=[.32,.48,.54,1]
    if interior:
        for n in ['V5_02_UPPER_FAIRING','BUY_TUBE','BUY_FRONT_WINDOW','BUY_FRONT_FLANGE','BUY_REAR_CAP']:
            i=mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,n)
            if i>=0:model.geom_group[i]=5
    model.geom_group[mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_GEOM,'studio_floor')]=0 if floor else 5
    option=mujoco.MjvOption();option.geomgroup[:]=[1,1,0,0,0,0];option.sitegroup[:]=0
    camera=mujoco.MjvCamera();camera.lookat[:]=[0,0,.002 if not with_buoyancy else .018]
    model.vis.global_.fovy=.32 if ortho else 45
    camera.distance=distance;camera.azimuth=azimuth;camera.elevation=elevation;camera.orthographic=int(ortho)
    mujoco.mj_forward(model,data);renderer.update_scene(data,camera,scene_option=option)
    renderer.scene.flags[mujoco.mjtRndFlag.mjRND_SHADOW]=0
    frame=Image.fromarray(renderer.render().copy())
    # Page framing is part of this generated technical illustration, not a photograph.
    canvas=Image.new('RGB',(2400,1800),'#f5f8fa');canvas.paste(frame,(0,100));draw=ImageDraw.Draw(canvas)
    draw.text((76,28),'SimpleROV',font=font(42),fill='#173c47');draw.text((2324,38),title,font=font(32),anchor='ra',fill='#315e6c')
    config='选装浮力模块' if with_buoyancy else '标准装配 · 不含浮力模块'
    if interior:config+=' · 隐藏上罩与压力舱组件'
    draw.text((76,1736),config,font=font(28),fill='#3b6570');draw.text((2324,1736),'CAD 渲染 / 非实物照片',font=font(25),anchor='ra',fill='#687d84')
    canvas.save(OUT/name,optimize=True)
    records.append(dict(file=name,title=title,configuration='with-buoyancy' if with_buoyancy else 'base',azimuth_deg=azimuth,elevation_deg=elevation,orthographic=ortho,interior=interior,pixels=[2400,1800],sha256=hashlib.sha256((OUT/name).read_bytes()).hexdigest()))

render('hero.png','整体 / FRONT-LEFT',45,-24,distance=.44)
render('front.png','前视 / +X',0,0,ortho=True,floor=False,distance=.43)
render('rear.png','后视 / -X',180,0,ortho=True,floor=False,distance=.43)
render('left.png','左视 / +Y',90,0,ortho=True,floor=False,distance=.43)
render('right.png','右视 / -Y',270,0,ortho=True,floor=False,distance=.43)
render('top.png','俯视 / +Z',0,-90,ortho=True,floor=False,distance=.51)
render('bottom.png','底视 / -Z',0,90,ortho=True,floor=False,distance=.51)
render('interior.png','内部安装 / 相机与托板',35,-17,interior=True,distance=.44)
render('buoyancy-option.png','选装浮力模块',45,-24,with_buoyancy=True,distance=.52)
renderer.close()
# Six consistent orthographic directions, with readable view names.
views=[('front.png','前视'),('rear.png','后视'),('left.png','左视'),('right.png','右视'),('top.png','俯视'),('bottom.png','底视')]
contact=Image.new('RGB',(2400,1800),'#f5f8fa')
for i,(name,title) in enumerate(views):
    im=Image.open(OUT/name).crop((0,100,2400,1700));im.thumbnail((780,760));x=(i%3)*800+(800-im.width)//2;y=(i//3)*850+70
    contact.paste(im,(x,y));ImageDraw.Draw(contact).text((i%3*800+30,i//3*850+20),title,font=font(34),fill='#173c47')
ImageDraw.Draw(contact).text((60,1740),'标准装配 · 六向视图 · 坐标 X前 / Y左 / Z上',font=font(32),fill='#315e6c')
contact.save(OUT/'overview.png',optimize=True)
comparison=Image.new('RGB',(2400,1100),'#f5f8fa')
for i,name in enumerate(['hero.png','buoyancy-option.png']):
    im=Image.open(OUT/name);im.thumbnail((1180,1000));comparison.paste(im,(i*1200+(1200-im.width)//2,40))
comparison.save(OUT/'configuration-comparison.png',optimize=True)
# The assembly manual's lead image uses the same standard configuration.
Image.open(OUT/'hero.png').save(R/'docs/assets/images/assembly_guide/04_完整总装.png')
report={'source':'Current CAD assembly meshes through MuJoCo visual meshes','source_parts_sha256':hashlib.sha256((R/'mechanical/parts.json').read_bytes()).hexdigest(),'default_configuration':'base','base_dimensions_mm':configurations['base']['dimensions_mm'],'optional_dimensions_mm':configurations['with-buoyancy']['dimensions_mm'],'views':records,'notes':'Foam and straps are excluded in standard views. Renderings do not show unmodeled electronics/cables and are not physical test evidence.'}
(R/'validation/gallery.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Gallery:',len(records),'views + overview + configuration comparison')
