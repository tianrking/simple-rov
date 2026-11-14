"""Render the published native PCB with KiCad; no image synthesis or photo claim."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

R=Path(__file__).resolve().parents[2]
cli=shutil.which('kicad-cli')
if not cli:
    mac=Path('/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli')
    if mac.is_file():cli=str(mac)
if not cli:raise SystemExit('Install KiCad 10 and put kicad-cli on PATH.')
board=Path('electronics/pcb/controller/SimpleROV001_control.kicad_pcb')
out=R/'docs/assets/hardware';out.mkdir(parents=True,exist_ok=True)
base=[cli,'pcb','render',str(board),'--width','1800','--height','1000','--side','top','--background','opaque','--quality','high','--floor','--zoom','1.25']
subprocess.run(base+['--output','docs/assets/hardware/controller-top.png'],cwd=R,check=True,capture_output=True,text=True)
subprocess.run(base+['--perspective','--rotate','335,0,20','--output','docs/assets/hardware/controller-angle.png'],cwd=R,check=True,capture_output=True,text=True)
sources=[board,Path('tools/hardware/render_controller.py')]
sources += [p.relative_to(R) for p in (R/'electronics/pcb/controller').rglob('*.step')]
report={'renderer':'KiCad native PCB raytracer','version':subprocess.check_output([cli,'version'],text=True).strip(),
'scope':'PCB design rendering; not a photograph, populated-board test or complete vehicle fit. Some nonstandard component models can be declared dimension envelopes.',
'source_sha256':{str(p):hashlib.sha256((R/p).read_bytes()).hexdigest() for p in sources},
'images':{str(p.relative_to(R)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(out.glob('controller-*.png'))}}
(R/'electronics/validation/controller_renders.json').write_text(json.dumps(report,indent=2)+'\n')
print('Rendered native controller top and perspective views')
