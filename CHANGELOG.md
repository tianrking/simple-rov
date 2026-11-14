# Changelog

## v0.6.0

- Verify MuJoCo 4.0.1 as the current stable runtime; retain a reproducible version pin.
- Add validated per-instance scenarios, seeded uncertainty, water-relative drag, current/shear, a tension-only tether and an optional native ellipsoid backend.
- Add bounded weighted allocation with explicit residual/rank, delayed/rate-limited thrusters, normalized command curves and stale-command timeout.
- Separate truth and sampled sensor proxies; run classical control at 50 Hz over 500 Hz physics with complete run metadata.
- Add a checked Gymnasium 1.4.0 sensor-based depth/heading task, normalized observations and episode limits; no trained policy.
- Add calibration tooling, physical-invariant tests, timestep comparison and an 18-case seeded scenario benchmark.
- Mechanical geometry is unchanged. Parameters remain uncalibrated; no physical performance or global optimality claim.


## v0.5.2

- Make English the default for project documentation, assembly PDF, diagram labels, offline HTML and the component-confirmation worksheet.
- Add a Spanish README and preserve a Chinese entry point, with visible language navigation.
- Refine the project landing page with centered navigation, compact specifications, structured galleries and expandable technical views.
- Add actual Onshape screenshots, explicitly labeled as the historical assembly with optional buoyancy fitted.
- Use English media filenames and keep existing mechanical part IDs and geometry unchanged.


## v0.5.1

- Unify the public project name as SimpleROV and expand README/navigation.
- Make top foam and straps optional: 213 x 210 x 148 mm default, 184.7 mm optional height; four assembly STEP files and explicit purchase quantities.
- Provide standard/optional MuJoCo models and CLI selection; hydrodynamics remain shared example parameters.
- Add a 2400 x 1800 gallery, six orthographic views, interior and configuration comparison; update illustrated guide, PDF and HTML.
- Add configuration, gallery and BOM consistency checks. Digital documentation update; no physical tests.

## v0.5.0 - 2026-11-14

Initial public engineering repository for mechanical revision V5-01.

- Original SimpleROV-4 frame, fairing, skids, pod clamps, vertical carriers, module tray and camera carrier.
- Ten independent printable STL/STEP parts, two motor-interface coupons, combined assemblies and commercial-component references.
- Mechanical BOM, interface coordinates, digital geometry/export reports and 11-page illustrated assembly manual.
- MuJoCo model, explicit uncalibrated water forces, four-thruster allocation, classical control, independent GLFW driving and functional checks.
- Organized locations for future KiCad hardware and embedded firmware; neither is implemented in this release.
- Public visibility with all rights reserved for original work; separate third-party provenance.
