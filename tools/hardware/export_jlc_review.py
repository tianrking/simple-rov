"""Convert frozen native exports to JLC review column names, without stock claims.

Does not approve order rotations, select LCSC inventory or place a manufacturing order.
"""
from pathlib import Path
import csv
import hashlib
import json
import zipfile
R=Path(__file__).resolve().parents[2]
P=R/'electronics/pcb/controller'
M=P/'manufacturing'
O=M/'jlc_review'
O.mkdir(parents=True,exist_ok=True)
def read(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(path,fields,rows):
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');w.writeheader();w.writerows(rows)
bom=read(M/'BOM_grouped.csv')
write(O/'BOM_JLC_review.csv',['Comment','Designator','Footprint','LCSC Part #','Manufacturer Part Number'],[{'Comment':p['Value'],'Designator':p['References'],'Footprint':p['Footprint'],'LCSC Part #':'','Manufacturer Part Number':p['MPN']} for p in bom])
positions=read(M/'CPL_top.csv')
write(O/'CPL_JLC_review.csv',['Designator','Mid X','Mid Y','Layer','Rotation'],[{'Designator':p['Ref'],'Mid X':p['PosX']+'mm','Mid Y':p['PosY']+'mm','Layer':p['Side'],'Rotation':p['Rot']} for p in positions])
assert not any(p['Ref']=='J11' for p in positions),'Mixed SMT/PTH USB must follow separate assembly instruction'
inputs=sorted((M/'gerbers').glob('*'))+sorted((M/'drill_separate').glob('*.drl'))
with zipfile.ZipFile(O/'Gerber_drill_review.zip','w',zipfile.ZIP_DEFLATED) as z:
    for p in inputs:
        zi=zipfile.ZipInfo(p.name,date_time=(2026,1,1,0,0,0));zi.compress_type=zipfile.ZIP_DEFLATED;z.writestr(zi,p.read_bytes())
source=inputs+[M/'BOM_grouped.csv',M/'CPL_top.csv',R/'tools/hardware/export_jlc_review.py']
report={'format_conversion_only':True,'assembly_order_approved':False,'LCSC_stock_selected':False,'placement_origin':'KiCad absolute; X right, Y up; negative Y retained, no new rotation offsets applied','manual_placement':['J11 mixed-technology Micro-B USB'],'source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source},'outputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(O.glob('*')) if p.is_file() and p.suffix in ('.csv','.zip')}}
(R/'electronics/validation/jlc_review_export.json').write_text(json.dumps(report,indent=2)+'\n')
print('Exported JLC column-format review files; stock, rotations and order remain unapproved')
