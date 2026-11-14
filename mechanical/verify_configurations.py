"""Read back both STEP variants and check default/optional geometry and purchase quantities."""
from pathlib import Path
import csv,hashlib,json
import cadquery as cq
R=Path(__file__).resolve().parents[1];M=R/'mechanical'
config=json.loads((M/'configurations.json').read_text());parts=json.loads((M/'parts.json').read_text())
optional={p['name'] for p in parts if p['optional_buoyancy']}
assert len(optional)==6
assert not optional.intersection(config['base']['included_parts'])
assert optional <= set(config['with-buoyancy']['included_parts'])
checks=[];sources=['mechanical/configurations.json','mechanical/parts.json','bom/BOM_PURCHASED.csv']
for key,count in [('base',24),('with-buoyancy',30)]:
 path=M/config[key]['step'];shape=cq.importers.importStep(str(path)).val();bb=shape.BoundingBox()
 actual=[bb.xlen,bb.ylen,bb.zlen];expected=config[key]['dimensions_mm']
 assert all(abs(a-b)<.001 for a,b in zip(actual,expected)),(key,actual,expected)
 assert len(shape.Solids())==count,(key,len(shape.Solids()))
 checks.append(dict(configuration=key,dimensions_mm=actual,solids=count,passed=True))
 sources.append(str(path.relative_to(R)))
with (R/'bom/BOM_PURCHASED.csv').open(encoding='utf-8-sig') as f:rows=list(csv.DictReader(f))
extras=[r for r in rows if r['configuration']=='optional buoyancy']
assert len(extras)==2 and sorted(int(r['optional_quantity']) for r in extras)==[2,4]
assert all(int(r['quantity'])==0 for r in extras)
report=dict(default='base',step_readback=checks,optional_parts=sorted(optional),optional_purchase_rows=extras,
 source_sha256={n:hashlib.sha256((R/n).read_bytes()).hexdigest() for n in sources},physical_tested=False,passed=True)
(R/'validation/configurations.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(checks,indent=2))
