"""Check the declared controller mounting stack against unchanged supplier/print CAD.

Requires requirements/cad.txt. Nominal CAD checks are not physical qualification.
"""
from pathlib import Path
import hashlib
import json
import math
import cadquery as cq

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = 'electronics/interfaces/MECHANICAL_CONTRACT.json'
BASE_NAMES = ['mechanical/step_parts/'+n+'.step' for n in ['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER']]
BASE_NAMES += ['mechanical/supplier/'+n for n in ['BR-106277-150_RevB.STEP','BR-102922-009_RevC.step','BR-102922-998_RevB.step','LOW-LIGHT-HD-USB-CAMERA-R1.STEP']]

def import_all(path):
    return cq.Compound.makeCompound(cq.importers.importStep(str(path)).solids().vals())

def block(dx, dy, dz, px, py, pz):
    return cq.Workplane('XY').box(dx,dy,dz,centered=(False,False,False)).translate((px,py,pz)).val()

def ring(ro, ri, height, px, py, pz):
    return cq.Workplane('XY').center(px,py).circle(ro).circle(ri).extrude(height).translate((0,0,pz)).val()

def baseline():
    parts={n:import_all(ROOT/'mechanical/step_parts'/f'{n}.step') for n in ['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER']}
    s=ROOT/'mechanical/supplier'
    parts['tube']=import_all(s/'BR-106277-150_RevB.STEP').translate((75,0,22))
    parts['rear_cap']=import_all(s/'BR-102922-009_RevC.step').rotate((0,0,0),(0,1,0),-90).translate((-59.5,0,22)).rotate((0,0,22),(1,0,22),270)
    parts['front_flange']=import_all(s/'BR-102922-998_RevB.step').rotate((0,0,0),(0,1,0),90).translate((59.5,0,22)).rotate((0,0,22),(1,0,22),270)
    parts['camera']=import_all(s/'LOW-LIGHT-HD-USB-CAMERA-R1.STEP').rotate((0,0,0),(0,0,1),-90).translate((54,16,38)).rotate((0,0,22),(1,0,22),180)
    return parts

def mounting(k):
    b=k['board'];x,y,z=k['coordinates']['board_local_origin_global_mm'];t=b['thickness_mm']
    top=k['host_tray']['top_plane_Z_mm'];bottom=k['host_tray']['bottom_plane_Z_mm']
    holes=[[x+hx,y+hy] for hx,hy in b['mount_holes_local_xy_mm']]
    hardware={}
    for i,(hx,hy) in enumerate(holes,1):
        hardware[f'Insulating_spacer_{i}']=ring(3,1.6,b['spacer_height_mm'],hx,hy,top)
        hardware[f'Top_washer_{i}']=ring(3.5,1.6,.5,hx,hy,z+t)
        hardware[f'Bottom_washer_{i}']=ring(3.5,1.6,.5,hx,hy,bottom-.5)
        hardware[f'M3_nut_{i}']=cq.Workplane('XY').center(hx,hy).polygon(6,5.5/math.cos(math.pi/6)).extrude(2.4).faces('>Z').workplane().hole(3.2).translate((0,0,bottom-.5-2.4)).val()
        seat=z+t+.5;length=b['screw_length_mm']
        shaft=cq.Workplane('XY').center(hx,hy).circle(1.5).extrude(length).translate((0,0,seat-length))
        head=cq.Workplane('XY').center(hx,hy).circle(2.75).extrude(3).translate((0,0,seat))
        hardware[f'M3x{length}_{i}']=shaft.union(head).val()
    return hardware

