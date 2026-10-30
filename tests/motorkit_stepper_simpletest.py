# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

"""Simple test for using adafruit_motorkit with a stepper motor"""

import time

import board
import busio # Brad added:

from adafruit_motorkit import MotorKit

kit = MotorKit(i2c=board.I2C())
kit.stepper1.release()

# Brad added: i2c scan (note this is actually i2c1,
i2c1 = busio.I2C(board.SCL, board.SDA)
devices1 = i2c1.scan()
print(f"I2C: {devices1=}")

# 100 steps is 180° (200 steps is 360°)
print("Stepper Motor start to rotate 180° @ 10 msec between steps (100 steps)")
for i in range(100):
    kit.stepper1.onestep()
    time.sleep(0.01)
print("Script exit")
