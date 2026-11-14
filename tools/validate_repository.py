"""Repository/path/provenance checks. Does not validate physical hardware."""
from pathlib import Path
import argparse,ast,csv,hashlib,json,re,xml.etree.ElementTree as ET
from urllib.parse import unquote,urlparse
from html.parser import HTMLParser
from project_files import ROOT,project_files
p=argparse.ArgumentParser();p.add_argument('--manifest',action='store_true');args=p.parse_args()
files=list(project_files());errors=[]
def require(condition,msg):
    if not condition:errors.append(msg)
def check_link(source,url):
    if not url or url.startswith(('#','http:','https:','mailto:','data:','javascript:')):return
    clean=unquote(url.split('#')[0].split('?')[0]);dest=(source.parent/clean).resolve()
    require(dest.is_relative_to(ROOT) and dest.exists(),str(source.relative_to(ROOT))+': missing/outside link '+url)
class Links(HTMLParser):
    def __init__(self,path):super().__init__();self.path=path
    def handle_starttag(self,tag,attrs):
        for key,val in attrs:
            if key in ('src','href') and val:check_link(self.path,val)
secret_patterns=[r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{40,}']
for file in files:
    name=str(file.relative_to(ROOT))
    if file.suffix=='.py':ast.parse(file.read_text(),filename=name)
    if file.suffix in ('.py','.md','.json','.yml','.toml','.command','.txt','.html'):
        text=file.read_text()
        require(('/'+'Users/') not in text and ('/'+'home/') not in text,name+': absolute personal filesystem path')
        require(not any(re.search(pattern,text) for pattern in secret_patterns),name+': potential secret material')
        if file.suffix=='.md':
            for url in re.findall(r'\]\(([^)]+)\)',text):check_link(file,url)
        if file.suffix=='.html':Links(file).feed(text)
require(len(list((ROOT/'mechanical/stl').glob('*.stl')))==10,'Expected10 main STL')
require(len(list((ROOT/'mechanical/step_parts').glob('*.step')))==10,'Expected10 main STEP')
require(len(list((ROOT/'mechanical/fit_coupons').glob('*.stl')))==2,'Expected2 coupons')
parts=json.loads((ROOT/'mechanical/parts.json').read_text());require(sum(x['kind']=='PRINT' for x in parts)==10,'Printed part manifest')
with (ROOT/'bom/BOM_FASTENERS.csv').open(encoding='utf-8-sig') as f:require(sum(int(x['installed_quantity']) for x in csv.DictReader(f))==134,'Fastener total')
with (ROOT/'bom/PRINT_MANIFEST.csv').open(encoding='utf-8-sig') as f:
    rows=list(csv.DictReader(f));require(len(rows)==10,'Print manifest count')
    for row in rows:
        for key in ['STL','editable_STEP']:check_link(ROOT/'bom/PRINT_MANIFEST.csv',row[key])
geometry=json.loads((ROOT/'mechanical/GEOMETRY_CHECKS.json').read_text());require(not geometry['interferences'] and not geometry['blocked_drivers'],'Geometry baseline failed');require(len(geometry['driver_checks'])==48,'Driver count')
for n,h in geometry['source_sha256'].items():require(hashlib.sha256((ROOT/'mechanical'/n).read_bytes()).hexdigest()==h,'Stale geometry source: '+n)
for x in json.loads((ROOT/'mechanical/EXPORT_CHECKS.json').read_text()):require(x['passed'],'Export baseline failed: '+x['part'])
sources=json.loads((ROOT/'SOURCES.json').read_text())
for n,h in sources['supplier_SHA256'].items():require(hashlib.sha256((ROOT/'mechanical/supplier'/n).read_bytes()).hexdigest()==h,'Supplier fingerprint: '+n)
for fname in ['SIMULATION_CHECKS.json','MANUAL_CONTROL_CHECKS.json','DRIVING_WINDOW_CHECKS.json']:
    report=json.loads((ROOT/'simulation/mujoco'/fname).read_text());require(report['passed'],'Failed report '+fname)
    for n,h in report['source_sha256'].items():require(hashlib.sha256((ROOT/'simulation/mujoco'/n).read_bytes()).hexdigest()==h,'Stale simulation source '+fname+':'+n)
guide=json.loads((ROOT/'validation/assembly_guide.json').read_text());require(guide['passed'] and guide['pages']==11,'Assembly guide status')
for n,h in guide['source_sha256'].items():require(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,'Stale assembly guide source '+n)
act=json.loads((ROOT/'simulation/mujoco/ACTUATOR_MAP.json').read_text())
for k,path in [('CAD_parameters_sha256','mechanical/parameters.json'),('CAD_parts_sha256','mechanical/parts.json')]:require(hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==act[k],'Stale actuator map: '+path)
for name in ['simple_rov.xml','simple_rov_with_buoyancy.xml']:
 root=ET.parse(ROOT/'simulation/mujoco'/name).getroot()
 for mesh in root.findall('./asset/mesh'):require((ROOT/'simulation/mujoco/meshes'/mesh.attrib['file']).is_file(),'Missing XML mesh')
configs=json.loads((ROOT/'mechanical/configurations.json').read_text());require(configs['default']=='base','Default must omit buoyancy')
for key in ['base','with-buoyancy']:require((ROOT/'mechanical'/configs[key]['step']).is_file(),'Missing assembly variant')
configuration_report=json.loads((ROOT/'validation/configurations.json').read_text())
require(configuration_report['passed'],'STEP configuration readback failed')
for n,h in configuration_report['source_sha256'].items():require(hashlib.sha256((ROOT/n).read_bytes()).hexdigest()==h,'Stale configuration source: '+n)
require(configs['base']['dimensions_mm']==[213,210,148],'Standard size mismatch')
require(configs['with-buoyancy']['dimensions_mm']==[213,210,184.7],'Optional size mismatch')
optional={p['name'] for p in parts if p['optional_buoyancy']}
require(len(optional)==6 and not optional.intersection(configs['base']['included_parts']),'Optional geometry in base CAD')
require(optional <= set(configs['with-buoyancy']['included_parts']),'Missing optional CAD geometry')
for name,expected in [('simple_rov.xml',False),('simple_rov_with_buoyancy.xml',True)]:
 root=ET.parse(ROOT/'simulation/mujoco'/name).getroot()
 names={g.attrib.get('name','') for g in root.findall('.//geom')}
 require(optional.issubset(names) if expected else not optional.intersection(names),'XML optional visual configuration: '+name)
 require(any(n.startswith('proxy_foam') for n in names)==expected,'XML foam collision configuration: '+name)
gallery=json.loads((ROOT/'validation/gallery.json').read_text())
require(hashlib.sha256((ROOT/'mechanical/parts.json').read_bytes()).hexdigest()==gallery['source_parts_sha256'],'Stale gallery CAD source')
require(len(gallery['views'])==9 and gallery['default_configuration']=='base','Gallery view inventory')
for view in gallery['views']:
 require(view['pixels']==[2400,1800],'Gallery image dimensions')
 require(hashlib.sha256((ROOT/'docs/assets/gallery'/view['file']).read_bytes()).hexdigest()==view['sha256'],'Stale gallery image: '+view['file'])
status=json.loads((ROOT/'STATUS.json').read_text());require(not status['physical_tested'] and status['pcb_status']=='PLANNED_NO_DESIGN','Maturity status mismatch')
require('All rights reserved' in (ROOT/'LICENSE').read_text(),'Missing reserved rights notice')
if args.manifest:
    manifest=json.loads((ROOT/'MANIFEST.sha256.json').read_text());actual={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};require(manifest==actual,'Manifest differs from project files; update after final verification')
if errors:raise SystemExit('\n'.join(errors))
print(json.dumps({'status':'PASS','project_files':len(files),'printed_parts':10,'fit_coupons':2,'modeled_metal_fasteners':134,'manifest_checked':args.manifest,'physical_tested':False},indent=2))
