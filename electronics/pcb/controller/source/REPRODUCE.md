# Reproduce the frozen candidate

Requires KiCad10.0.8's Python pcbnew+wx and its kicad-cli. Use a separate output directory; the script refuses to overwrite this distributed native project.

```
python source/rebuild.py --output-dir /absolute/path/to/rebuilt --kicad-cli /absolute/path/to/kicad-cli
```

Run that command with the Python interpreter bundled with KiCad (on macOS it resides inside KiCad.app/Contents/Frameworks/Python.framework). No router service or downloaded autorouter is required to replay the final saved routing.

Frozen inputs:design.json, native_common_sch.py, generate_native.py, route_completed.ses, silkscreen.json, the local standard footprint subsets, SimpleROV_HW.pretty and models. The electrical and geometry source is design.json; legacy seed designs and private work files are not shipped. The saved SES contains the routed copper; rebuild reassigns pad nets from a fresh native XML netlist, reapplies final component positions, corrects the1nm Specctra endpoint rounding, restores final silkscreen, and fills all four ground zones. It verifies ERC0/DRC0/unconnected0/parity0. UUIDs and timestamps can differ; the supplied native checked PCB and its manifest hashes identify the delivered artifact.

Original generation/replay scripts are all rights reserved. The footprint/model collections are licensed separately by KiCad; retain controller/third_party when redistributing those collections. The two simplified envelope models are explicitly documented in models/ENVELOPE_MODELS.md. To regenerate only those with CadQuery, run make_envelope_models.py with an explicit output directory.
