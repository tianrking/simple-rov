# Wiring and port allocation

Read the delivered PCB connector table and schematic before assembly. The connector table below follows the delivered native PCB; functional CTRL names elsewhere are system endpoints. The canonical pin/net/position table is [CONTROLLER_PINOUT.csv](interfaces/CONTROLLER_PINOUT.csv). All views must state whether they show the mating face or wire-entry face; continuity testing is required regardless of wire color.

## Controller connector map

Pin numbers below are **PCB pad/cavity numbers**, not a left-to-right view of the cable's wire-entry side. Identify pin 1 from the board and the manufacturer's mating drawing, then continuity-test every cable before connecting power. All J1–J9 headers use the specified JST GH mating family; they are not interchangeable with JST PH, SH or generic 1.25 mm lookalikes.

| Board connector | Pins in numerical order | External connection |
|---|---|---|
| J1, 2-pin | 1 SYS5V; 2 GND | Regulated 5 V controller branch only; never 12 V and never the Pi power feed |
| J2, 3-pin | 1 GND; 2 controller TX; 3 controller RX | Pi physical 6 GND; physical 10 RX; physical 8 TX, respectively |
| J3, 3-pin | 1 H_LEFT BEC +5 V; 2 PWM; 3 matching ESC return | Left horizontal ESC control lead |
| J4, 3-pin | 1 H_RIGHT BEC +5 V; 2 PWM; 3 matching ESC return | Right horizontal ESC control lead |
| J5, 3-pin | 1 V_LEFT BEC +5 V; 2 PWM; 3 matching ESC return | Left vertical ESC control lead |
| J6, 3-pin | 1 V_RIGHT BEC +5 V; 2 PWM; 3 matching ESC return | Right vertical ESC control lead |
| J7, 4-pin | 1 regulated 3.3 V; 2 SCL; 3 SDA; 4 GND | Bar02 factory ordering; confirm the delivered mating cable |
| J8, 2-pin | 1 LEAK_LIMIT; 2 LEAK_RETURN | Replaceable two-contact dry-compartment leak probe; no external power |
| J9, 2-pin | 1 ARM_FEED (3.3 V through 330 Ω); 2 ARM_KEY | Internal removable service-enable key, installed/removed only with power off; software arming is still required |
| J10, solder pad | 1 positive voltage sense | Source-positive takeoff through the specified external 1 kΩ / ≥0.5 W resistor at the source; no motor current and no second sense-return wire |
| J11, Micro-B | Standard USB data/power interface | Shore service/programming cable; follow the board power-OR and boot instructions |

J3–J6 must use each ESC's matching BEC and return. Do not connect these BEC positives to J1 or join them together. J2 is a 3.3 V logic interface and must not be confused with the similarly sized ESC headers. The service key is a maintenance interlock, not an externally accessible emergency power disconnect.

The [controller harness mating-parts list](bom/CONTROLLER_HARNESS_PARTS.csv) separates cable-side housings/contacts from the headers already populated on the PCBA. Pin maps must be checked against the final native schematic and exported connector table before building the harness.

## Power paths

```text
12.0 V / 5 A limited source (future approved battery is a separate build)
  + --> nearby main fuse --> accessible disconnect --> positive junction
  - -----------------------------------------------> return junction
Positive junction --> branch fuse 1 --> ESC H_LEFT +
                  --> branch fuse 2 --> ESC H_RIGHT +
                  --> branch fuse 3 --> ESC V_LEFT +
                  --> branch fuse 4 --> ESC V_RIGHT +
                  --> logic fuse ----> Pololu VIN
Return junction   --> each ESC power - and Pololu GND
Pololu 5 V/GND     --> controller and Pi power input
Pi USB host/hub    --> camera USB power + data
```

Do not connect the main input to a controller 5 V connector. Before connecting electronics, verify actual polarity and voltage at each terminated branch. Use separate power-return paths for motor currents; implement the signal-reference/isolation arrangement exactly as the PCB design specifies. A silicone boot or dry XT connector is not a wet connector.

## Four propulsion channels

