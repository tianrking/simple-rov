"""Nominal native controller STEP, GH reservations and mounting-stack fit check.

Requires requirements/cad.txt. Does not qualify real cables, tolerances, sealing,
thermal performance or complete electrical payload packaging.
"""
from pathlib import Path
import argparse
import hashlib
import json
import cadquery as cq
from check_controller_mount import ROOT, CONTRACT, BASE_NAMES, import_all, baseline, mounting, block

p=argparse.ArgumentParser();p.add_argument('--hardware-dir',type=Path,default=ROOT/'electronics/pcb');a=p.parse_args()
k=json.loads((ROOT/CONTRACT).read_text());meta=json.loads((a.hardware_dir/'mechanical/MECHANICAL_EXPORT.json').read_text());translation=tuple(k['coordinates']['board_local_origin_global_mm']);assert list(translation)==meta['world_translation_mm']
models={}
for name in ['controller_assembled','mated_connector_keepouts','wire_bend_reservations']:
    models[name]=import_all(a.hardware_dir/'mechanical'/f'{name}.step').translate(translation)
parts=baseline();hardware=mounting(k);collisions=[];checks=[]
for name,model in models.items():
    for other,solid in parts.items():
        volume=model.intersect(solid).Volume();distance=model.distance(solid)
        checks.append({'model':name,'other':other,'minimum_distance_mm':distance,'overlap_mm3':volume})
        if volume>.01:collisions.append(checks[-1])
    for other,solid in hardware.items():
        volume=model.intersect(solid).Volume()
        if volume>.01:collisions.append({'model':name,'other':other,'overlap_mm3':volume})
# Individual GH reservation boxes come from the final native connector placement.
# Mated boxes intentionally encompass their own installed headers. Compare them
# with other reservations and the mechanical hardware, not the header itself.
envelopes=[]
for e in meta['envelopes']:
    x0,y0,z0,x1,y1,z1=e['step_bbox_mm']
    envelopes.append((e,block(x1-x0,y1-y0,z1-z0,x0+translation[0],y0+translation[1],z0+translation[2])))
reservation_overlaps=[]
for i,(e,solid) in enumerate(envelopes):
    for f,other in envelopes[i+1:]:
        if e['connector']==f['connector']:continue
        volume=solid.intersect(other).Volume()
        if volume>.01:reservation_overlaps.append({'connector_a':e['connector'],'kind_a':e['kind'],'connector_b':f['connector'],'kind_b':f['kind'],'overlap_mm3':volume})
assert len(envelopes)==18
assert len(models['controller_assembled'].Solids())==meta['board_solid_count']
assert not collisions,collisions
assert not reservation_overlaps,reservation_overlaps
# All purchased parts are top side; the conservative USB underside envelope
# clears the actual tray top at the selected five-millimetre spacer height.
bbox=models['controller_assembled'].BoundingBox()
underside_min=bbox.zmin-k['host_tray']['top_plane_Z_mm']
ass=cq.Assembly(name='Native_controller_fit_review')
for name in ['V5_06_MODULE_TRAY','V5_07_CAMERA_CARRIER']:ass.add(parts[name],name=name,color=cq.Color(.15,.4,.43))
ass.add(models['controller_assembled'],name='Native_controller_with_standard_and_declared_envelope_models',color=cq.Color(.15,.55,.28))
ass.add(models['mated_connector_keepouts'],name='GH_mating_engineering_reservations',color=cq.Color(.3,.6,.9,.25))
ass.add(models['wire_bend_reservations'],name='Wire_bend_engineering_reservations',color=cq.Color(.9,.7,.2,.25))
for name,solid in hardware.items():ass.add(solid,name=name,color=cq.Color(.65,.67,.7))
out=ROOT/'electronics/mechanical/native-controller-fit.step';out.parent.mkdir(parents=True,exist_ok=True);ass.save(str(out))
sources={n:ROOT/n for n in [CONTRACT,'tools/hardware/check_native_fit.py','tools/hardware/check_controller_mount.py']+BASE_NAMES}
for n in ['MECHANICAL_EXPORT.json','controller_assembled.step','mated_connector_keepouts.step','wire_bend_reservations.step']:
    sources['electronics/pcb/mechanical/'+n]=a.hardware_dir/'mechanical'/n
report={'project_version':'v0.0.1','passed':True,'scope':'Nominal native PCB/component STEP, GH mating/wire reservations and nominal M3 mounting hardware against unchanged tray, camera carrier, tube, rear cap, front flange and camera. All imported STEP solids are included.','native_controller_solid_count':len(models['controller_assembled'].Solids()),'models_include_explicit_dimension_envelopes':['ICM42688_max','USB105017_conservative'],'world_translation_mm':list(translation),'native_controller_global_bbox_mm':[bbox.xmin,bbox.ymin,bbox.zmin,bbox.xmax,bbox.ymax,bbox.zmax],'minimum_controller_underside_to_tray_top_plane_mm':underside_min,'boolean_interferences_over_0_01_mm3':collisions,'mechanical_distances':checks,'GH_reservation_rows':len(envelopes),'GH_reservation_pair_interferences':reservation_overlaps,'mount_stack':{'PCB_bottom_Z_mm':13,'tray_support_top_Z_mm':8,'tray_support_bottom_Z_mm':6,'insulating_spacer_height_mm':5,'M3_screw_length_mm':14,'washer_count':8,'nut_count':4,'screw_count':4,'nominal_nut_engagement_mm':2.4,'nominal_tip_protrusion_beyond_nut_mm':2},'not_established':['Real mating connector or wire bend geometry/tolerances','Lower GH mating reservations versus their own header/component bodies; these reservations intentionally include the headers','USB service plug access and insertion/removal sequence','Physical screw thread/chamfer engagement and print tolerances','Positive axial tray retention','Battery, four ESCs, Pi/hub, power junctions and complete harness packaging','Sealing, thermal, electrical and water operation'],'physical_fit_tested':False,'complete_vehicle_electrical_packaging_verified':False,'actual_component_and_mating_cable_fit_verified':False,'source_sha256':{n:hashlib.sha256(path.read_bytes()).hexdigest() for n,path in sources.items()},'output_sha256':{str(out.relative_to(ROOT)):hashlib.sha256(out.read_bytes()).hexdigest()}}
(ROOT/'electronics/validation/native_controller_fit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({key:report[key] for key in ['passed','native_controller_solid_count','native_controller_global_bbox_mm','minimum_controller_underside_to_tray_top_plane_mm','boolean_interferences_over_0_01_mm3','GH_reservation_pair_interferences']},indent=2))
