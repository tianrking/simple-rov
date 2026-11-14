# Electronics: future KiCad work

**Planned. No schematic, PCB, Gerbers, pick-and-place files or orderable electronics BOM are included.** Previous prototype PCBs are not part of this design.

Future work can use `kicad/`, `libraries/`, `bom/`, `fabrication/` and `validation/` directories. Include manufacturing outputs only after the native project, ERC/DRC, interfaces, thermal checks and output consistency have been reviewed.

First select the controller, four bidirectional ESCs, video host, power protection, communications, depth and leak detection. Collect real part envelopes and connectors, then check enclosure layout, service access, wiring, current and heat. See [mechanical interface constraints](interfaces/README.md).

No existing MCU or PCB is claimed to fit. The generic tray requires a board-specific adapter and positive retention.
