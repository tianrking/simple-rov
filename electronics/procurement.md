# Procurement and BOM use

The CSV files describe the complete functional purchasing scope and distinguish selected references from parts held for interface or physical verification. They do not certify a fitted, powered or pressure-tested vehicle.

| Table | Scope |
|---|---|
| [SYSTEM_BOM.csv](bom/SYSTEM_BOM.csv) | Purchased modules, PCB assembly, sensors, power and shore equipment |
| [HARNESS_BOM.csv](bom/HARNESS_BOM.csv) | Each power/data/phase/control harness and connector family |
| [CONSUMABLES_TOOLS.csv](bom/CONSUMABLES_TOOLS.csv) | Insulation, fasteners, labels, seal supplies, spares and test equipment |
| [PCBA BOM](pcb/controller/BOM.csv) | Exact parts populated on one controller |
| [Controller mating parts](bom/CONTROLLER_HARNESS_PARTS.csv) | Cable-side housings/contacts and external resistors, not additional populated chips |
| [Existing mechanical BOM](../bom/README.md) | Printed parts, structural fasteners, enclosure reference and propulsion/camera references |

## Quantity and purchasing rules

`installed_qty` is a system allocation. `new_purchase_qty` is the incremental purchase allocation before checking existing stock. `reference_only` rows identify parts already represented in the mechanical BOM, so they must not be added again when consolidating procurement. A quantity of one PCB assembly means one assembled board: do not also add every populated PCB IC to the system-module shopping cart. Bare PCB fabrication and assembly quantities come from the board BOM/order process, including selected spares and minimum order quantities.

`HARNESS_BOM.csv` is a wiring and assembly breakdown, not a second shopping cart. A connector or fuse named in a harness termination refers to the matching purchased component in `SYSTEM_BOM.csv`; do not add it again. For example, the XT90S mating pair in SYS-013 is incorporated into HAR-001, and the four XT60H pairs in SYS-014 terminate HAR-003. HAR-012 uses the cable already supplied with the camera. Module-supplied adapters and cables are checked against actual kit contents before any additional order.

The first-stage main fuse is SYS-015, **0287075.L / 7.5 A ATOF**, with its SYS-016 holder and an enforced 5 A source ceiling. The future **40 A MIDI** alternative is SYS-031/SYS-032, currently quantity zero. HAR-002’s M5 terminals belong only to that future alternative and are also quantity zero; do not order them for the first-stage ATOF harness.

`CONSUMABLES_TOOLS.csv` distinguishes installed extras, stock, existing mechanical references, optional items and shore tools. Its four spacers and one PCB-fastener set add **16 metal items** to the controller mount; they do not replace or repeat the base mechanical BOM’s 134 metal items. Fuse-spare rows are additional stock rather than installed fuse quantities. The enclosure seal kit and optional buoyancy items remain references to the mechanical procurement list, not duplicate purchases.

Every `stock_allocation` is a purchasing allowance or routing estimate, **not a production cut length**. Stock may serve several harnesses, so consolidate by gauge, color and cable construction before ordering; do not blindly add overlapping descriptions. Final cut lengths are measured after the real connector, service-loop, strain-relief and enclosure layout is approved. The tables deliberately retain quantities for unresolved feedthroughs, protection and battery functions; a HOLD does not mean the part is unnecessary. Currency, stock and prices are not frozen. Check exact current product revisions, included leads, kit contents and shipping restrictions before purchasing.

## Status definitions

| Status | Meaning |
|---|---|
| SELECTED_REFERENCE | Concrete manufacturer reference selected; verify exact delivered variant and perform stated tests |
| PCB_DEPENDENT | Final connector/MPN/circuit comes from the reviewed native control-board design |
| RFQ_HOLD | A supplier-built item requires a documented quotation/specification before purchase |
| FIT_HOLD | A product or function is known, but package, seal, wire or thermal compatibility is unresolved |
| OPTIONAL | Not required for the first build; explicitly selected only when the need is measured |
| BENCH_ONLY | Shore/test equipment, not installed in the submerged robot |

The final [connector pin map](interfaces/CONTROLLER_PINOUT.csv) and [wiring table](wiring.md#controller-connector-map) resolve controller harness ends to J1–J11. Functional `CTRL.*` endpoint names remain in the system allocation table; use the numerical pin map for crimping, followed by a full continuity check. GH contacts require their specified AWG30–26 conductor and 0.76–1.0 mm insulation range; the selected harness uses 26 AWG at the PCB.

## Purchase in controlled groups

1. Inspect existing stock and supplier-kit contents. Obtain one matched X2/ESC set, its delivered drawing, cable details and input specification before buying the other three.
2. Obtain controller-PCB review exports, selected logic/video modules and a protected 12 V bench harness. Verify power rails, UART/I²C, video and neutral outputs without propulsion power.
3. Freeze actual electronics/connector envelopes and the complete port plan. Add all board adapters, insulating hardware, tray retention, penetrators and plugs to the physical mock-up.
4. After the single-channel motor test and wiring/thermal review, assemble remaining channels. Keep the current-limited supply and conservative output bounds.
5. Mobile battery procurement requires a professionally assembled pack specification, voltage limits, protection/charging arrangement, real dimensions, mass and a matching enclosure/mount. Do not buy a generic 4S LiPo or loose cells as a substitute.

## Current release holds

- Actual X2/ESC revision, 3.3 V/5 V input behavior, neutral dwell, lost-signal behavior and full battery operating-voltage interpretation.
- A complete motor-power fuse/holder/junction/harness package, including temperature-rise and fault coordination.
- Fit of the video stack, controller, four ESCs, battery and connectors; no complete single-tube fit has been demonstrated.
- Positive tray retention and the complete M10/M6 penetrator/blank/vent allocation, including actual cable sealing.
- Mobile battery pack and approved charger/lead interface; complete mass, submerged trim and thermal budget.

Manufacturing review files are not proof of a qualified whole-system release. Keep physical-test records with the exact component revisions and update the BOM after each approved substitution.
