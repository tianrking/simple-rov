# Mechanical structure

`build.py` and `parameters.json` are the dimension-driven source. Supplier reference geometry lives in `supplier/`. CAD uses millimeters, X forward, Y left and Z up.

| Directory | Purpose |
|---|---|
| [stl/](stl/) | Ten individual main prints, oriented and placed on the bed |
| [step_parts/](step_parts/) | Ten editable solids in assembly coordinates |
| [fit_coupons/](fit_coupons/) | Two motor-interface test coupons |
| [assembly_meshes/](assembly_meshes/) | Assembly-coordinate meshes for visualization and simulation |
| [assemblies/](assemblies/) | Standard and optional-buoyancy assemblies |

Commercial thrusters, camera and pressure hardware are references, not project prints. Read the [assembly guide](../docs/assembly.md), [acceptance plan](../docs/acceptance.md) and [design reference](../docs/design.md).

## Assembly variants

The standard assembly has no top foam or straps: 213 × 210 × 148 mm. The reference buoyancy module increases height to 184.7 mm. Dimensions exclude final wiring, penetrators, ballast and strap buckles.

| Configuration | Assembly | With nominal metal fasteners |
|---|---|---|
| Standard | [simple-rov.step](assemblies/simple-rov.step) | [simple-rov-with-fasteners.step](assemblies/simple-rov-with-fasteners.step) |
| Optional buoyancy | [simple-rov-with-buoyancy.step](assemblies/simple-rov-with-buoyancy.step) | [simple-rov-buoyancy-with-fasteners.step](assemblies/simple-rov-buoyancy-with-fasteners.step) |

[configurations.json](configurations.json) records envelopes and included parts; [parts.json](parts.json) contains the full inventory with optional flags. Both assemblies use the same ten printed parts. Foam is cut from suitable purchased material, not printed. See [buoyancy and trim](../docs/buoyancy.md).

## Validation and cloud reference

[GEOMETRY_CHECKS.json](GEOMETRY_CHECKS.json) records nominal interference and 48 driver-path checks, with source hashes. [EXPORT_CHECKS.json](EXPORT_CHECKS.json) records print readback. [STRENGTH_SCREEN.json](STRENGTH_SCREEN.json) is a local ideal-section estimate, not FEA or a physical load rating.

The historical Onshape assembly includes the optional foam. Its ten printed parts are imported editable solids, without native sketch history. The rear commercial cap imported as an open reference shell; use the local OEM STEP for that reference. See the [round-trip record](../validation/onshape/ONSHAPE_ROUNDTRIP.json). Current default assemblies are defined by this repository.
