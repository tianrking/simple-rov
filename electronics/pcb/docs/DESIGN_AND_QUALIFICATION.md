# SimpleROV v0.0.1 controller

Engineering prototype for the current four-X2 vehicle. This board carries control/sensor signals and its own fused5V branch. Motor current, Pi power distribution, the external5V converter, ESCs, tether hardware and battery are outside this PCB. No battery-fit or complete electronics-bay-fit claim is made. Initial system commissioning remains regulated12V with an enforced5A total limit; begin with one motor at1A, then the separately agreed provisional3A single-motor limit.

## Circuit

U1 is bare RP2040 QFN56 with2MiB W25Q16JVSNIQ flash. The SN 150mil package matches the3.9x4.9mm SOIC footprint; SS 208mil is not interchangeable. The12MHz ABM8-272-T3 oscillator uses1k XOUT damping and two15pF C0G capacitors. BOOT and RESET are service buttons. J11 is full-speed12Mbps USB service only, with27ohm series data resistors, USBLC6 ESD and Schottky power ORing. The USB power input cannot feed the external5V source through D1. No host-powered motor operation is authorized. Disconnect propulsion for service and keep the key removed.

J1 receives regulated5V, through0467.500NR500mA fuse and SS14 to the TLV75533PDBVR3.3V LDO. USB5V is the alternative OR input. Input to the LDO must remain within5.5V. The board engineering3.3V load budget is150mA: MCU/core regulator, flash, IMU, logic, sensor and four optocoupler LEDs; measure actual current with the target firmware. Expected LDO dissipation is about0.20W at4.6V in/150mA out. A500mA regulator rating is not approval for continuous500mA in the sealed enclosure. Use the external Pololu D24V50F5 for the independently sized Pi/system supply. Do not route Pi, camera or motor current through J1 or this PCB.

U3 ICM-42688-P uses SPI on GP16..20. Its3x2.5mm,14-pad package and top-view pin numbering were checked against TDK DS-000347 package drawing. Sensor+X/+Y/+Z are derived to match vehicle forward/left/up at the documented zero-degree footprint orientation; physical six-face/sign testing remains required. All purchased parts are top-side. Six unpopulated copper test pads on the back are SWDIO,SWCLK,GND,3V3,RUN and arm-latch Q; debug with the PCB removed from its tray.

J7 powers Bar02 at3.3V through10ohm and uses4.7k I2C pullups plus33ohm series resistors. Start at100kHz; its factory GH4 sequence is1Vin(red),2SCL(green),3SDA(white),4GND(black), address0x76. This is not the Qwiic pin sequence. UART J2 uses3.3V logic:pin1GND,pin2MCU_TX,pin3MCU_RX; cross TX/RX to the Pi. It carries no5V supply.

U5..8 TLP2361 each have a separate receiver supply from the corresponding ESC5V BEC. Their four receiver grounds and BEC positives are separate from each other and controller GND on the PCB. Common battery-negative connections elsewhere can remove system-level galvanic separation. This is per-channel signal decoupling, not complete vehicle galvanic isolation. Each BEC must be checked for the TLP2.7..5.5V operating range, including ripple/transients. A no-BEC ESC cannot be substituted without changing the system interface. Toshiba's exact orderable string is `TLP2361(TPL,E` without a closing parenthesis, as printed in the manufacturer's order table.

The LVC126 buffer sinks the optocoupler LED through365ohm1%;10k1% output pullups keep the LEDs off when disabled. End-to-end PWM is non-inverting. GP6/7/8/9 respectively drive J3HL/J4HR/J5VL/J6VR. Receiver outputs go through100ohm series resistors. When inhibited and its BEC is valid, an ESC sees static HIGH/no frames. It does not receive1500us neutral. An unpowered BEC has no valid output guarantee. The exact ESC revision's missing-pulse stop behavior is a release gate.

See FAULT_CHAIN_AND_SENSE.md for the active clear gate, latched arming truth table, electrical corners and positive-only battery-sense source resistor. J9 is an internal removable enable cap installed with propulsion power off. It is not an outside emergency stop. A key installed at startup only permits a later explicit software arm request. Watchdog timeout or key removal clears Q; recovery alone cannot set Q. Firmware is not delivered, compiled, flashed or physically tested in this package.

The leak probe uses two corrosion-resistant exposed electrodes on an insulating mount, with a1Mohm1% end-of-line resistor at the remote probe, electrically across the contacts and with resistor/joints insulated from water. Board3.3k series resistance on both probe wires limits wet/short current. Ideal dry ratio is1006.6/1106.6=0.90963, wet short6.6/106.6=0.06191, and an open lead is near1.0. Initial candidate thresholds are dry0.89..0.93, wet<0.85, open>0.975. These are bench starting values; water conductivity and contamination are not characterized. Confirm open-wire, short and real-water responses before relying on the alarm.

## Fabrication and assembly

