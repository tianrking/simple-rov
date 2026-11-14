# SimpleROV v0.0.1 — frozen fault chain and external sense resistor

The deliverable design.json is canonical. The two-contact J9 is an internal removable service enable cap/pigtail, installed or removed with propulsion power disconnected. Installing it permits arming; it does not arm. Closing the enclosure still requires a new explicit ARM_SET command. It is not an externally accessible emergency stop.

The earlier D6 diode clamp is deleted. U13 SN74LVC1G97DCKR, Schmitt inputs, implements Y=In2?In0:In1. Pin1 In1=GND, pin2 GND, pin3 In0=WDT_OK, pin4 Y=ARM_CLEAR_DRIVE, pin5 VCC=3V3, pin6 In2=ARM_KEY. Therefore Y=ARM_KEY AND WDT_OK. R14=1k feeds the 100nF C21 clear RC; R13=100k now pulls that RC to GND, not 3V3. R48=1k isolates the HCS74 CLR pin. U12 SN74HCS74PWR has CLR1 pin1, D1 pin2 tied high, CLK1 pin3=GP22 ARM_SET, PRE1 pin4 high, Q1 pin5=GP15 ARM_LATCH_Q, GND7 and VCC14. Unused second flip-flop inputs are tied; outputs NC. A released watchdog never sets Q. Key removal both removes the direct U10 enable permission and drives clear low. Key reinsertion never sets Q. D6 is absent from final PCB/BOM.

R49=330 ohm limits J9 feed; R11=2.2k returns ARM_KEY to GND. At 3.267V and 1% resistor corners, closed key >=2.833V before input leakage. Up to 2uA RP2040 plus 5uA U13 plus 5uA U10 input leakage reduces this by <3.5mV. Open key <=12uA*2.222k=26.7mV. There is no diode path from RC to key. R15=10k pulls WDT_OK high; 5uA U13+2uA RP leakage drops <=71mV. STWD100NXWY3F WDO low sinks <0.34mA at 3.333V, below its 1.2mA rated test condition. U13's clear low has at most 1uA HCS input loading, VOL<=0.1V (100uA test across 1.65–5.5V); after R14/R48 the CLR DC ceiling is <0.103V. Clear high is >=(3.267-.1)*100/101-0.002=3.134V with <=35uA load, using VOH>=VCC-.1 at 100uA. HCS74 data sheet only lists switching thresholds at 2/4.5/6V: no 3.3V interpolation is claimed. Rail-level drive supplies large margin; threshold/timing at actual board voltage still belongs in electrical qualification. U13 RC time constant is about 99us (1k//100k *100nF); allow >=1ms after valid key and watchdog before an ARM_SET edge. This is intentional RC into Schmitt HCS inputs, not a standard LVC input.

U10 Y=ARM_KEY AND ARM_LATCH_Q AND MCU_ENABLE. GP11 MCU_ENABLE and GP22 ARM_SET have hardware pull-downs. Firmware starts both low, configures neutral PWM, validates communication/sensors/key, waits >=1ms after fault-chain recovery, pulses GP22 low-high-low, verifies Q, then raises GP11. Any control fault immediately lowers GP11. WDI heartbeat occurs only after a complete valid control iteration, target 20ms; actual STWD100 timeout is 71–142ms, nominal102ms. Recovery requires a fresh software arming request. No firmware is supplied or tested here.

| Event | Q after event | MCU_ENABLE required | Buffer OE | ESC signal if its BEC is valid |
|---|---|---|---|---|
| Power-up, key absent or installed | held/initialized clear; verify on bench | 0 | 0 | static HIGH/no frames |
| Fresh ARM_SET, key and watchdog valid | 1 | 0 until checked, then1 | 0 then1 | raw MCU PWM, same polarity |
| Key removed | asynchronous clear after RC; direct OE permission removed immediately | software0 | 0 | static HIGH/no frames |
| Key replaced | 0 | 0 | 0 | static HIGH/no frames |
| WDT times out | 0 after clear RC | irrelevant to hardware clear | 0 after clear | static HIGH/no frames |
| WDT later releases | stays0 | 0 until fresh ARM_SET | 0 | static HIGH/no frames |
| MCU drops ENABLE without watchdog timeout | Q may remain1 | 0 | 0 | static HIGH/no frames |
| 3V3 off, ESC BEC on | logic unpowered | unavailable | unavailable; LEDs off | static HIGH/no frames |
| Corresponding BEC off | primary state irrelevant | any | any | unpowered; no valid output guarantee |

A command fault without watchdog timeout must invalidate firmware arming state and require a fresh ARM_SET workflow even though Q can remain1. Static HIGH is not a neutral pulse and is not a guaranteed motor stop. Missing-pulse stop behavior must be measured on each exact ESC revision before propulsion release. This is not a safety-rated system.

R26–29 are 10k 1%, not 100k. LVC126 IOZ max20uA over -40..125C gives <=0.202V cathode drop in high-Z, below TLP2361's recommended VF(off)<=0.8V. Active-low extra sink current is <=0.337mA per channel. R18–21 365ohm1% yield IF 2.487..5.903mA for 3.3V±1%, VOL<=.55V, engineering VF window1.2..1.8V. That VF window requires bench confirmation over the intended 0..50C enclosure range; it is not a full-temperature manufacturer guarantee. Recommended TLP IF is2..6mA. End-to-end PWM is non-inverting: buffer low lights LED, receiver output low; buffer high turns LED off, receiver high. No software polarity inversion.

## Positive-only voltage-sense wire

External harness item R_EXT: Yageo **MFR50SFBE52-1K**, 1k ohm, ±1%, 0.5W at <=70C, axial metal film, body6.3±.5 by diameter2.4±.2mm. Fit next to the positive bus takeoff and individually insulate both joints and the body. This is one sense wire to J10; controller power return supplies the reference. Do not add another battery-negative sense wire. A short downstream of this resistor is limited to <=16V/990ohm=16.17mA; max dissipation16²/990=.259W, below0.5W at <=70C. This does not protect an uninsulated takeoff before the resistor and does not approve 4S LiPo16.8V.

Board R42=147k±0.1%, R43=27k±0.1%; R44=1k is series into the high-impedance ADC and does not enter the DC ideal ratio. Let Rs be the installed measured source resistor and Vref the calibrated ADC supply:

`Vadc = Vbus*R43/(Rs+R42+R43)`

`Vbus = (ADC_code/4095)*Vref*(Rs+R42+R43)/R43`

For Rs=1k, ratio=27/175=.154285714; ideal Vadc(12V)=1.8514286V and Vadc(16V)=2.4685714V. The nominal 3.3V ideal ADC full-scale corresponds21.3889V; **the approved propulsion/sense input is still <=16V**, not21.39V. Allow ADC gain/offset, Vref, source1%, board0.1%, leakage and clamp errors in calibration. The ADC is not a calibrated battery monitor until two-point bench calibration. With board5V off and16V sense on, possible clamp injection is bounded about108uA by148k; rail discharge/backfeed must be measured. No claim of zero backfeed.

Primary sources: [TI SN74LVC1G97](https://www.ti.com/lit/ds/symlink/sn74lvc1g97.pdf), [TI HCS74](https://www.ti.com/lit/ds/symlink/sn74hcs74.pdf), [TI LVC126A](https://www.ti.com/lit/ds/symlink/sn74lvc126a.pdf), [ST watchdog](https://www.st.com/resource/en/datasheet/stwd100.pdf), [Yageo MFR ordering/dimensions/derating](https://yageogroup.com/content/Resource%20Library/Datasheet/YAGEO-MFR_DATASHEET.pdf).
