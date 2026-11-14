"""Run native KiCad ERC/DRC/netlist and bind the results to exact input files."""
from pathlib import Path
import hashlib,json,shutil,subprocess,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[2]
P=R/'electronics/pcb/controller'
V=R/'electronics/validation'
cli=shutil.which('kicad-cli') or '/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
commands=[['sch','erc','SimpleROV001_control.kicad_sch','--format','json','--severity-all','--exit-code-violations','--output','../../validation/erc.json'],['pcb','drc','SimpleROV001_control.kicad_pcb','--format','json','--severity-all','--schematic-parity','--exit-code-violations','--refill-zones','--output','../../validation/drc.json'],['sch','export','netlist','--format','kicadxml','--output','../../validation/controller.net.xml','SimpleROV001_control.kicad_sch']]
for command in commands:
    result=subprocess.run([cli]+command,cwd=P,text=True,capture_output=True)
    if result.returncode:raise SystemExit(result.stdout+result.stderr)
    print(result.stdout.strip())
# KiCad netlist embeds an absolute design-source path even for a relative input.
# Only this publication metadata field is made portable; component/net data stay intact.
f=V/'controller.net.xml';tree=ET.parse(f);tree.find('./design/source').text='SimpleROV001_control.kicad_sch';tree.write(f,encoding='utf-8',xml_declaration=True)
paths=[p for p in P.rglob('*') if p.is_file() and (p.suffix in ('.kicad_pro','.kicad_pcb','.kicad_sch','.kicad_dru','.kicad_sym','.kicad_mod') or p.name in ('fp-lib-table','sym-lib-table'))]+[R/'tools/hardware/run_native_checks.py']
report={'tool':subprocess.check_output([cli,'version'],text=True).strip(),'commands':commands,'netlist_metadata_normalization':'Only design/source absolute path replaced by schematic filename; native ERC/DRC JSON unchanged.','source_sha256':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)},'outputs':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [V/'erc.json',V/'drc.json',f]}}
(V/'native_checks.json').write_text(json.dumps(report,indent=2)+'\n')
print('Bound native checks to the published source files')
