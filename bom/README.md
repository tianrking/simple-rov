# Bill of materials

These are mechanical prototype quantities, not a frozen whole-vehicle electrical BOM.

| File | Contents |
|---|---|
| [PRINT_MANIFEST.csv](PRINT_MANIFEST.csv) | Ten main prints and their STEP/STL paths; two fit coupons are separate |
| [BOM_FASTENERS.csv](BOM_FASTENERS.csv) | 38 M3 and 10 M2 screws, matching nuts and washers; 134 metal instances in total |
| [BOM_PURCHASED.csv](BOM_PURCHASED.csv) | Thrusters, enclosure, camera, liners and optional foam/straps; pending penetrators and ballast are marked |
| [FASTENER_INSTANCES.csv](FASTENER_INSTANCES.csv) | Head-seat datums for 48 screws |
| [KEY_HOLES.csv](KEY_HOLES.csv) | Key holes and coordinate conventions |
| [component-confirmation.csv](component-confirmation.csv) | Worksheet for actual part revisions, dimensions, mass, cables, ratings and fit evidence |

The six OEM acrylic-window screws may already be in the supplier kit; do not double-order them. Installed quantities exclude spares.

## Default and optional quantities

In the purchased BOM, `quantity` is the standard assembly quantity, `optional_quantity` is the add-on quantity, and `configuration` identifies its use. Top foam: **0 default / 2 optional**. Straps: **0 default / 4 optional**. Neither changes the ten prints or 134 nominal metal fasteners. Select foam only after weighing and checking submerged trim; see [buoyancy](../docs/buoyancy.md).

Start with one thruster and a matched bidirectional ESC, then test both coupons. Do not tighten a nominal screw into an unmeasured blind hole. Confirm the full battery/controller/four-ESC/video-host arrangement and thermal requirements before freezing an electrical BOM.

## Electrical and harness material lists

The [hardware package](../electronics/README.md) has separate [system](../electronics/bom/SYSTEM_BOM.csv), [harness](../electronics/bom/HARNESS_BOM.csv) and [consumables/tools](../electronics/bom/CONSUMABLES_TOOLS.csv) lists. Mechanical thrusters, camera and enclosure references are cross-referenced rather than ordered twice. The controller mount adds four screws, eight washers and four nuts (16 metal items) plus four insulating spacers; these are additional to the base 134 and are not silently included in its count.
