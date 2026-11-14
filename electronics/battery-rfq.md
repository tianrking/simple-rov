# Mobile battery procurement specification

**RFQ only: no finished-pack part number, approved supplier or fitted battery assembly is released.** The first controller/motor commissioning stage uses the documented current-limited source. This specification makes the mobile-power hold concrete; it is not a direction to assemble loose cells.

## Candidate basis

Request a professionally assembled **4S1P LiFePO4** pack based on Lithium Werks **APR18650m1B, P/N 300949-001**, with cell interconnects, individual series monitoring, a protection/management circuit, insulation, a protected output and a compatible charging interface. The manufacturer's cell page lists 3.3 V / 1.2 Ah cells; cell data do not establish the complete pack's rating. [Manufacturer](https://lithiumwerks.com/products/lithium-ion-18650-cells/).

| Requested characteristic | Required supplier response |
|---|---|
| Series arrangement | Four cells in series; state exact cell revision and traceability |
| Charging target | 14.4 V for the referenced 3.6 V/cell charge target; supplier must confirm chemistry-specific CC/CV procedure, current and temperature range |
| Nominal energy reference | 4 × 3.3 V × 1.2 Ah = 15.84 Wh before discharge-rate, cutoff, reserve and aging effects; no endurance promise |
| Operating-voltage envelope | Full-charge voltage must not exceed the agreed X2/ESC limit; normal vehicle return/cutoff must occur before leaving the manufacturer-approved motor range |
| Current | Quote verified complete-pack continuous and timed peak ratings, including PCM, welds, output leads and connector; do not copy the cell rating into this field |
| Protection | Document overcharge, undervoltage, overcurrent, short-circuit and temperature behavior, trip/recovery thresholds and tolerances |
| Charging interface | Define how the selected charger connects without bypassing protection; specify whether balancing is internal or requires an external balance connector |
| Connectors | Supply exact source-side contact sex, pinout, wire gauge, insulation, lead lengths and dry connector ratings; exposed energized male contacts are unacceptable |
| Mechanical drawing | Provide maximum dimensions including PCM, insulation, lead exits, connectors and bend/service envelopes, plus mass and centre-of-mass reference |
| Records | Product test report, cell/pack handling instructions, transport documentation where applicable and replacement criteria |

A four-cell square arrangement has a theoretical circular envelope of approximately Ø44.9 mm using the maximum cell diameter from the research reference. This excludes separators, tabs, protection, insulation and cable bends. A **Ø48 × 105 mm maximum package can be requested as a feasibility target**, but is not a proven supplier capability or a fit allowance. The existing logic/video enclosure has no reserved battery volume. Do not insert this theoretical pack beside the controller and call the full system packaged.

## Power-envelope decision

The four motor supplier references sum to 28 A continuous and 60 A maximum before the host and logic. A 4S1P cell proposal must not be called a 60 A complete pack. If the quoted pack is lower rated, either establish and validate a lower operating envelope or select a different professionally engineered pack and revise the mechanical packaging.

The present controller has voltage sensing; **it does not measure aggregate propulsion current**. A firmware thrust/PWM limit is not measured current feedback. Any later current-limited mobile design needs a validated current-measurement/control arrangement, or independently proven electrical operating bounds and protection. Do not assume a fuse is a precise current regulator or that a BMS trip is an acceptable routine control strategy.

No direct 4S LiPo substitution is released: its 16.8 V full-charge value exceeds the X2 page's numerical 16 V listing. A 3S LiPo is listed as supported by the motor vendor, but operation below its numerical 12 V listing and the resulting thrust/current curve still need confirmation. [Power and voltage review](power.md).

## Mechanical and acceptance gates

1. Obtain a finished-pack drawing and complete power/charging ratings, rather than purchasing loose cells.
2. Place that exact pack, connector, protection and harness in CAD together with every installed module. If a separate pod is needed, design and check its mounts, axial retention, penetrators, guards and service paths explicitly.
3. Recalculate mass, displacement and CG/CB. Establish slightly positive unpowered submerged trim with the complete payload.
4. Test complete-pack current and voltage sag, temperature, cutoff and recovery in the actual dry housing. Validate ESC deceleration/reversal bus transients.
5. Record the approved pack MPN and revision in the system BOM and component-confirmation worksheet. Freeze charger/lead/fuse choices only against that approved pack.

Keep the RFQ status until these requirements are resolved. No battery-pod geometry, printed retaining parts or full-power mobile operating capability is included by implication.
