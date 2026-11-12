import board
import busio
from adafruit_motorkit import MotorKit

from lib.stepper_4_wire_bipolar_utils import (rotate_at_rpm_stepper, turn_off_stepper, rotate_time_between_steps_stepper, \
    OUTPUT_GEAR_REDUCTION, MAX_RATED_RPM_STEPPER)

kit = MotorKit(i2c=board.I2C())
kit.stepper1.release()

i2c1 = busio.I2C(board.SCL, board.SDA)
devices1 = i2c1.scan()
print(f"I2C devices: {[hex(addr) for addr in devices1]}\n")

kit = MotorKit(i2c=board.I2C())

try:
    print("=== Test 1: Zero")
    rotate_at_rpm_stepper(kit, output_rpm=0, output_rotations=2, gear_ratio=OUTPUT_GEAR_REDUCTION, clockwise=True)

    print("\n=== Test 2: Negative RPM")
    rotate_at_rpm_stepper(kit, output_rpm=-5, output_rotations=2, gear_ratio=OUTPUT_GEAR_REDUCTION, clockwise=True)

    # turret_rpm = MAX_RATED_RPM_STEPPER / OUTPUT_GEAR_REDUCTION
    # turret_rpm = 12
    # number_rotations = 2.0
    #
    # print(f"\n=== Test 3: Direct Drive Clockwise ({turret_rpm:.2f} RPM)")
    # rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, output_rotations=number_rotations,
    #                       gear_ratio=OUTPUT_GEAR_REDUCTION, clockwise=True)
    #
    # print(f"\n=== Test 4: Direct Drive Counter-Clockwise ({turret_rpm:.2f} RPM)")
    # rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, output_rotations=number_rotations,
    #                       gear_ratio=OUTPUT_GEAR_REDUCTION, clockwise=False)
    #
    # turn_off_stepper(kit)


    # Slow Scanning rotation example:
    # With 6 seconds between each motor step (0.655°), 3,300 seconds per rotation (55 min = (550 * 6)/60)

    rotate_time_between_steps_stepper(kit, step_interval_sec=1, output_rotations=1.1, gear_ratio=OUTPUT_GEAR_REDUCTION,
                                      clockwise=True)

    turn_off_stepper(kit)

except KeyboardInterrupt:
    turn_off_stepper(kit)