def main():
    k=json.loads((ROOT/CONTRACT).read_text());b=k['board'];x,y,z=k['coordinates']['board_local_origin_global_mm'];L,W,T=b['length_mm'],b['width_mm'],b['thickness_mm']
    pcb=block(L,W,T,x,y,z);upper=block(L,W,b['provisional_top_component_height_mm'],x,y,z+T);lower=block(L,W,b['provisional_bottom_protrusion_mm'],x,y,z-b['provisional_bottom_protrusion_mm'])
    holes=[[x+hx,y+hy] for hx,hy in b['mount_holes_local_xy_mm']]
    for hx,hy in holes:pcb=pcb.cut(cq.Workplane('XY').center(hx,hy).circle(b['mount_hole_diameter_mm']/2).extrude(T+2).translate((0,0,z-1)).val())
    parts=baseline();hardware=mounting(k);collisions=[];measurements=[]
    for hx,hy in holes:
        samples=[]
        for dy in [-2.5,2.5]:
            rod=cq.Workplane('XY').center(hx,hy+dy).circle(.2).extrude(30).val()
            sample=parts['V5_06_MODULE_TRAY'].intersect(rod);bb=sample.BoundingBox();assert sample.Volume()>.1
            samples.append([bb.zmin,bb.zmax]);assert abs(bb.zmax-k['host_tray']['top_plane_Z_mm'])<1e-6;assert abs(bb.zmin-k['host_tray']['bottom_plane_Z_mm'])<1e-6
        measurements.append({'slot_xy_mm':[hx,hy],'support_samples_zmin_zmax_mm':samples})
    assert abs(z-k['host_tray']['top_plane_Z_mm']-b['spacer_height_mm'])<1e-6
    for name,solid in parts.items():
        for ename,envelope in [('board',pcb),('declared_top',upper),('declared_bottom',lower)]+list(hardware.items()):
            v=solid.intersect(envelope).Volume()
            if v>.01:collisions.append({'part':name,'envelope':ename,'overlap_mm3':v})
    assert not collisions,collisions
    assert sorted(holes)==sorted(k['host_tray']['slot_centres_global_XY_mm'])
    assert b['mount_hole_diameter_mm']<k['host_tray']['slot_size_mm'][1]
    hardware_tube_clearance={n:solid.distance(parts['tube']) for n,solid in hardware.items() if n.startswith(('M3x','M3_nut'))}
    seat=z+T+.5;tip=seat-b['screw_length_mm'];nutbottom=k['host_tray']['bottom_plane_Z_mm']-.5-2.4
    protrusion=nutbottom-tip;assert protrusion>=.5
    ass=cq.Assembly(name='Controller_mount_review')
    for name in ['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER']:ass.add(parts[name],name=name,color=cq.Color(.15,.4,.43))
    ass.add(pcb,name='Declared_PCB_outline_not_component_CAD',color=cq.Color(.1,.55,.35));ass.add(upper,name='Declared_top_envelope_not_component_CAD',color=cq.Color(.4,.65,.85,.25))
    for name,solid in hardware.items():ass.add(solid,name=name,color=cq.Color(.65,.67,.7))
    target=ROOT/'electronics/mechanical/controller-mount-review.step';target.parent.mkdir(parents=True,exist_ok=True);ass.save(str(target))
    names=[CONTRACT,'mechanical/INTERFACES.json','mechanical/parts.json','tools/hardware/check_controller_mount.py']+BASE_NAMES
    report={'contract_id':k['contract_id'],'project_version':'v0.0.1','declared_board_bounds_global_mm':[x,x+L,y,y+W,z,z+T],'mount_centres_global_XY_mm':holes,'spacer_height_mm':b['spacer_height_mm'],'tray_support_step_samples':measurements,'screw_length_mm':b['screw_length_mm'],'nominal_nut_engagement_mm':2.4,'mount_hardware_to_tube_minimum_distance_mm':hardware_tube_clearance,'nominal_screw_tip_protrusion_beyond_nut_mm':protrusion,'declared_envelope_interferences':collisions,'mount_centres_match_tray_slots':True,'added_hardware':{'M3x14_screw':4,'M3_washer':8,'M3_nut':4,'insulating_spacer_5mm':4},'base_metal_count':134,'with_controller_mount_metal_count':150,'full_vehicle_electrical_packaging_verified':False,'actual_component_and_mating_cable_fit_verified':False,'physical_fit_tested':False,'passed':True,'scope':'Nominal declared outline/height and actual tray support/fastener stack against supplied CAD. No thread/chamfer/tolerance, actual cable, battery/ESC/Pi/hub/thermal or full-vehicle fit qualification.','source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in names},'output_sha256':{str(target.relative_to(ROOT)):hashlib.sha256(target.read_bytes()).hexdigest()}}
    (ROOT/'electronics/validation/controller_mount.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({key:report[key] for key in ['passed','spacer_height_mm','screw_length_mm','nominal_screw_tip_protrusion_beyond_nut_mm','declared_envelope_interferences']},indent=2))

if __name__=='__main__':main()
