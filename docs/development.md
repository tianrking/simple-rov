# Development, reproduction and releases

Run commands from the repository root in a Python 3.12 virtual environment. Dependencies are grouped into `requirements/sim.txt`, `requirements/cad.txt` and `requirements/docs.txt`. Do not commit virtual environments, credentials, personal configuration or run logs.

## Simulation

`python simulation/mujoco/run.py --viewer --manual --seconds 300` opens the dedicated GLFW driving window on the Python main thread. On macOS, the automatic native MuJoCo viewer can be launched with `python simulation/mujoco/launch_macos.py --seconds 120`; it repairs the selected virtual environment's libpython link when required, without modifying system Python.

`--output-dir runs/demo` selects a run directory; otherwise a UTC timestamp is used. `verify.py` checks allocation, motion signs and depth/attitude response. `verify_manual.py` checks command targets and release behavior. `verify_driving_window.py` creates an OpenGL window to check callbacks and framebuffer rendering; it requires a desktop and does not inject operating-system keyboard events.

## CAD

Geometry is defined in `mechanical/build.py`, parameters in `mechanical/parameters.json`. Preserve supplier STEP revisions in `mechanical/supplier/`. Build commands are in the root README. Geometry boolean operations may take time.

`export_metadata.py` reads back print exports and updates BOM/interfaces. Then run `python mechanical/verify_configurations.py` to read both assembly STEP files and check envelope, solid counts and optional purchase quantities.

The default is `assemblies/simple-rov.step`; the optional variant is `assemblies/simple-rov-with-buoyancy.step`. Each also has a nominal-fastener version. A simulation rebuild writes both `simple_rov.xml` and `simple_rov_with_buoyancy.xml`; select with `--configuration`. Both use explicit water-model assumptions until calibrated.

Reports record source hashes. A changed source invalidates its old report; regenerate and recheck rather than merely changing the recorded hash.

## Documentation and images

English is the default. `README.es.md` and `README.zh-CN.md` are language entry points; technical manuals are in English. Preserve dimensions, configuration defaults, physical-validation boundaries and rights across languages.

Assembly content is defined in `tools/docs/content.py`; PDF, Markdown and local HTML are generated from it. Other documents are edited as Markdown.

```bash
python -m pip install -r requirements/docs.txt
python tools/docs/make_figures.py
python tools/docs/build_pdf.py
python tools/docs/build_web.py
```

`make_figures.py` also regenerates the nine-view gallery. Run `python tools/docs/render_gallery.py` for the gallery alone. English figures use standard Latin fonts; `SROV_FONT` optionally selects a TrueType font for gallery labels. The PDF uses built-in Helvetica. Render every PDF page with `pdftoppm` and visually inspect it before recording a completed review.

Onshape captures are real browser screenshots, not generated renders. Keep their source URL, configuration and hashes in `validation/onshape/screenshots.json`. Do not imply the historical cloud assembly is the current foam-free default.

## Integrity and packaging

```bash
python tools/validate_repository.py
python tools/update_manifest.py
python tools/validate_repository.py --manifest
python tools/build_release.py
```

The inventory excludes Git, environments, caches and `runs/`. Release ZIPs go to `runs/releases/`; update STATUS and CHANGELOG with a new version. GitHub Actions checks repository integrity and headless simulation, not physical reliability.

`requirements/lock-macos-py312.txt` records the original complete macOS/Python 3.12 validation environment. Linux CI installs `requirements/sim.txt`; native libraries are not assumed identical across platforms. CSV files use LF so fingerprints match a Git checkout.
