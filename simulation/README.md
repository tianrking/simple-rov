# MuJoCo simulation

MuJoCo **4.0.1** provides the rigid-body plant. The foundation adds validated scenario configuration, water-relative loads, bounded allocation, actuator dynamics/failure/timeout, sensor proxies, classical control, reproducible benchmarks and an optional Gymnasium 1.4.0 task.

[Simulation foundation](../docs/simulation-foundation.md) · [Installation and driving](../docs/simulation.md) · [Quick start](../README.md#run-the-simulation)

The default is the foam-free assembly, fully submerged. Parameters remain uncalibrated. Native ellipsoid and analytic water backends are alternatives; neither is CFD. Classical control is the initial real-vehicle baseline; no trained policy or firmware is included.
