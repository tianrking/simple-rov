# Hardware architecture — SimpleROV v0.0.1

The first hardware build targets a recoverable freshwater-pool prototype with four independent bidirectional thrusters, a tethered operator, USB video and classical stabilization. The control PCB is a low-power controller/interface board; motor current travels through a separate fused harness. Native PCB files and their exact connector contract govern assembly. This system plan is not flashable firmware or proof of a completed underwater vehicle.

## Data and control

```text
Topside computer + USB gamepad
              | Ethernet: control, telemetry and compressed video
       5–10 m trial data tether
              |
     Pi Zero 2 W + Ethernet/USB hub ----- USB camera
              | 3.3 V UART
      Independent real-time controller ----- IMU / pressure / leak inputs
              | four independent ESC control channels
      H_LEFT   H_RIGHT   V_LEFT   V_RIGHT
              | three motor phase conductors per ESC
         Four APISQUEEN X2 thrusters
```

The Pi forwards operator targets and streams the camera's existing H.264 output. Its Linux scheduler does not generate propulsion PWM. A real-time MCU owns arming, validity checks, motor neutral, feedback control and output limiting. The reference Pi is 65 × 30 mm; the Waveshare ETH/USB HUB HAT adds Ethernet and USB host ports. The camera draws up to 220 mA at 5 V. These selected modules are not a verified fitted stack. [Pi](https://www.raspberrypi.com/documentation/computers/zero.html) · [Hub](https://www.waveshare.com/product/raspberry-pi/hats/interface-power/eth-usb-hub-hat.htm) · [Camera](https://bluerobotics.com/store/sensors-cameras/cameras/cam-usb-low-light-r1/).

Use a standard 100BASE-TX-capable cable/termination for the short trial link, preserving the two signal pairs. Ordinary UART or RS-485 does not carry the camera's USB video. The small first build does not require a Fathom-X bridge. A longer, thinner tether requires a separately selected PHY/bridge and a new space/power budget; do not infer a range rating from this trial allocation.

A later surface buoy can bridge an above-water wireless link to the same underwater data tether. Underwater Wi-Fi/Bluetooth is not the control link.

## Propulsion and sensing

| Channel | Role | Positive force convention |
|---|---|---|
| H_LEFT | Left horizontal thruster | Forward, +X |
| H_RIGHT | Right horizontal thruster | Forward, +X |
| V_LEFT | Left vertical thruster | Up, +Z |
| V_RIGHT | Right vertical thruster | Up, +Z |

Forward/reverse uses the horizontal pair together; yaw uses differential horizontal force. Heave uses both vertical thrusters; differential vertical force controls roll. Sway and pitch are passive/coupled axes. Propeller handedness and ESC sign must be established by submerged calibration, not assumed from phase-wire colors.

Pressure gives depth relative to the water surface. It does not measure bottom clearance. An IMU supplies attitude/rates; if the selected IMU has no absolute heading reference, gyro-derived yaw drifts. A pressure sensor and ordinary IMU do not supply global position, ground speed or obstacle avoidance.

## Power and packaging

Start commissioning from a regulated **12.0 V source with an enforced 5 A aggregate ceiling**. The selected shore reference is KORAD KA3005P, operated at those reduced settings; source sink capability and ESC return-energy transients remain a separate verification gate. Begin one secured submerged motor at a 1 A source limit, with a provisional 3 A single-motor ceiling after observation. These are proposed commissioning bounds, not implemented current control or measured vehicle limits. [KORAD KA series](https://www.koradtechnology.com/product/83.html). A future mobile battery pack is an independent RFQ and fit gate; it is not included as an invented ready-to-use pack. The 50 mm-series, 150 mm reference enclosure has not been demonstrated to contain the PCB, Pi/hub, four ESCs, battery, connectors and complete harness. Nominal tube length is not usable payload length.

The proposed control-board outline is 80 × 32 mm on the existing tray's X = −40/20, Y = ±10 mm slots; the final machine-readable board contract records actual holes, height and placement. Board-only fit does not establish whole-system fit. Additional dry power/battery housing and its mounts would be new mechanical work. No externally mounted ESC or battery becomes pressure-rated by coating or heat-shrink.

## Required firmware behavior

- Command packets contain sequence, validity/range checks and a heartbeat. Proposed heartbeat 20–50 Hz; proposed stale-command threshold 0.5 s. These are design requirements pending implementation and bench verification.
- At boot/reset, outputs remain disabled until sensor/input checks and an explicit arm action. The actual ESC's neutral/arming dwell must be checked on the delivered revision.
- Loss of fresh operator commands clears old surge and descent commands. The required fallback, pending implementation and verification, is propulsion neutral/disable and passive ascent from measured slight positive buoyancy. Restoration of communication does not automatically rearm.
- The control loop runs independently of video and network activity, with a hardware watchdog. Depth PI plus vertical-rate damping, roll/heading feedback and bounded four-thruster allocation follow the simulator conventions, after real calibration.
- Log supply voltage, actuator commands, depth, attitude, leak state and command age. Low voltage, leak and controller faults require separately tested responses. A BMS trip is not the normal low-battery control strategy.

No firmware implementation, complete electrical fit, thermal verification, leakage test or sea trial is claimed by these documents. The selected X2 product is explicitly sold for freshwater. Sea use requires separate motor/material and corrosion review. [X2 source](https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters).

## Attitude and heading reference

The selected ICM-42688-P is a six-axis accelerometer/gyro, not an absolute-heading sensor. Gravity can support roll/pitch estimation; integrated gyro yaw drifts. The initial firmware can use gyro yaw-rate feedback and relative heading over bounded intervals after calibration. Long-term absolute heading hold requires a separately chosen and calibrated reference. Do not equate the simulator's noisy orientation proxy with a completed onboard estimator. No magnetometer, navigation estimator or vehicle firmware is currently implemented.

