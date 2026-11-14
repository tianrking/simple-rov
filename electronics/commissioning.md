# Hardware commissioning and acceptance

These are staged engineering checks for the first freshwater prototype. Record actual part revisions, photos, instrument readings, limits and source-file hashes. A digital PCB pass or an empty-enclosure leak test does not establish full vehicle reliability or depth rating. Initial powered water work is recoverable shallow freshwater operation; a proposed 2 m limit is a test scope, not a certified capability.

## 1. Inspection before power

Compare the delivered PCB, schematic, board BOM and connector contract. Check component values/polarity, module orientation, connector numbering, fuse values, crimp retention, strand clearance and insulation. Verify continuity pin by pin with the harness disconnected. Confirm no battery/12 V connection reaches a 5 V or 3.3 V pin, no BEC-positive outputs are paralleled, each TLP2361 receiver is powered only from its matching ESC BEC, and no motor return current is routed through signal connectors. Check mains-powered test equipment remains dry and properly isolated from the water test setup.

## 2. Logic rails and communications

Power logic from a current-limited source with ESC power disconnected. Check regulator input/output polarity, 5 V and 3.3 V at idle and under a representative load. Confirm no backfeed through USB, UART or an attached debugger. Record current, ripple, startup and brownout/reset behavior.

Bring up the Pi, its Ethernet/USB hub, supplied camera cable and topside link. Check stable compressed video while exchanging command/telemetry traffic. Confirm UART crossed TX/RX and 3.3 V levels, pressure address 0x76, pressure-sensor actual pin order, leak detection polarity and IMU axes. Set the surface pressure reference before interpreting depth. A depth sensor does not measure clearance above the pool floor.

## 3. Output and fault checks without a motor

Use an oscilloscope or logic analyzer to check each output channel, the buffered optocoupler chain and its normal noninverting pulse mapping, neutral timing, allowed pulse range and startup enable sequence. Missing pulses/fixed logic levels are not equivalent to 1500 µs neutral. Exercise missing, repeated, malformed, out-of-range and stale commands; unplug the network and UART separately; stop the host program; force MCU reset/watchdog and brownout conditions. Verify the specified safe output persists and reconnection does not automatically rearm. Four simulated or measured waveform checks do not prove the actual ESC will stop on missing pulses; that requires the next stage.

## 4. One submerged motor

Secure one manufacturer's matched motor/ESC in an appropriate submerged fixture and use an appropriate current-limited supply. Keep body parts, loose lines and foreign objects out of the propeller. Confirm the actual motor's required immersion/cooling conditions. For the isolated one-motor fixture, use 12.0 V input and an initial 1 A source limit, with a provisional 3 A single-motor ceiling only after observation. Keep the Pi/video load disconnected during that low-current fixture test or supply logic separately through its approved input; do not brown out the controller by applying a motor-only current budget to the full system. Start at neutral, then increase the command cautiously in both directions; return gently through neutral without abrupt reversal. Observe motor-bus voltage because an ordinary current-limited supply may not absorb returned motor energy. Record startup current, supply sag, neutral deadband, thrust sign, pulse frequency/input level, response lag and lost-signal behavior. Verify the actual ESC and its control isolation/ground arrangement; do not extrapolate from another revision.

## 5. Complete harness and mechanical mock-up

With propulsion disconnected, place real boards, ESCs, battery representative mass, holders, connectors and cables. Verify screw/tool access, wire bends, positive tray retention, removal sequence, strain relief and cable isolation from propellers. Update the wire cut sheet from measured routes. Confirm that every used port has a compatible feedthrough/seal and every unused port has a compatible plug. Do not force the closure or use seal friction to retain electronics.

## 6. Empty enclosure and trim

Leak-test the empty complete enclosure, with actual cables/penetrators/plugs, using the applicable supplier procedure. An electrical leak probe is additional monitoring, not a replacement for sealing. Repeat after connector, seal or cable changes. Soak with an unpowered moisture witness; inspect after cable flexing.

Install representative final mass without powering motors. Measure mass, displacement, level attitude and fully submerged net buoyancy. Adjust suitable depth-rated closed-cell foam and ballast so that the free vehicle is slightly positively buoyant. Verify unpowered ascent in a recoverable setting with the actual tether configuration. Flooding, entanglement or obstruction can still prevent recovery.

## 7. Four-channel low-power operation

Maintain the enforced 5 A aggregate source ceiling during the first four-channel trial. Test each channel independently to establish H_LEFT/H_RIGHT forward force and V_LEFT/V_RIGHT upward force. Confirm manual stop and command-loss stop, then enable depth control, then roll/heading stabilization with bounded commands. Validate low voltage and leak responses. Measure complete sealed-system temperatures, supply voltage/current and control/video stability during a representative duty cycle before increasing duration or load.

The main/branch fuse and conductor coordination requires manufacturer curves, measured startup/steady current and temperature derating. Never validate protection by directly shorting an unprotected battery. A battery BMS trip must not be used as a routine endurance limit.

## Acceptance record

| Record | Minimum evidence |
|---|---|
| Parts | Delivered MPNs/revisions, included cables and measured envelope/mass |
| Wiring | Signed continuity/polarity table, connector-face photos, fuse and wire specifications |
| Electrical | Rail startup/ripple/sag, current, neutral/direction/timeout waveforms and temperatures |
| Mechanical | Actual assembly/service photos, retained tray, cable clearance and strain relief |
| Sealing | Exact seal/cable arrangement, applicable procedure, dates and leak-test result |
| Water operation | Measured trim, unpowered ascent, low-power command/fault results and recovery method |

Onboard firmware and the topside control/video application must exist and pass these checks before the hardware can be described as remotely operable. The present simulator is an independent software demonstrator, not an MCU image.
