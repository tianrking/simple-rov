"""Build a versioned source/engineering ZIP with a verifiable file inventory."""
import hashlib,json,zipfile
from project_files import ROOT,project_files
status=json.loads((ROOT/'STATUS.json').read_text());manifest=json.loads((ROOT/'MANIFEST.sha256.json').read_text())
for name,h in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
out=ROOT/'runs/releases';out.mkdir(parents=True,exist_ok=True);path=out/f"simple-rov-{status['release']}.zip"
with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as f:
    for p in [*project_files(),ROOT/'MANIFEST.sha256.json']:f.write(p,'simple-rov/'+str(p.relative_to(ROOT)))
with zipfile.ZipFile(path) as f:
    assert f.testzip() is None
    for name,h in manifest.items():assert hashlib.sha256(f.read('simple-rov/'+name)).hexdigest()==h,name
print(path);print('SHA256',hashlib.sha256(path.read_bytes()).hexdigest())
