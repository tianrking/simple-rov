from pathlib import Path
import cadquery as cq,json
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True);args=ap.parse_args();r=Path(args.output_dir).resolve();r.mkdir(parents=True,exist_ok=True)
def box(x0,y0,z0,x1,y1,z1):return cq.Workplane('XY').box(x1-x0,y1-y0,z1-z0,centered=False).translate((x0,y0,z0)).val()
# Package BSC body 3x2.5, edge +/-0.1, max A=.97 in TDK DS-000347 1.2 p54/55.
cq.exporters.export(box(-1.6,-1.35,0,1.6,1.35,.97),str(r/'ICM42688_max.step'))
# Deliberately conservative service connector volume, not a manufacturer shape.
a=[box(-4.2,-3.6,0,4.2,2.6,3.5)]
for x in [-3.5,3.5]:
 for y in [-1.2375,1.4625]:a.append(box(x-.45,y-.55,-2.4,x+.45,y+.55,0))
cq.exporters.export(cq.Compound.makeCompound(a),str(r/'USB105017_conservative.step'))
(r/'ENVELOPE_MODELS.md').write_text('''# Original simplified envelopes\n\nICM42688_max.step is an original rectangular max package envelope:3.2x2.7x0.97mm. TDK package is3x2.5 BSC with0.1 edge tolerance and maximum thickness0.97mm, DS-000347 revision1.2 pages54/55. It preserves footprint pin1 orientation; it is not manufacturer CAD.\n\nUSB105017_conservative.step is an original engineering clearance envelope,8.4x6.2x3.5mm above PCB. Four conservative tab volumes reach2.4mm below PCB top,0.8mm below a1.6mm PCB. These dimensions are allowances, not sourced manufacturer maxima. The exact Molex1050170001 model was unavailable; physical height/tab protrusion require measurement. The local KiCad footprint is the standard named Molex footprint. Reference:https://www.molex.com/en-us/products/part-detail/1050170001 and its sales drawing. The assembly cannot be described as manufacturer-complete mechanical CAD.\n\nOriginal simplified models:All rights reserved. Other models in this folder are unmodified KiCad library copies under the separately included KiCad CC BY-SA4.0 license plus electronic-design exception.\n''')
print('Created two explicitly documented envelope models')
