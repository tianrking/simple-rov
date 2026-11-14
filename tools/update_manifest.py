from pathlib import Path
import json,hashlib
from project_files import ROOT,project_files
manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in project_files()}
(ROOT/'MANIFEST.sha256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
print('Manifest:',len(manifest),'files')
