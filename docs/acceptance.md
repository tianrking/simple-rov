# Assembly interfaces and physical acceptance

[Step-by-step assembly](assembly.md) · [PDF](assembly.pdf)

Ten main prints and two separate fit coupons are provided. Commercial motor/propeller references are not printable project parts. Digital checks do not establish physical fit, load capacity, sealing or operating depth.

## Before printing the main parts

1. Confirm all four X2 hole types, the 14/8 mm cross orientation, usable blind depths, inferred 31 mm face offset and axial datums. Check the actual three-phase cable construction and sealing options; loose wires do not automatically seal in a single-cable gland.
2. Test H_mount_fit and V_mount_fit with one real thruster. Horizontal effective clamping plus washer is about 5 mm; M3 × 8 targets 3 mm engagement. Vertical wall plus washer is about 8.5 mm; M3 × 12 targets 3.5 mm. Change screw length or geometry when needed; do not bottom a screw.
3. Confirm the real electrical stack and service access before committing to the enclosure. Complete a board adapter and positive axial tray retention.
4. Slice PETG prints with at least six walls, 0.2 mm layers and solid load paths. Check orientation, local supports, warping, nut pockets and dimensional coupons. Printed M3/M2 clearances are nominally 3.4/2.2 mm.

## Assembly interfaces

| Module | Installation and inspection |
|---|---|
| Skids | Four M3 × 16 from above, top washers and side-loaded nuts. Install before horizontal motors; remove obstructing horizontal motors for skid service. |
| Vertical carriers | Four M3 × 20 per side, upward through the flange/chassis, washers both sides and nuts above. Two X-separated rows and ribs transmit the moment. Each motor uses four side-entering M3 × 12. |
| Horizontal motors | Four M3 × 8 and recessed washers per motor, from below; attach the OEM foot, never the rotor, shaft, propeller or thin duct. |
| Camera | Four M2 × 10, front washers and rear-pocket nuts. Rotate the board 180° for USB clearance. Two M3 × 12 with washers both sides attach the carrier to the tray. Assemble outside the tube. |
| Tray | Curved feet with closed-cell pads are provisional fit retention. Confirm pad compression and add positive axial retention; final module space, heat and shock retention are pending. |
| Enclosure | Follow the compatible supplier system. Align locking entry, tube cutout and six window holes. Use six OEM M2 × 0.4-10 screws without extra washers in the original stack. |
| Tube clamps / stops | About 1 mm EPDM liners; four M3 × 16 with washers both sides and nuts. Stop at the clamp hard stops. End slots contact metal flange projections with about 0.6 mm axial clearance, not the window or seal/locking surfaces. |
| Wiring / tether | Route away from propellers, flow paths and cover lips. Strain-relieve independently. Use the rear 6 mm eye for a separately engineered load path; its recovery rating is untested. |
| Fairing | Seat the locating lip and fit four M3 × 25 with washers both sides and nuts. Four 8 mm wells admit long hex tools. The cover is neither a pressure vessel nor a lifting handle. |
| Optional foam | Default: absent. If needed, fit two closed-cell blanks and four releasable straps; see [buoyancy](buoyancy.md). Remove optional foam before accessing cover screws. |
| Trim | Weigh the complete payload and measure displacement. Use the bottom M3 slots for engineered ballast. Establish appropriate CG/CB and near-level trim with the heave line near the real CG. |

[Fastener BOM](../bom/BOM_FASTENERS.csv) · [Bolt datums](../mechanical/bolt_locations.json). No common torque or thread-locking process is frozen. Respect supplier requirements and actual printed-joint tests; metal-joint torque assumptions do not apply to acrylic or FDM parts. Check chemical compatibility before using locking products.

## Completed digital checks

- Nominal printed-part / hardware / supplier interferences, supplier-to-supplier interference and optional strap paths.
- 48 screw-driver paths, evaluated in appropriate assembly states. These do not cover every wrench, finger or tool brand.
- Two D54 mm vertical corridors from Z = -140 to +120 mm: geometric clearance, not thrust or flow-efficiency validation.
- Sampled central/boundary camera rays at horizontal ±40° and vertical ±32°, without printed-part blockage. This is not full optical validation; refraction, distortion, lighting and the final USB cable are absent.
- Ten watertight, single-component print STLs and STEP volume/envelope readback; standard/optional assembly STEP envelopes and solid counts.

## Strength-screen limits

The vertical carrier uses an 8 mm main wall, two ribs and four foot connections. An ideal 32 × 8 mm solid section at 35 mm eccentricity under the supplier's 20.59 N maximum-thrust reference gives about 2.2 MPa nominal stress, or 6.6 MPa at three times that analysis load. Ribs are not credited. This is not FEA, a complete joint check or an established safety factor; hole/root stress concentration, wet anisotropy, creep, fatigue and impact are excluded.

Proposed physical gates, not yet performed:

1. Measure actual interfaces, gaps and blind depths on this print batch.
2. Using a rigid substitute fixture at the real thrust axis, load each mount in both directions at a provisional 41 N, hold five minutes and repeat three times. This is a project test proposal, not a certification standard. Record displacement, residual deformation, cracks, layer separation, nut-pocket damage and slip. Allowed displacement must be below half the actual minimum clearance.
3. Validate chassis, one-sided support, enclosure retention and tether eye against the eventual vehicle weight and simultaneous thrust combinations. No whole-vehicle payload or recovery rating is assigned.
4. Repeat critical retention/load checks wet, and inspect after repeated assembly, reversals and starts/stops. Short tests do not establish lifetime.
5. Leak-test the completed enclosure/penetrators using the supplier process, then perform recoverable shallow-water trim and low-thrust trials.

Without physical evidence, no rated depth, full-power endurance or service life is claimed.

Sources: [enclosure assembly](https://bluerobotics.com/learn/watertight-enclosure-wte-assembly-new/), [enclosure datasheet](https://bluerobotics.com/wp-content/uploads/2025/02/WTE-DATASHEET-RevC.2-FEB2025.pdf), [X2 product reference](https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters).
