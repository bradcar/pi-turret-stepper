# pi-turret-stepper
Turret driven by stepper motor controlled by Pi Zero 2 W.

Turret can be used as a platter for rotating sensors. Sensors may be mounted to point inward or outward.

Scanning rotation example:
* for 6 seconds every 0.655°, a complete rotation would take 3,300 seconds (55 min, = (550 * 6)/60)

## References:
Detailed HW/SW Info: [stepper_motor_turret_specs.md](docs/stepper_motor_turret_specs.md)

### GitHub for Adafruit DC and Stepper Motor HAT for Raspberry Pi
* https://github.com/adafruit/Adafruit_CircuitPython_MotorKit

### Combined Turret (2.75:1) + Stepper (NEMA-17) Statistics
* **Turret Step Angle:** 0.655° per step (1.8° * 2.75)
* **Turret Revolution Steps:** 550 total steps (200 * 2.75)
* **Turret Output Speed:** 18.18 RPM
  * Steps per second: 18.18 RPM × 200 steps/revolution / 60 seconds = 60.6 steps/second
  * Time per single step: 1 second / 60.6 steps = 0.0165 seconds (16.5 ms)
* **Full Rotation Duration:** 3.3 secs
* **Estimated Angular Error:** 0.033° positional error

### Adafruit Stepper Motor (NEMA-17) 4-wire bipolar
* **Product Page:** [Adafruit Product 324](https://www.adafruit.com/product/324)
* **Overview Doc:** [Adafruit DC & Stepper Motor HAT for Raspberry Pi](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)
* **Rated Voltage & Current:** 12v  @ 350 mA
* **Step Angle:** 1.8° per step (5% angle accuracy)
* **Steps per Revolution:** 200
* **Speed:** 50 RPM
* **Holding Torque (per phase):**
  * 2 kg-cm (20 N-cm, 28 oz-in)
* **Drive Shaft:** 5 mm diameter, 24 mm long, with a machined flat

### goBILDA 169 Metal Turret
* **Product Page:** [Gear-Driven Turret (2.75:1 Ratio, 105mm ID)](https://www.gobilda.com/gear-driven-turret-2-75-1-ratio-105mm-id/)
* **Gear Reduction:** 2.75:1
* **Weight:** 438 g (with 64T Gear)

### Python
* **Software:** pip3 install adafruit-circuitpython-motorkit




