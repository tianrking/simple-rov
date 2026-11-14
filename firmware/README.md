# Onboard firmware: future work

**Planned. There is no flashable vehicle firmware in this repository.** `simulation/mujoco/environment.py` is a Python simulation and controller example, not an MCU application.

For the first prototype, evaluate an established controller that supports the actual four-thruster allocation and use classical feedback. After selecting hardware, add board configuration, build instructions, parameters, communication protocol, signal mapping and bench-test evidence.

Requirements include four independent bidirectional ESC outputs, IMU/depth acquisition, neutral/deadband/thrust calibration, saturation limits, loss-of-command shutdown, leak handling, an accessible power disconnect and logs. Do not publish an invented pinout or flash target before packaging and electronics are defined.

## Selected hardware interface

The controller design uses RP2040 with an SPI ICM-42688-P IMU and four optocoupled ESC outputs. [SYSTEM_CHANNELS.json](../electronics/interfaces/SYSTEM_CHANNELS.json) aligns connector channels and positive thrust with the MuJoCo actuator map. Use the actual board pin table for GPIO assignment and electrical levels; the Pi video/networking host communicates by 3.3 V UART. The IMU is a six-axis device: absolute yaw is not independently observed, so heading drift and any later magnetic/visual reference require a separate implementation and calibration.

Normal output pulses have the same polarity as the MCU waveform in the driver circuit. Inhibition produces a fixed level rather than a 1500 µs neutral frame; actual ESC loss-of-signal behavior must be tested before relying on it. Implement boot inhibit, sensor checks, fresh-command timeout, watchdog servicing and an explicit rearm sequence; no such firmware is currently shipped. See [wiring](../electronics/wiring.md) and [commissioning](../electronics/commissioning.md).
