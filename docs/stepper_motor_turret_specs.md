# Combined Turret & Stepper Motor Assembly
## 1. Combined Stepper + Turret Specifications

Resolution & Step Angle
* **Turret Step Angle:** 0.655° per step (standard Step 1.8° / 2.75)
* **Turret Revolution:** 
  * 550 steps Full Step (200 * 2.75)
  * 1,100 steps Half Step (400 * 2.75)
  * 8,800 steps MicroSteps (16 * 200 * 2.75)

Output Speed (200 Steps)
* **Turret Output Speed:** 18.18 RPM (50 RPM / 2.75)
* **Time for Full Rotation:** 3.3 seconds

Ideal Holding Torque
* **Metric:** 5.5 kg-cm (2 kg-cm * 2.75)
* **Metric (Newtons):** 55 N-cm (20 N-cm * 2.75)
* **Imperial:** 77 oz-in (28 oz-in * 2.75)

Realistic Holding Torque (~85% efficiency)
* 4.7 kg-cm
* 65.5 oz-in

Mechanical Loading & Edge Forces
* **Bending Moment (M):** 560 N-mm = 28N * 20mm *(based on stepper rating of 28N at 20mm from the flange)*
* **Turret Geometry:** 128mm diameter (64mm radius)
* **Force at Turret Edge (64mm:** 8.75N = 560 N-mm / 64mm (~1.97 Lbs)
* **Safety Factor at Edge (50% to 75%):** 4.4 to 6.5N (~1 Lbs)

Precision, Accuracy & Backlash
* **Estimated Angular Error:** 0.033° positional error at the turret output
* **Backlash:**
  * On metal turret reductions, mechanical backlash (interplay between gear teeth) can dominate real-world positioning accuracy when reversing direction
  * Even if the motor steps precisely, the turret may exhibit a small deadband of free movement before gears engage in the opposite direction, unless anti-backlash gears or preload mechanisms are used

## 2. Adafruit Stepper Motor 4-wire bipolar (NEMA-17, pid 324)
* **Rated Voltage:** 12V
* **Max Current:** 350mA

### Physical & Mechanical Specifications
* **Body Size:** 42mm / 1.65" square body
* **Mounting Holes:** 31mm / 1.22" square pattern, 3mm metric screws (M3)
* **Drive Shaft:** 5mm diameter, 24mm long, with a machined flat
* **Step Angle:** 1.8° per step (5% angle accuracy)
* **Steps per Revolution:** 200 steps
* **Speed:** 50 RPM
* **Holding Torque (per phase):** 
  * 28 oz-in
  * 20 N-cm
  * 2 kg-cm
* **Operating temp:**  Measured 60°C - Stepper motors are designed to run hot due to continuously holding current even when stationary
* **Heat Sinks:**  Most effective on bottom. but sides also good if bottom not accessible
  * Aluminum Heat Sink 40x40x20mm with thermal conductive adhesive tape
  * Thermal paste is used between 1700 Series stepper mount and top of stepper. Turret frame may remmove some heat (open question how much?)

### Links & Documentation
* **Product Page:** [Adafruit Product 324](https://www.adafruit.com/product/324)
* **Overview Doc:** [Adafruit DC & Stepper Motor HAT for Raspberry Pi](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)


## 3. goBILDA 169 Metal Turret (3208-0004-0001)
* **Product Page:** [Gear-Driven Turret (2.75:1 Ratio, 105mm ID)](https://www.gobilda.com/gear-driven-turret-2-75-1-ratio-105mm-id/)
* **Gear Reduction:** 2.75:1 ratio (Gears MOD 0.8)
* **Weight:** 438g (with 64T Gear)
* **Adaptors:**: 
  * 1700 Series Stepper Mount (NEMA-17)
    * Adding thermal paste between top stepper & mount so that the frame can also be heat sink.
  * 1314 Series Set-Screw Hub (5mm bore)
  * 1120 Series U-Channel (8 Hole, 216mm)
  * 140 Series Aluminum Baseplate (6mm, 144mm diameter)
  * Plastic Hub-Mount Disc (240mm diameter)

## 4. Optical encoder [TODO ...Explore this more]
Optical encoder connected to 30-Tooth Encoder Pinion Gear
* **Encoder Product (DigiKey):** Bourns EM14R0D-R20-L064S optical encoder
* **Product page:** https://www.digikey.com/en/products/detail/bourns-inc/EM14R0D-R20-L064S/2538006
  * Optical Quadrature Encoder Specifications
    * Encoder Resolution: 64 PPR (Pulses Per Revolution)
    * Quadrature Decoding: 256 Counts Per Revolution (CPR) Generates 4x counts per pulse (leading/trailing edges of both channels).
    * 120 Max RPM
    * No Detent (1M cycles)
  * 6mm D-shaft (flatten end)
  * 5v - need buck converter and level shifter to work with Pi 3v3
* **30-Tooth Encoder Pinion Gear (goBilda):** 2303 Series Steel, MOD 0.8 Pinion Gear (6mm D-Bore, 30 tooth)
  * High confidence for missed Step Detection gives 2.73 counts per full motor step.
    * 2.73 counts = 256 CPR/200 steps * 2.133 gear ratio (64:30)
  * 64:30 Stepper converts 50 RPM to 106.6 RPM (50 * 2.133), which is less than encoder's 120 RPM Max
---

