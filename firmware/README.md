# Onboard firmware: future work

**Planned. There is no flashable vehicle firmware in this repository.** `simulation/mujoco/environment.py` is a Python simulation and controller example, not an MCU application.

For the first prototype, evaluate an established controller that supports the actual four-thruster allocation and use classical feedback. After selecting hardware, add board configuration, build instructions, parameters, communication protocol, signal mapping and bench-test evidence.

Requirements include four independent bidirectional ESC outputs, IMU/depth acquisition, neutral/deadband/thrust calibration, saturation limits, loss-of-command shutdown, leak handling, an accessible power disconnect and logs. Do not publish an invented pinout or flash target before packaging and electronics are defined.
