# Stepper Motor & Turret Assembly Specifications

## 1. Combined Stepper + Turret Performance Statistics

Resolution & Step Angle
* **Turret Step Angle:** 0.655° per step (Standard Step 1.8° / 2.75)
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

Realistic Holding Torque (~85% Efficiency)
* ~4.67 kg-cm
* ~65.45 oz-in

Mechanical Loading & Edge Forces
* **Bending Moment (M):** 560 N-mm = 28N * 20mm *(Based on stepper rating of 28N at 20mm from the flange)*
* **Turret Geometry:** 128mm diameter (64mm radius)
* **Force at Turret Edge:** 8.75N = 560 N-mm / 64mm (~1.97 lbs)
* **Safety Factor at Edge (50% to 75%):** 4.4 to 6.5N (~1 lbs)

Precision, Accuracy & Backlash
* **Estimated Angular Error:** 0.033° positional error at the turret output.
* **Backlash:**
  * On metal turret reductions, mechanical backlash (interplay between gear teeth) an dominate real-world positioning accuracy when reversing direction.
  * Even if the motor steps precisely, the turret may exhibit a small deadband of free movement before gears engage in the opposite direction, unless anti-backlash gears or preload mechanisms are used.

## 2. Adafruit Stepper Motor 4-wire bipolar (NEMA-17, pid 324)
* **Rated Voltage:** 12V (can be driven at lower voltage, but torque will drop)
* **Max Current:** 350mA

### Physical & Mechanical Specifications
* **Body Size:** 42mm / 1.65" square body
* **Mounting Holes:** 31mm / 1.22" square pattern, 3mm metric screws (M3)
* **Drive Shaft:** 5mm diameter, 24mm long, with a machined flat
* **Step Angle:** 1.8° per step (5% angle accuracy)
* **Steps per Revolution:** 200
* **Speed:** 50 RPM
* **Holding Torque (per phase):** 
  * 28 oz-in
  * 20 N-cm
  * 2 kg-cm

### Links & Documentation
* **Product Page:** [Adafruit Product 324](https://www.adafruit.com/product/324)
* **Overview Doc:** [Adafruit DC & Stepper Motor HAT for Raspberry Pi](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)


## 3. goBILDA 169 Metal Turret (3208-0004-0001)
* **Product Page:** [Gear-Driven Turret (2.75:1 Ratio, 105mm ID)](https://www.gobilda.com/gear-driven-turret-2-75-1-ratio-105mm-id/)
* **Gear Reduction:** 2.75:1
* **Weight:** 438g (with 64T Gear — may need to be purchased separately)
* **Adaptors:**: 
  * 1700 Series Stepper Mount (NEMA-17)
    * will add thermal paste so frame can also be heat sink
  * 1314 Series Set-Screw Hub (5mm Bore)
  * 1120 Series U-Channel (8 Hole, 216mm)
  * 140 Series Aluminum Baseplate (6mm, 144mm Diameter)
  * Plastic Hub-Mount Disc (240mm Diameter)

---

