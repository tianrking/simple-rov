# Mechanical and electrical interfaces

The mechanical baseline remains the current small SimpleROV assembly. Coordinates are mm, X forward, Y left and Z up. Standard envelope: 213 × 210 × 148 mm; optional buoyancy module: 184.7 mm high. Final cables, connectors and ballast are excluded.

- [Mechanical source interfaces](../../mechanical/INTERFACES.json): thruster locations, tray slots, camera, tether eye and reference ports.
- [Controller mounting contract](MECHANICAL_CONTRACT.json): 80 × 32 × 1.6 mm outline, four 3.2 mm NPTH holes, coordinate transforms, spacers and declared height limits.
- [Controller mount review](../validation/controller_mount.json): declared-envelope collision and slot-alignment checks.
- [Native controller fit report](../validation/native_controller_fit.json) and [STEP](../mechanical/native-controller-fit.step): all exported PCB/component solids, GH plug/wire reservations and mounting hardware against the unchanged core geometry; not complete vehicle payload packaging.
- [Mount reference STEP](../mechanical/controller-mount-review.step): unchanged tray/camera carrier plus a labeled board envelope, spacers and nominal fasteners; not populated-PCB CAD.

The reference enclosure uses a 150 mm tube with 58 mm OD and a nominal 50 mm central bore. Nominal tube length is not usable payload length. Account for both end fittings, the camera/carrier, connectors and wire service loops. The existing tray is 100 × 35 mm; selected slots at global X = −40/20, Y = ±10 mm receive the controller through bolts.

The contract uses 5 mm insulating spacers, PCB bottom Z = 13 mm and the original tray support top Z = 8 mm. Four M3×14 screws, eight M3 washers and four nuts add 16 metal pieces; four spacers are additional nonmetal items. The base mechanical BOM remains 134 metal pieces. Confirm actual screw engagement and clearances on the printed tray.

The sole reference M10 port is reserved for the Bar02 depth sensor; eight M6 ports remain. Thread, sealing seat, cable bore and all actual seal parts must match the purchased revisions. A port count is not a sealed-harness design. Do not enlarge pressure-hardware holes or modify manufacturer seal surfaces to make a selected cable fit.

Positive axial tray retention and complete electrical packaging remain unresolved. The board mounting review does not establish battery/ESC/video/harness fit, connector access, thermal capability, sealing or recovery strength. Native outline, hole centres and component/GH plug reservations have passed the recorded nominal digital checks; physical tolerances, actual wire bends and assembly access remain to be checked.
