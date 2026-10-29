# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""
Stepper Motor Test

Four Modes
1. Single Coil Steps (stepper.SINGLE)
   - How it works: Energizes one single coil (phase) at a time.
   - Characteristics:
     - Power/Torque: Lower holding torque. Draws the lowest current (coolest).
     - Step Angle: 1.8° per step (200 steps/rev).

2. Double Coil Steps (stepper.DOUBLE)
   - How it works: Energizes two adjacent coils simultaneously.
   - Characteristics:
     - Power/Torque: Maximum holding torque (matches motor rating).
     - Efficiency: Draws maximum current and produces the most heat.
     - Step Angle: 1.8° per step (200 steps/rev).

3. Interleaved Coil Steps (stepper.INTERLEAVE)
   - How it works: Alternates between single and double coils (Single → Double → Single...).
   - Characteristics:
     - Power/Torque: Moderate holding torque and current draw.
     - Step Angle: 0.9° per step (400 steps/rev, half-stepping).

4. Microsteps (stepper.MICROSTEP)
   - How it works: Uses PWM to ramp coil currents in sinusoidal increments.
   - Characteristics:
     - Motion & Smoothness: Extremely smooth, quiet, low vibration.
     - Step Angle: 0.1125° per microstep (16x microstepping = 3,200 microsteps/rev).
     - Torque Trade-off: Lower dynamic holding torque at microstep positions.
"""

import board
from adafruit_motor import stepper

from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())

kit.stepper1.release()

print(" Four tests: 180° forward and back (100 Steps each)\n")
while True:
    print("\nSingle coil steps (1.8°/step, lower torque, cooler)")
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.SINGLE)
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)

    print("Double coil steps (1.8°/step, highest torque, hottest)")
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.DOUBLE)
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)

    print("Interleaved coil steps (0.9°/step, moderate torque/temp)")
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.INTERLEAVE)
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.INTERLEAVE)

    print("Microsteps (0.1125°/step [16x], ultra-smooth, fluctuating torque)")
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)
    for i in range(100):
        kit.stepper1.onestep(direction=stepper.BACKWARD, style=stepper.MICROSTEP)
