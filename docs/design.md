# Structure and interface reference

[Illustrated assembly](assembly.md) · [PDF](assembly.pdf) · [Acceptance](acceptance.md)

SimpleROV uses two straight horizontal thrusters and two side-by-side vertical thrusters. The frame, fairing, carriers, camera mount and simulation are original project sources. Thrusters, camera and pressure hardware are attributed commercial references. This project does not make a rotating shaft seal or a PCB.

![Standard assembly](assets/gallery/hero.png)

## Layout and coordinates

CAD: mm, X forward, Y left, Z up. Standard envelope: **213 × 210 × 148 mm**, with no top foam/straps. The optional reference module increases height to **184.7 mm**. Final cables, penetrators, tether fittings, strap buckles and ballast are excluded.

| Module | Datum / role |
|---|---|
| Horizontal pair | Axes at (-78, ±74, 18) mm, along X; common thrust gives surge, differential thrust gives yaw |
| Vertical pair | Axes at (0, ±62, -40) mm, along Z; common thrust gives heave, differential thrust gives roll |
| Central enclosure | 150 mm tube, 58 mm OD, axis at Z = 22 mm |
| Camera | Lens front near X = 77.35, Y = 0, Z = 22 mm |
| Optional foam | Two 62 × 160 × 35 mm reference blanks, centered X = ±69 mm, with four tool reliefs and four longitudinal straps |
| Ballast / tether | Two bottom M3 slots; integrated rear 6 mm tether eye, without a rated recovery load |

The four controlled inputs are Fx, Fz, Mx and Mz. Sway and pitch are passive axes, with possible coupling. Real CG/CB placement must establish fore/aft trim; a controller cannot make this a fully actuated six-axis vehicle.

## Ten printed parts

| Prefix | Qty. | Function / print orientation |
|---|---:|---|
| V5_01_LOAD_CHASSIS | 1 | Closed frame, beams, enclosure saddles/stops and tether eye; base down |
| V5_02_UPPER_FAIRING | 1 | Freely flooding cover, locating lip and four screw wells; top down, local support |
| V5_03_SKID | 2 | Side skids and reinforced legs; print on side |
| V5_04_POD_CLAMP | 2 | Tube clamps with soft liners; end face down |
| V5_05_VERTICAL_CARRIER | 2 | 8 mm wall, two ribs and four foot bolts; motor face down, support flange ears |
| V5_06_MODULE_TRAY | 1 | Internal generic tray with module slots and camera-carrier holes |
| V5_07_CAMERA_CARRIER | 1 | Camera, USB relief and M2 nut pockets; local support |

Initial print settings: PETG, 0.2 mm layers, at least six walls and solid structural regions. Infill alone does not establish wet layer strength. Verify supports, nuts, holes and bed envelope in the slicer. The largest main part is about 210 × 210 mm in the bed plane; a nominal 220 mm printer needs sufficient usable travel and brim clearance.

## Commercial interfaces

**Thrusters: four APISQUEEN X2 complete waterproof units.** Use an opposite-handed pair for each axis, then calibrate actual force direction. Manufacturer dimensional references give D56.38 and axial length 60 mm with a 14/8 mm cross pattern. All four holes are currently interpreted as M3, and a 31 mm mounting-face offset is inferred. No OEM X2 STEP is available; the motor/duct/propeller geometry is reconstructed. Confirm hole types, blind depths, axial datums and cable exits with one physical unit and both coupons. Horizontal M3 × 8 and vertical M3 × 12 are trial selections targeting about 3 / 3.5 mm engagement, not permission to bottom screws.

**Camera: Blue Robotics Low-Light HD USB Camera.** The 32 × 32 mm board has 28 × 28 mm mounting spacing and OEM 2.44 mm holes. Supplier STEP locates board, lens and USB relative to the carrier. Rotate the board 180° about its optical axis to move USB above it; rotate captured images 180° accordingly. The actual cable/plug is not selected.

**Enclosure: Blue Robotics 50 mm series.** Reference set: 150 mm tube, front RAILS flange/transparent window and rear 1 M10 + 8 M6 flange cap. Supplier geometry is rigidly positioned; locking entries and window holes are aligned. Use six OEM M2 × 0.4-10 window screws with the supplier's stack. Procure matching O-rings, locking cords, plugs and penetrators as a compatible system. Geometry does not establish vehicle operating depth.

**Optional foam.** Default quantity is zero. The reference blanks are cut closed-cell material, secured through 3 × 7 mm guides by approximately 450 × 4.8 mm straps, no more than 1.2 mm thick. Buckles are not modeled. Select grade, thickness and placement from actual trim; see [buoyancy](buoyancy.md).

## Editing and provenance

The parameter-driven source is [build.py](../mechanical/build.py) with [parameters.json](../mechanical/parameters.json). Some local dimensions remain explicit constants. Changing a motor requires its full envelope, mounting-face offset, axial datums, wiring and screw stack, followed by interference, tool and flow checks. Do not scale purchased pressure hardware.

[STEP assemblies](../mechanical/assemblies/) define current standard and optional configurations. The [historical Onshape assembly](https://cad.onshape.com/documents/256f9be06adfdc472f7aac06/w/aefb43ce726d3d5c24877f23/e/1186baa4f5bb2c01f6be971a) contains the optional foam. Ten printed parts are directly editable imported solids, not native feature-history models. The rear commercial cap imported as an open 480-face shell; local OEM STEP remains solid. The other 29 cloud reference solids and the ten printed-part envelopes/volumes were checked in the [round-trip record](../validation/onshape/ONSHAPE_ROUNDTRIP.json). Do not manufacture pressure parts from the cloud shell reference. Onshape edits do not write back into Python.

[Development and rebuild](development.md) · [Gallery](gallery.md) · [Prototype plan](build-plan.md)