| System endpoint | Signal cable | Motor cable | Confirmation |
|---|---|---|---|
| CTRL.ESC_H_LEFT → ESC H_LEFT | PWM + that ESC’s BEC +5 V + reference return | U/V/W → left horizontal motor | Forward force is +X |
| CTRL.ESC_H_RIGHT → ESC H_RIGHT | PWM + that ESC’s BEC +5 V + reference return | U/V/W → right horizontal motor | Forward force is +X |
| CTRL.ESC_V_LEFT → ESC V_LEFT | PWM + that ESC’s BEC +5 V + reference return | U/V/W → left vertical motor | Up force is +Z |
| CTRL.ESC_V_RIGHT → ESC V_RIGHT | PWM + that ESC’s BEC +5 V + reference return | U/V/W → right vertical motor | Up force is +Z |

Each ESC has **two DC input conductors**, **three motor-phase conductors**, and a control lead arrangement. Three phase wires are not supply +, supply − and PWM. Mark channels at both cable ends. Use the manufacturer's matched bidirectional ESC revision; the [30 A reference](https://www.underwaterthruster.com/products/apisqueen-bi-directional-30a-esc-2-4s-5v-1a-bec-electronic-speed-controllers) describes 1000–2000 µs with 1500 µs neutral. Frequency, startup dwell, electrical input thresholds and loss-of-signal behavior still require confirmation on the delivered part.

The selected board has four **TLP2361 receiver stages**. Each stage is powered only by the matching ESC’s own **BEC +5 V** and its reference return. Keep each red BEC lead connected only to its own channel input; do not join red leads together or to the Pololu/Pi 5 V domain. Individually insulate any unused BEC-positive lead. Common battery-negative wiring may already connect ESC returns; this is signal-domain separation, not a claim of complete power isolation. The buffered optocoupler chain preserves the normal MCU pulse polarity. Verify pulse width and logic levels at the ESC-side connector before applying propulsion power. **Missing pulses or a fixed level is not a valid 1500 µs neutral command.** Actual ESC stopping after signal loss is unverified until tested. Follow the final J-number/pin map, and prove neutral/polarity with an oscilloscope before applying propulsion power.

## Intended output states

| Circuit condition | ESC-side signal, when that ESC's BEC is valid |
|---|---|
| Outputs enabled, MCU raw signal LOW | LOW |
| Outputs enabled, MCU raw signal HIGH | HIGH |
| Buffer disabled, controller supply valid | Static HIGH; no PWM frames |
| Controller 3.3 V absent | Static HIGH; no PWM frames |
| ESC-side BEC absent | Output level is not guaranteed |

These are circuit-intended states requiring waveform measurements. A static HIGH is not a 1500 µs neutral pulse, and this table is not evidence that an actual ESC stops after signal loss. Confirm that behavior on the exact delivered ESC before relying on the inhibit circuit.

## Video and command computer

