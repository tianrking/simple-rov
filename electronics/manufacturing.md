# Controller fabrication and assembly review

Open the self-contained [KiCad project](pcb/controller/SimpleROV001_control.kicad_pro) in KiCad 10.0.8. The checked artifact is an **80 × 32 × 1.6 mm, four-layer** engineering prototype. The PCB carries controller/sensor current only. Read the [electrical review](validation/ELECTRICAL_REVIEW.md) and [qualification plan](pcb/docs/DESIGN_AND_QUALIFICATION.md) before fabrication.

## Files for quotation

| File | Role |
|---|---|
| [Gerber/drill ZIP](pcb/controller/manufacturing/jlc_review/Gerber_drill_review.zip) | Copper, mask, paste, silkscreen, outline and separate PTH/NPTH drills |
| [JLC-format BOM](pcb/controller/manufacturing/jlc_review/BOM_JLC_review.csv) | Grouped designators, footprint and exact manufacturer part numbers |
| [JLC-format placement](pcb/controller/manufacturing/jlc_review/CPL_JLC_review.csv) | Top-side positions and native rotation values |
| [Full populated-parts BOM](pcb/controller/BOM.csv) | Per-reference canonical purchasing record |
| [Top assembly](pcb/drawings/assembly_top.pdf) / [bottom assembly](pcb/drawings/assembly_bottom.pdf) | Part identifiers, connector orientation and rear test pads |
| [Schematic](pcb/drawings/schematic.pdf) | Native circuit export; zoom the A0 drawing for pin/net detail |

These converted columns follow the [JLC BOM](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly) and [placement](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly) specifications. **LCSC numbers are blank:** live stock, approved substitutions and supplier assembly rotations have not been selected. They must be reviewed in the assembly preview against each manufacturer's pin-1/package drawing. No fabrication/assembly order has been submitted. This is a quotation/review package, not a preapproved one-click production order.

The native position export uses its absolute origin, X right / Y up; negative Y values are retained. The conversion does not invent centroid offsets or supplier rotation corrections. Confirm the board outline/origin and every part in the manufacturer's preview. All purchased components are on top. J11 is mixed SMT/PTH and deliberately absent from the SMT-only placement CSV: arrange its manual placement/reflow and retention-tab soldering with the assembler. J10 and TP1–6 are bare copper features, not purchased connectors. Do not order mounting-hole footprints as components.

## Manufacturing settings to confirm

- Four copper layers F.Cu / In1.Cu / In2.Cu / B.Cu; 1.6 mm FR-4. Agree a real manufacturer stack-up; no controlled-impedance certification is claimed.
- Quote the actual 0.10 mm minimum track width, 0.127 mm minimum electrical clearance and 0.30 mm via drill / 0.60 mm diameter. QFN 0.4 mm pitch and the IMU LGA require capable assembly and inspection.
- Four mounting holes are **3.2 mm NPTH**, with copper kept at least 3.7 mm from each centre. Keep PTH and NPTH drill classification intact.
- Request electrical net test and fabricator DFM. Decide finish, stencil/reflow process, moisture handling and inspection with the assembler; inspect the RP2040 exposed pad and IMU joints.
- Some secondary silkscreen text is 0.8 mm high. Confirm the manufacturer's accepted silkscreen process and clipping rules; the [JLC character guidance](https://jlcpcb.com/blog/character-design-specifications) distinguishes process capabilities. Numerical pin tables remain the connection authority.
- Keep the original design rights and [redistributed library notices](pcb/controller/third_party/ATTRIBUTION.md) with the engineering sources.

## Rebuild and evidence

The native engineering package includes its own [reproduction instructions](pcb/controller/source/REPRODUCE.md). Changes to the circuit, placement or route require new native ERC/DRC, netlist, manufacturing files and fit review. The system scripts are:

```bash
python tools/hardware/run_native_checks.py
python tools/hardware/export_jlc_review.py
python tools/hardware/render_controller.py
python tools/hardware/check_controller_mount.py
python tools/hardware/check_native_fit.py
python tools/hardware/verify_hardware.py --publish
python tools/hardware/verify_hardware.py --check
```

The first two need the native exports/KiCad as applicable; the two fit scripts need `requirements/cad.txt`. `--publish` records consistency evidence after fresh KiCad checks, and CI checks the committed fingerprints. It does not rerun KiCad or perform a physical test in CI. See [integration checks](validation/INTEGRATION_CHECKS.json), [JLC conversion record](validation/jlc_review_export.json) and [commissioning](commissioning.md).
