#
"""
stepper_4_wire_bipolar_utils.py

Adafruit Stepper Motor (NEMA-17) 4-wire bipolar
    Product Page: [Adafruit Product 324](https://www.adafruit.com/product/324)
    Overview Doc: [Adafruit DC & Stepper Motor HAT for Raspberry Pi](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)
    * Step Angle: 1.8° per step (5% angle accuracy)
    * Steps per Revolution: 200
    * Speed: 50 RPM

"""
import time

import board
from adafruit_motor import stepper
from adafruit_motorkit import MotorKit

# Motor Specifications Constants
STEP_ANGLE_DEG = 1.8
STEPS_PER_REV = 200
MAX_RATED_RPM = 50.0
TURRET_GEAR_REDUCTION = 2.75


def set_direction_stepper(clockwise: bool):
    if clockwise:
        print("Clockwise")
    else:
        print("Counter-clockwise")


def step_stepper(num_steps: int, step_delay_us, clockwise=True):
    print(f"step_stepper: Steps {num_steps}, Clockwise={clockwise}")
    print(f"Step Delay Us{step_delay_us}")


def move_degrees_stepper(degrees, gear_ratio=1.0, clockwise=True):
    print(f"move_degrees_stepper: Degrees {degrees}, gear_ratio={gear_ratio}, Clockwise={clockwise}")
    pass


def move_to_position_stepper(target_step: int, gear_ratio=1.0, clockwise=True):
    print(f"move_to_position_stepper: target_step {target_step}, gear_ratio={gear_ratio}, Clockwise={clockwise}")
    pass


def home_stepper(home_step, gear_ratio=1.0, clockwise=True):
    print(f"home_stepper: target_step {home_step}, gear_ratio={gear_ratio}, Clockwise={clockwise}")
    pass


def turn_off_stepper():
    kit.stepper1.release()


def rotate_at_rpm_stepper(kit, output_rpm, number_rotations=1.0, gear_ratio=1.0, clockwise=True) -> bool:
    """Executes motor rotation based on output RPM, gear ratio, and number of rotations."""
    if output_rpm < 0.0:
        print(f"[ERROR] Invalid RPM requested: {output_rpm} RPM. Speed must be positive (> 0).")
        return False
    elif output_rpm == 0.0:
        print(f"[WARNING]: No RPM requested: {output_rpm} RPM.")
        return True

    if number_rotations is None or number_rotations <= 0:
        print(f"[ERROR] Invalid number of rotations: {number_rotations}. Must be greater than 0.")
        return False

    motor_rpm = output_rpm * gear_ratio
    if motor_rpm > MAX_RATED_RPM:
        print(f"[WARNING] Requested speed ({motor_rpm:.2f} RPM), capping speed at {MAX_RATED_RPM} RPM.")
        motor_rpm = MAX_RATED_RPM

    print(f"rotate_at_rpm_stepper: actual RPM {motor_rpm}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    total_steps = int(number_rotations * STEPS_PER_REV)
    steps_per_sec = (motor_rpm * STEPS_PER_REV) / 60.0
    step_interval = 1.0 / steps_per_sec

    print(
        f"Stepper at {motor_rpm:.2f} RPM ({steps_per_sec:.2f} steps/sec) for {number_rotations} rotations ({total_steps} total steps).")

    start_time = time.perf_counter()
    chunk_start_time = start_time
    step_count = 0

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    try:
        while step_count < total_steps:
            step_start = time.perf_counter()

            kit.stepper1.onestep(direction=stepper_direction, style=stepper.SINGLE)
            step_count += 1

            # Print estimated RPM every 20 steps
            if step_count % 20 == 0:
                now = time.perf_counter()
                chunk_duration = now - chunk_start_time
                if chunk_duration > 0:
                    est_motor_rpm = (20 / STEPS_PER_REV) * (60.0 / chunk_duration)
                    est_output_rpm = est_motor_rpm / gear_ratio
                    print(
                        f" -> Step {step_count}/{total_steps}: Est Motor RPM: {est_motor_rpm:.2f}, Est Turret RPM: {est_output_rpm:.2f}")
                chunk_start_time = now

            # Precise drift compensation using perf_counter
            elapsed = time.perf_counter() - step_start
            sleep_time = step_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False


if __name__ == "__main__":
    kit = MotorKit(i2c=board.I2C())

    try:
        print("--- Test 1: Zero / Negative RPM ---")
        rotate_at_rpm_stepper(kit, output_rpm=0, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)
        rotate_at_rpm_stepper(kit, output_rpm=-5, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)

        turret_rpm = MAX_RATED_RPM / TURRET_GEAR_REDUCTION
        print(f"\n--- Test 2: Valid Direct Drive ({turret_rpm:.4f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=True)

        turret_rpm = MAX_RATED_RPM / TURRET_GEAR_REDUCTION + 0.5
        print(f"\n--- Test 3: Requested RPM ({turret_rpm:.2f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=False)

    except KeyboardInterrupt:
        turn_off_stepper()
