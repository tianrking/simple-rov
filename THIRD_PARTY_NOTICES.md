# Third-party provenance and rights

Original frame, mounts, tray, camera carrier, documentation and simulation code were created for this project. They are not a copy of a complete commercial ROV design. The four-thruster layout is a standard SimpleROV-4 arrangement.

| Material | Owner / source | Treatment in this repository |
|---|---|---|
| Pressure tube, front flange, rear flange cap and camera native STEP | Blue Robotics, [technical reference](https://bluerobotics.com/learn/technical-reference/) | Purchased-component reference geometry. Original files in `mechanical/supplier/` retain their upstream ownership. Assembly uses rigid transforms. |
| Original WTE2 acrylic endcap design | Blue Robotics, [original enclosure announcement](https://bluerobotics.com/our-original-watertight-enclosure-designs-are-now-open-source/) | The announcement licenses its identified original enclosure files under CC BY 4.0. This is not a blanket license for modern Blue Robotics CAD. |
| X2 dimension drawing | APISQUEEN, [product page](https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters) | Manufacturer reference image, separately attributed. X2 meshes are dimension reconstructions, not OEM solids or printable motor designs. |
| Derived supplier meshes and combined STEP assemblies | Derived from the component references above | Simplified meshes for assembly/visualization. No claim of ownership or new license over upstream component geometry. |
| MuJoCo, CadQuery, GLFW and other Python dependencies | Their respective upstream projects | Installed dependencies, not vendored software. Their own licenses apply. |

SOURCES.json records source pages and SHA256 fingerprints of native supplier files. Publicly downloadable CAD is not assumed to carry a general open-source license: where a specific license has not been confirmed, upstream rights are retained and no additional reuse rights are granted by this project. Users distributing or manufacturing third-party designs must check the relevant upstream terms. Brand names identify compatibility and sources; no endorsement is implied.

The project LICENSE applies only to original project work. Public visibility is not an open-source grant.
