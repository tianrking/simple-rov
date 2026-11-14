# Controller electrical review

Review date: 2026-11-14. Scope: the RP2040 controller topology, manufacturer pin assignments, reset/enable logic, optical outputs and source/schematic/PCB agreement. This is an independent file/design review. It does not establish powered behavior, EMI, thermal performance, actual ESC stopping or water reliability.

## Checked interfaces

- RP2040 supply domains, internal 1.1 V regulator, TESTEN, USB series resistors, boot/reset and QSPI connections; ABM8-272-T3 reference crystal and 15 pF load capacitors.
- W25Q16JVSNIQ ordering code with the narrow 150 mil SOIC-8 footprint.
- ICM-42688-P SPI, supply and reserved-pin assignments.
- STWD100NXWY3F physical pin 1 WDO and pin 4 WDI.
- SN74LVC1G97 pin/function mapping: In1=GND, In0=WDT_OK, In2=ARM_KEY, so Y=ARM_KEY AND WDT_OK.
- SN74HCS74 asynchronous clear, arm-clock/Q and fixed unused-half inputs. Its Schmitt inputs accept the intentional clear RC edge.
- Separate per-ESC BEC supply nets, buffered LED cathode drive, and the disabled-state pull-ups.
- USB/external supply Schottky-OR direction, voltage-sense divider/clamp and the required source-side sense resistor.

The reset driver actively discharges the clear network when the service key or watchdog permission is absent. Restoring either permission releases clear but does not set the latch: a new ARM_SET rising edge is required. The software enable remains a separate permission. These statements assume valid supply levels and settled propagation; the design is not safety rated.

The four channels preserve normal MCU pulse polarity. With valid ESC-side BEC, disabled or settled unpowered logic produces static HIGH/no frames. This is **not** a 1500 µs neutral pulse. Actual ESC signal-loss stopping is a mandatory commissioning test.

## LED-current boundary

The 365 Ω / 1% sink-drive selection was checked against the 25°C TLP2361 forward-voltage boundaries, regulator accuracy and conservative LVC126 sink loss. At 2 mA, the worst required voltage is 3.1873 V, below the assumed regulated minimum 3.2505 V. At 6 mA, the minimum required voltage is 3.5181 V, above the assumed maximum 3.3495 V. This supports a 2–6 mA design interval at the stated condition; it is not a full-temperature measurement or guarantee. The 10 kΩ pull-up limits a 20 µA disabled-buffer leakage deficit to approximately 0.2 V.

## Evidence and next checks

[INTEGRATION_CHECKS.json](INTEGRATION_CHECKS.json) records native PCB pad checks, exported schematic-netlist agreement, connector/mount/BOM consistency, source fingerprints and the separately generated native ERC/DRC results. [Fault-chain and sense analysis](../pcb/docs/FAULT_CHAIN_AND_SENSE.md) contains the device-corner assumptions and rearm state table. The native engineering files remain the source for the final routed design.

Manufacturer references: [RP2040](https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf), [ST watchdog](https://www.st.com/resource/en/datasheet/stwd100.pdf), [TI configurable gate](https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf), [TI HCS74](https://www.ti.com/lit/ds/symlink/sn74hcs74.pdf), [TI LVC126A](https://www.ti.com/lit/ds/symlink/sn74lvc126a.pdf), [Toshiba TLP2361](https://toshiba.semicon-storage.com/eu/semiconductor/product/optoelectronics/detail.TLP2361.html).
