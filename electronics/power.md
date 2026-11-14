# Power selection and budget

## First commissioning configuration

Use **KORAD KA3005P** as the shore-supply reference, set to **12.0 V DC with a physically enforced 5 A total current ceiling**, a fused input harness and a secured submerged motor fixture. Begin with logic/video only. For the isolated one-motor fixture, disconnect Pi/video or supply logic separately through its approved input before applying the motor-only initial 1 A source limit; a provisional 3 A single-motor ceiling follows observation. Do not apply that motor-only budget to a loaded Pi/video rail. Four-channel low-power operation is later under the same 5 A aggregate source limit. These are engineering test bounds, not firmware-enforced current limits. [KORAD KA series](https://www.koradtechnology.com/product/83.html). A final shore cable voltage-drop/ampacity calculation is required before extending bench power to a shallow-water rig. The data tether is not assumed to deliver motor power or PoE.

The first-stage main harness uses a **7.5 A ATOF 0287075.L** fuse and an appropriate holder; its fuse rating does not replace the 5 A source limit. Use a separate **3 A ATOF 0287003.L** logic-input fuse, subject to actual regulator inrush review. Larger 40 A main-fuse/10 AWG examples below are future battery-system candidates, not permission to exceed first-stage limits.

A normal bench supply may not absorb motor/ESC return energy. Measure motor-bus voltage during slow deceleration and neutral transitions with suitable instruments and protection. Until the source/ESC combination is qualified, prohibit abrupt direction reversal and full-power bench operation. A series diode alone does not dissipate energy left on the motor bus. [TDK motor-load guidance](https://product.tdk.com/en/contact/faq/power-supplies-0025.html).

This plan does not ask the small controller PCB to distribute propulsion power. Logic and ESC branches leave a protected power junction separately; motor return current stays out of MCU/sensor traces. Keyed dry connectors do not provide polarity reversal protection by themselves.

## Reference electrical load cases

| Load | Budget / reference | Meaning |
|---|---|---|
| Four X2 motors | 4 × 7 A = 28 A continuous; 4 × 15 A = 60 A maximum | Supplier-reference sums, not measured simultaneous vehicle current |
| Pi Zero 2 W supply branch | 5 V / 2.5 A supply capacity | Supply sizing allowance, not measured consumption |
| Camera BR-100126 | 5 V / 0.220 A maximum | USB downstream load; avoid counting twice if included in host supply allowance |
| Control PCB, IMU, depth and leak input | Reserve 5 V / 0.3 A pending board measurements | Engineering allocation, not a component rating |
| Ethernet/USB hub | Reserve 5 V / 0.5 A pending measurement | Engineering allocation; USB downstream loads listed separately |
| Combined logic rail | Initial 5 V / 3.5 A design allowance, then measure | Host allowance conservatively includes some USB load; no endurance claim |

[X2](https://www.underwaterthruster.com/products/apisqueen-12-16v-2-1kg-thrust-84w-x2-freshwater-brushless-dc-waterproof-thrusters) · [Pi product brief](https://pip-assets.raspberrypi.com/categories/584-raspberry-pi-zero-2-w/documents/RP-008359-DS-1-raspberry-pi-zero-2-w-product-brief.pdf) · [Camera](https://bluerobotics.com/store/sensors-cameras/cameras/cam-usb-low-light-r1/).

At 12 V, 17.5 W of logic at an illustrative 85% converter efficiency would draw about 1.72 A. Thus the reference continuous source case approaches 30 A before margin. This is a sizing example; converter loss and sealed-tube temperature must be measured. Full 60 A motor demand is not authorized by a 40 A fuse or by this prototype plan.

## Independent 5 V supply

Selected reference: **Pololu D24V50F5, item 2851**, 17.8 × 20.3 × 8.8 mm, fixed 5 V, 6–38 V input and typical maximum 5 A dependent on input/cooling. Its reverse-input, short-circuit and thermal protection apply to the module, not the full motor bus. Feed it through its own protected branch. Full advertised output inside the small dry tube remains unverified. [Manufacturer](https://www.pololu.com/product/2851).

The selected control board uses **four TLP2361 receiver stages, each powered only by its corresponding ESC’s own 5 V BEC**. For every channel connect that ESC’s BEC positive, its reference return and its signal to the matching channel connector, exactly as the final pin map specifies. **Do not remove all four red BEC leads for this board.** Each BEC feeds only its own receiver side; never join BEC-positive nets together or connect them to the Pololu/Pi 5 V rail. Unused BEC-positive terminals are individually capped. Common motor-battery negatives can connect the ESC returns, so the optocouplers do not establish complete system power isolation. The input buffer drives the optocoupler LED cathode, so the complete channel preserves the normal MCU pulse polarity; verify the waveform at the ESC connector. No pulses or a fixed logic level is not the same as a valid 1500 µs neutral pulse. Actual lost-signal stopping remains an ESC test gate.

## Fuses, conductors and connectors

| Function | Candidate | Quantity installed | Review boundary |
|---|---|---:|---|
| Main dry mating pair | AMASS XT90S-F / XT90S-M | 1 pair | Manufacturer lists 45 A under its 10 AWG test condition; name is not a 90 A continuous rating |
| ESC branch mating pairs | AMASS XT60H-F / XT60H-M | 4 pairs | Manufacturer lists 35 A under its 12 AWG test condition; factory connectors may replace this purchase |
| First-stage main fuse | Littelfuse 0287075.L, 7.5 A ATOF + FHAC0001ZXJ holder | 1 | Used with enforced 5 A source limit; inrush/temperature coordination pending |
| Future battery main fuse | Littelfuse 0498040.TXN, 40 A MIDI | 0 first-stage / 1 future candidate | Not installed in parallel or substituted into the first-stage limited rig |
| Future battery main holder | Littelfuse 04980921GXM5 | 0 first-stage / 1 future candidate | Full holder/lug/cover envelope not fitted in the small tube |
| ESC branch fuse | Littelfuse 0287015.L, 15 A ATOF | 4 | Check actual startup/stall, wire size and temperature |
| ESC branch holder | Littelfuse FHAC0001ZXJ | 4 | 20 A / 32 V holder, 16 AWG leads; not a pressure enclosure |
| Logic branch fuse | Littelfuse 0287003.L, 3 A ATOF + matched holder | 1 | Verify regulator inrush/current and holder/gauge coordination |

For the short, enforced-5-A first-stage rig, use a properly terminated 16 AWG copper main harness coordinated with its holder and 7.5 A fuse. The larger future battery-system allocation is 10 AWG copper, subject to its own thermal/fault review. Retain factory 14 AWG ESC power leads where possible. Any thinner inserted conductor, holder lead, crimp or contact changes the branch rating. Gauge alone does not establish allowed current in a bundle or sealed tube. Connect source-side recessed female metal contacts to the power source, verify molded polarity, and insulate all solder cups. A fuse does not limit every transient to its printed current; coordinate the actual manufacturer's time-current curve and ambient derating with the weakest protected conductor/contact.

[XT90S](https://www.china-amass.net/xt90s-f-product/) · [XT60H](https://www.china-amass.net/xt60h-f-product/) · [MIDI](https://www.littelfuse.com/assetdocs/littelfuse_automotive_bolt_down_fuse_midi_32v?assetguid=b55e8034-180d-40f6-a0a7-bebc2d4a94f5) · [ATOF](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40) · [Branch holder drawing](https://www.littelfuse.com/assetdocs/fhac0001zxj-2d-print?assetguid=3959eb51-0df1-4ffd-a2a6-c64b8e165c85).

## Mobile battery RFQ

The motor page lists **12–16 V** and **3–4S LiPo**. A 3S LiPo is 12.6 V full / 11.1 V nominal; 4S is 16.8 V full. The numerical boundary is unresolved. Do not directly connect a fully charged 4S LiPo to X2 on the basis of the cell-count label. A listed 3S pack is a prototype candidate, but thrust/current below the stated 12 V must be confirmed. [Manufacturer battery guide](https://www.underwaterthruster.com/blogs/knowledge/how-to-choose-the-right-battery-and-esc-for-an-underwater-thruster-complete-guide-to-voltage-current-and-battery-capacity).

The compact professional-pack RFQ direction is **4S1P LiFePO4 using Lithium Werks APR18650m1B, P/N 300949-001**, nominal 3.3 V / 1.2 Ah cells. The maker recommends 3.6 V charging per cell, giving a 14.4 V pack charge target. Cell-level 30 A continuous / 50 A ten-second figures do not establish an assembled pack's ratings. Request a professionally assembled pack with documented PCM/BMS behavior, fuse, insulation, strain relief, temperature sensing, charge/balance arrangement, connector, dimensions, mass and transport documentation. Do not buy loose cells expecting a user-ready protected pack. [Cell maker](https://lithiumwerks.com/products/lithium-ion-18650-cells/).

RFQ operating target: support the supplier-derived approximately 30 A continuous sizing case, subject to measurement with temperature margin, and a documented bounded transient case; stop propulsion before motor-voltage or cell limits are crossed. The cell's own lower-voltage allowance is not the motor's operating limit. Four cells have a theoretical circular packing envelope around 44.9 mm before insulation/BMS/wires; this is not proof of fit in a 50 mm-class bore, nor of coexistence with the electronics.

A specific 3S size reference is Tattu **TA-75C-1800-3S1P-XT60**, 105 × 35 × 19.3 mm / 159 g / 1800 mAh from the [official catalogue](https://www.genstattu.com/content/instock/rc_product_brochure.pdf). It is not a frozen compatible battery or a demonstrated fitted part. Capacity and a printed C-rate do not replace assembled-pack thermal/current testing.

Charging is done ashore with the pack disconnected from propulsion, using its specified chemistry, cell count, voltage and balancing/protection method. **SkyRC B6neo SK-100198** is a selectable charger reference supporting LiFe/LiPo; its input power supply and exact main/balance leads are separate BOM items. An internal-BMS pack may require a different maker-approved charge connection. [Charger](https://www.skyrc.com/b6neo-series).