80x32x1.6mm FR4, four copper layers F/In1/In2/B. Quote the actual0.10mm minimum track width,0.127mm minimum electrical clearance,0.30mm minimum via drill/0.60mm via diameter, and the QFN0.4mm pitch/LGA pads. Request electrical net test, lead-free finish and fabricator DFM before fabrication. No controlled-impedance stackup or USB compliance certification is claimed. The routed board uses197vias; the exact critical-net lengths/via counts are in verification/ROUTING_METRICS.json. Start firmware commissioning with conservative flash clock division, e.g. <=31.25MHz at125MHz system clock, and verify boot/USB waveforms and repeated resets. Oscillator startup and USB enumeration are physical qualification items, not conclusions from DRC.

Four3.2mm NPTH holes keep copper at least3.7mm from their centers; component courtyards reserve4.5mm for the M3 hardware/tool envelope. These are unplated mounting holes. Use the final system mechanical contract for insulating spacer length, washers and M3 retention hardware; the board world-bottom datum remains13mm. The tray-slot top/bottom and fastener stack must follow that latest contract. Inspect all copper layers and screw hardware clearance. Backside debug pads are bare copper, not bottom components. USB tab geometry uses a conservative envelope with about0.805mm underside projection; measure the supplied connector and solder before accepting the1mm underside allowance.

The Gerber folder and separate PTH/NPTH Excellon files are native exports from the checked PCB. CPL_top.csv uses KiCad absolute placement origin with X right/Y up (native KiCad Y is inverted). Inspect manufacturer component zero rotations before assembly. The mixed SMT/PTH USB connector is deliberately excluded by the SMT-only pick-and-place export; hand-place/reflow it according to the assembly drawing, then solder its retention tabs. J10 and TP1..6 are bare copper features and excluded from purchase BOM. Pin1 markers and pad shapes are retained in the footprint drawings. Front identifiers are1mm where space permits; detailed connector functions and pin legend are on the back and in CONNECTOR_PINOUT.csv. Do not identify the identical GH3 housings by cable color alone.

## Electrical qualification record to complete on the first assembly

| Stage | Setup and required observations | Current result |
|---|---|---|
| Unpowered inspection | AOI/microscope QFN/LGA/flash orientation, solder bridges,3V3/GND resistance, all four BEC domains separate on PCB, source resistor at bus takeoff | Not performed |
| Board supply | Propulsion disconnected, key out,5V input current limited initially0.25A; record5V/3.3V/1.1V, startup/no overshoot, USB/external OR and backfeed behavior | Not performed |
| Programming/boot | Read SWD ID, test BOOTSEL/USB, flash exact W25Q16-compatible boot2,100cold boots/reset cycles, measure12MHz startup and USB signaling | No firmware supplied |
| Sensors | Verify IMU WHO_AM_I/signs/six-face calibration, Bar02 identity/0x76/depth datum, UART TX/RX, leak dry/wet/open/short | Not performed |
| Arm supervision | Scope MCU_ENABLE,ARM_CLEAR_DRIVE,CLR,Q,all buffer OEs and powered ESC PWM; test key absent/startup/key removal/reinsertion, heartbeat stop and watchdog recovery without ARM_SET | Not performed |
| Output stages | Separate5V sources emulate each BEC; prove no onboard BEC paralleling, measure2..6mA LED current over target0..50C and all receiver high/low/pulse widths; verify static HIGH on inhibit | Not performed |
| Voltage sense | Apply calibrated0/12/16V via the actual external1k; record ADC gain/offset/reference; test16V sense with5V off for rail injection, no unintended operation and source-resistor temperature | Not performed |
| Exact ESC | With a safe motor/propeller setup, establish neutral pulse and explicitly measure startup, missing-pulse, watchdog, UART loss,5V loss and BEC loss behavior; never infer stop from HIGH/no frames | Not performed |
| Enclosure/system | Mated plugs, wire bends, USB service access, sensor wires, tray retention, Pi/hub/camera/ESC fit,12V/5A staged commissioning, thermal soak, EMC and waterproof tests | System integration open |

## Primary references

- Raspberry Pi: https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf
- TDK: https://product.tdk.com/system/files/dam/doc/product/sensor/mortion-inertial/imu/data_sheet/ds-000347-icm-42688-p-v1.6.pdf ; package/axes checked with the TDK-authored v1.2 drawing mirrored at https://media.digikey.com/pdf/Data%20Sheets/TDK%20PDFs/ICM-42688-P_DS_Rev1.2.pdf
- TI: https://www.ti.com/lit/ds/symlink/tlv755p.pdf ; https://www.ti.com/lit/ds/symlink/sn74lvc126a.pdf ; https://www.ti.com/lit/ds/symlink/sn74hcs74.pdf ; https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf
- ST: https://www.st.com/resource/en/datasheet/stwd100.pdf
- Toshiba: https://toshiba.semicon-storage.com/eu/semiconductor/product/optoelectronics/detail.TLP2361.html
- JST: https://www.jst.com/wp-content/uploads/2025/06/eGH.pdf ; contacts AWG30..26, insulation OD0.76..1.0mm
- Blue Robotics: https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/

Original SimpleROV design, layout, documentation and scripts:All rights reserved. KiCad library subsets/derived footprints retain the separate upstream license in controller/third_party.
