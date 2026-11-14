# From CAD to the first prototype

[Assembly guide](assembly.md) · [PDF](assembly.pdf) · [Acceptance](acceptance.md)

The initial target is a tethered, recoverable shallow freshwater-pool prototype. The standard 213 × 210 × 148 mm mechanical envelope omits top foam; the optional reference module raises height to 184.7 mm. Final electrical packaging, penetrators, mass and thermal behavior are not frozen. PCB fabrication is not part of this phase.

## Resolve two interfaces first

**Motor fit.** Buy one complete APISQUEEN X2 and a compatible bidirectional ESC. Confirm four hole types/depths, 14/8 cross orientation, inferred face offset, axial dimensions and cable construction. Pass the H/V coupons before buying the other three motors or printing all main parts.

**Dry payload.** The current 150 mm tube has been checked for the camera, lens and tray only. Obtain actual dimensions, connectors, wire-bend envelopes, mass, power and heat information for the battery, four ESCs, controller, regulator/distribution/protection and USB host. Build a full-scale bench layout and CAD assembly. Freeze the enclosure only when parts fit, plugs are serviceable, the battery is removable and thermal requirements are met. If necessary, revise the tube and clamps explicitly.

## System architecture

Surface computer/controller → tethered communications → underwater controller → four independent bidirectional ESCs → four thrusters.

Onboard power → accessible disconnect, main protection, distribution and branch protection → ESCs. Regulated supplies serve logic and camera. IMU supplies attitude; an appropriate pressure sensor supplies depth; leak sensing supports fault handling. The USB camera requires a USB-capable host, adding volume, power and heat.

For initial classical control, evaluate an established controller/firmware implementation and confirm its support for the actual SimpleROV-4 allocation, output protocol and bidirectional ESCs before selecting a board. Python simulation is not flashable firmware. Do not assume underwater Wi-Fi/radio is a working control/video link. Provide a separate tether load path; penetrators and conductors must not carry recovery tension.

## Procurement stages

| Stage | Quantity | Gate |
|---|---:|---|
| Complete X2 and matched bidirectional ESC | 1 each | Manufacturer confirms mounting, cable, voltage, current, protocol, neutral and setup |
| H/V printed fit coupons | 1 each | Measured engagement without bottoming |
| Compatible 50 mm / 150 mm enclosure kit | 1 set | Full electrical stack assessed; include seals, locks and plugs |
| Remaining motors / ESCs | 3 each | Single-motor mechanical, reverse-thrust and power checks passed; opposite-handed pair per axis |
| Prints, metal hardware, liners | Per mechanical BOM | Coupons and dry-payload assessment passed |
| Foam / straps | Optional | Measured displacement and trim |
| Battery, controller, host, power protection, tether and sensors | To select | Actual envelope, ratings, mass, protocols and compatibility |

The stored X2 reference lists 117 g each (468 g for four), 15 A maximum and 7 A continuous each. Four units imply nominal totals of 60/28 A before other loads, with conditions still needing measurement. The reference also lists 12-16 V and 3-4S LiPo; a fully charged 4S pack is 16.8 V, so obtain the manufacturer's allowable maximum rather than assuming compatibility. These are supplier reference values, not validated vehicle ratings. Use an appropriate current-limited bench supply and a secured submerged fixture according to motor requirements.

## Physical gates

1. **One motor, coupons and ESC:** documented fit, depth, direction, neutral, deadband and current.
2. **Complete payload mock-up:** fit, wire bends, connectors, battery access, CAD agreement, mass and thermal records.
3. **Print and dry assemble:** assembly/service access, load and wet-retention tests without unacceptable cracking, slip or residual deformation.
4. **Empty enclosure with real penetrators:** compatible supplier leak/vacuum procedure, unpowered shallow soak with a moisture indicator, and repeat after cable flexing or seal changes.
5. **Unpowered representative payload:** fully submerged trim, measured net buoyancy, near-level fore/aft attitude and recorded unpowered response.
6. **Low-power shallow-water operation:** verify each force direction, ascent/descent, yaw and depth hold; provide current limits, recovery and accessible power isolation.
7. **Post-run inspection:** leakage, fasteners, mounts, connectors, temperature and current before increasing duration or thrust.

The supplier vacuum guide describes approximately 15 inHg, a 10-15 minute observation and no more than 0.5 inHg loss for its applicable setup. Confirm applicability to the purchased complete enclosure and tool, and rule out tool leakage first. Vacuum and a shallow soak do not certify operating depth.

Weigh everything: battery, cables, penetrators, tether termination, fasteners and ballast. Freely flooded fairing volume is not sealed displacement. Simulation's 1.4 kg and 1% positive-buoyancy assumptions are not measurements.

## Control and calibration

Establish neutral, loss-of-command shutdown, thrust signs, IMU orientation and pressure calibration before classical depth/heading control. Feed measured mass, CG/CB, forward/reverse curves, deadband, lag and drag back into simulation. Tether disturbance requires its own model. Validate fault handling before powered shallow-water trials.

Reinforcement learning follows this baseline, with offline training and independent evaluation. An uncalibrated policy does not replace basic stabilization or failure handling.

Record results in [component-confirmation.csv](../bom/component-confirmation.csv). Sources: [X2](https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters), [enclosure assembly](https://bluerobotics.com/learn/watertight-enclosure-wte-assembly-new/), [vacuum procedure](https://bluerobotics.com/learn/using-the-vacuum-test-plug/), [ArduSub frame reference](https://ardupilot.org/sub/docs/sub-frames.html).
