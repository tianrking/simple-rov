# Electronics: deferred design

**Planned. No schematic, PCB, Gerbers, pick-and-place files or orderable electronics BOM are included.** The custom-controller candidate is deferred and excluded from the current release. Its engineering files are retained on the [draft/controller-pcb branch](https://github.com/tianrking/simple-rov/tree/draft/controller-pcb) for reference.

Future work can use `kicad/`, `libraries/`, `bom/`, `fabrication/` and `validation/` directories. Include manufacturing outputs only after the native project, ERC/DRC, interfaces, thermal checks and output consistency have been reviewed.

First select the controller, four bidirectional ESCs, video host, power protection, communications, depth and leak detection. Collect real part envelopes and connectors, then check enclosure layout, service access, wiring, current and heat. See [mechanical interface constraints](interfaces/README.md).

No existing MCU or PCB is claimed to fit. The generic tray requires a board-specific adapter and positive retention.
