# MuJoCo simulation

The runnable implementation in [mujoco/](mujoco/) includes the current CAD appearance, rigid body, four thrust locations, explicit Python buoyancy/drag, motor lag and classical control.

[Installation, operation and assumptions](../docs/simulation.md) · [Quick start](../README.md#run-the-simulation)

This is an underactuated, fully submerged, still-water demonstrator with uncalibrated hydrodynamics. It has no CFD, waves/currents, free surface, tether, optical refraction or reinforcement-learning environment. Use classical control for initial remote operation and stabilization. Later policy work needs explicit observations, actions, rewards, parameter randomization and independent evaluation.