- Supply Pi Zero 2 W from the regulated 5 V domain through its **PWR IN micro-USB** port with a properly terminated cable. The other micro-USB is the **USB OTG host/data** port. They have different roles.
- Connect the ETH/USB HUB HAT using its supplied Zero-compatible host interconnect. Inspect the exact HAT revision and avoid a second conflicting 5 V feed through USB/GPIO.
- Plug the camera's supplied JST-PH-to-USB cable into one downstream hub USB port. This carries 5 V, GND and USB D+/D−; do not substitute an unverified JST cable merely because its shell fits. The reference camera requires up to **220 mA at 5 V** and supplies compressed H.264 video. Rotate the received image 180° for the existing physical mounting orientation. [Camera](https://bluerobotics.com/store/sensors-cameras/cameras/cam-usb-low-light-r1/).
- Pi UART: physical **pin 8 / GPIO14 TX → MCU RX**, **pin 10 / GPIO15 RX ← MCU TX**, and **pin 6 GND → the specified MCU logic reference**. Both UART sides use 3.3 V logic; disable the Pi serial console and configure the intended hardware UART. This UART does not power either board. Never connect RS-232 voltage levels, battery voltage or 5 V TTL to these signals. [Pi documentation](https://www.raspberrypi.com/documentation/computers/zero.html).
- Connect the hub's RJ45 to the trial data tether and topside Ethernet adapter. Standard 100BASE-TX signal pairs use RJ45 pins **1/2** and **3/6**. Keep each differential pair together and use one consistent T568A or T568B termination at both ends. An unspecified thin tether is not automatically Ethernet-rated. No power is injected on spare pairs in this design.

## Pressure sensor — Bar02

The current [manufacturer pin map](https://bluerobotics.com/store/sensors-cameras/sensors/bar-depth-pressure-sensor/) is:

| Bar02 sensor mating circuit | Factory color | Signal | Controller connection |
|---:|---|---|---|
| 1 | Red | Vin | Selected regulated sensor supply; 3.3 V preferred for this system |
| 2 | Green | SCL | 3.3 V I²C clock |
| 3 | White | SDA | 3.3 V I²C data |
| 4 | Black | GND | Sensor/MCU logic reference |

This is **not** the common generic GND/VCC/SDA/SCL order. Confirm connector cavity numbering from the manufacturer's drawing before crimping. The sensor supports 2.5–5.5 V supply, while SCL/SDA must remain within 2.5–3.6 V logic; a 5 V supply does not permit 5 V pull-ups. Its fixed address is **0x76**. Use only one Bar02/Bar30 on a given un-multiplexed bus. Check existing pull-ups before adding more. Keep I²C wiring short and separated from motor phases.

Bar02 mounts through an **M10 × 1.5** bulkhead port. Its supplied nut/O-ring belong to that sensor, not to a generic cable gland. Its sensor pressure capability does not establish this vehicle's operating depth. Dry the sensing element for at least two hours daily and observe the maker's maximum continuous immersion limitation. [Guide](https://bluerobotics.com/learn/bar-sensors-guide/).

## Leak and IMU

Place a replaceable leak probe at the lowest dry-space location without shorting adjacent hardware. Route it to the defined low-energy detection input; bare water contacts must not be connected to battery voltage. A probe only at the top of the compartment may miss early leakage. At the remote probe end, connect one 1 MΩ ±1% EOL resistor (MAT-008) across the two electrodes. Fully insulate the resistor and its joints from water, leaving only the electrodes exposed. An absent EOL resistor makes a dry probe resemble an open lead. Verify dry, wet, disconnected and shorted readings before choosing firmware thresholds. The [board circuit analysis](pcb/docs/DESIGN_AND_QUALIFICATION.md) records initial uncalibrated threshold candidates.

Mount the IMU rigidly in the documented board axes. Record the board-to-vehicle rotation and verify roll/pitch/rate signs before closing the enclosure. If an external IMU board is selected, its voltage and connector order require a separate verified mapping; do not order both a board-mounted IMU and an external duplicate unintentionally.

## Rear port inventory and mechanical holds

The current rear reference has **one M10 and eight M6 ports**. Reserve the sole M10 for Bar02. No other M10 cable penetrator can simply be added to this drawing.

| Function | Proposed reservation | Status |
|---|---|---|
| Pressure sensor | 1 × M10 | Sensor reference selected; physical cap/interface fit pending |
| Four motor cable entries | 4 × M6 | Cable construction, actual bore and potting method unresolved |
| Ethernet entry | 1 × M6 | Exact cable OD/pair construction and entry method unresolved |
| Power entry from an approved separate module | 1–2 × M6 | Conductor gauge/bore/strain relief unresolved; no fitted battery module |
| Vent / unused positions | Remaining M6 positions | Exact vent/blank choice follows the approved complete port plan |

M6 **BR-100991** potted penetrators are a candidate for suitable 4–5 mm cable, not an approved solution for arbitrary bundles. A compression gland around three loose phase wires is not a demonstrated seal. Potting requires compatible cable/insulation/resin, controlled preparation, void control and an empty-system leak test. The Ethernet candidate must pass its bore while preserving pair geometry. Main power wire gauge may require separate penetrations or a revised endcap. Exact penetrator/plug counts remain **FIT_HOLD**, not zero required parts. [Penetrator specifications](https://bluerobotics.com/store/cables-connectors/penetrators/penetrator-vp/).

Provide mechanical strain relief tied to the chassis. The tether's recovery load must bypass seals, conductors and internal connectors. The existing 6 mm chassis eye has no established recovery load rating. No production cut length is issued until routing, plug service access and positive tray retention are verified.
