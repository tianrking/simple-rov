# Mechanical and electrical interface constraints

- Geometry source: [mechanical/INTERFACES.json](../../mechanical/INTERFACES.json).
- Coordinates: mm, X forward / Y left / Z up. Standard envelope 213 × 210 × 148 mm; with reference buoyancy module, 213 × 210 × 184.7 mm. Excludes final connectors, cables and ballast.
- Enclosure reference: 50 mm series, 150 mm tube, 58 mm OD. Determine usable space with real endcaps, tray, connectors and wire bends; nominal tube length is not usable payload length.
- Tray: 100 × 35 mm; 8 × 3.4 mm slots centered at X = -40/-20/0/20 and Y = ±10 mm. Board adapters and positive axial tray retention are pending.
- Rear reference ports: 1 M10 + 8 M6. Penetrators, plugs and cable sealing method remain unselected.
- Camera: 32 × 32 mm board, 28 × 28 mm holes; rotated 180° about the optical axis to place USB above the board. Check the actual host and plug envelope.

New electronics must include native KiCad sources, board outline/hole coordinates, component heights and keepouts, connector service envelopes, power/wiring budget, mass and thermal records. If an interface changes, update CAD, BOM, assembly instructions and simulation inertial parameters together.
