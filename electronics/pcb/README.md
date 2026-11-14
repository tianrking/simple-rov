# SimpleROV v0.0.1 hardware

Frozen engineering controller PCB for the current80x32mm interface. Native KiCad10 sources, checked reports, procurement/assembly files and mechanical exports are provided. This is a prototype design ready for independent fabrication review, not a tested propulsion system.

- Open controller/SimpleROV001_control.kicad_pro. Its local symbol library, used standard footprint subsets, modified footprint library and STEP models are included.
- verification/ERC.json and DRC.json are untouched KiCad CLI reports. DRC has0violations/0unconnected/0schematic-parity issues with no ignored DRC checks or exclusions. ERC has0violations; only SPICE model checking is ignored, because no SPICE simulation is claimed.
- controller/source/netlist.xml is exported from the final schematic. docs/CONNECTOR_PINOUT.csv and controller/source/physical_placement.json follow the final native PCB, not the earlier proposal.
- controller/BOM.csv lists individual purchased parts; controller/manufacturing holds fabrication layers, separate drills and SMT-only placement data. USB is a manual mixed-technology placement.
- mechanical/controller_assembled.step uses board-bottom origin and includes111 KiCad model instances plus explicit IMU/USB envelopes. Mated connector keepouts and wire-bend reservations are separate STEP files, built from final native placement. Apply world translation[-50,-16,13]mm to each. Complete enclosure and cable fit is still a system integration task.
- docs/FAULT_CHAIN_AND_SENSE.md gives J9 arming behavior, non-inverting PWM and the1k0.5W source-resistor MPN/formula. docs/DESIGN_AND_QUALIFICATION.md specifies assembly and the unperformed physical qualification stages.
- controller/source/rebuild.py reproduces a separate candidate from frozen JSON, local libraries and the saved route session. It reruns ERC/DRC. See controller/source/REPRODUCE.md.

The prototype requires the exact5V-BEC ESC interface. Inhibit is static HIGH/no frames and does not prove the motor stops. First system commissioning is limited to regulated12V/5A total, per the main system plan. No board firmware or physical bench tests are represented as completed.

Original SimpleROV project materials:All rights reserved. Redistributed KiCad collections and modified KiCad footprints remain under the upstream CC BY-SA4.0 license with its electronic-design exception; see controller/third_party. No vendor datasheet full texts are redistributed. This package does not write, commit or push the shared repository.
