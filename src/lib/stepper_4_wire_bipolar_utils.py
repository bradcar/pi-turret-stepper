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
TURRET_GEAR_REDUCTION = 1.0


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
    """
    Executes stepper motor rotation based on output RPM, gear ratio, and number of rotations,
    using dynamic feedback error correction on sleep time.

    * Error Tracking: Every 20 steps, it compares the actual_time_per_step against the target_time_per_step.
    * Damped Adjustment (Gain = 0.5): It updates sleep_correction using a 50% damping factor (time_error * 0.5).
    * Clamping: The correction is bounded so sleep time can't be below zero or into unstable negative numbers.
    * Visibility: The print statement now also shows the Correction in milliseconds.

    """
    if output_rpm < 0.0:
        print(f"[ERROR] Invalid RPM requested: {output_rpm}. Speed must be positive (> 0).")
        return False
    elif output_rpm == 0.0:
        print(f"[WARNING]: No RPM requested: {output_rpm}.")
        return True

    if number_rotations is None or number_rotations <= 0:
        print(f"[ERROR] Invalid number of rotations: {number_rotations}. Must be greater than 0.")
        return False

    motor_rpm = output_rpm * gear_ratio
    if motor_rpm > MAX_RATED_RPM:
        print(f"[WARNING] Requested speed ({motor_rpm:.2f} RPM), capping speed at {MAX_RATED_RPM} RPM.")
        motor_rpm = MAX_RATED_RPM

    print(f"rotate_at_rpm_stepper: Desired RPM {motor_rpm}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    total_steps = int(number_rotations * STEPS_PER_REV)
    steps_per_sec = (motor_rpm * STEPS_PER_REV) / 60.0
    step_interval = 1.0 / steps_per_sec

    print(f"rotate_at_rpm_stepper: {steps_per_sec:.2f} steps/sec for {number_rotations} rotations ({total_steps} total steps).")

    start_time = time.perf_counter()
    chunk_start_time = start_time
    step_count = 0

    # Feedback loop variable for sleep correction
    sleep_correction = 0.0

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    try:
        while step_count < total_steps:
            step_start = time.perf_counter()

            kit.stepper1.onestep(direction=stepper_direction, style=stepper.SINGLE)
            step_count += 1

            # Every 20 steps, evaluate performance and adjust sleep correction
            if step_count % 20 == 0:
                now = time.perf_counter()
                chunk_duration = now - chunk_start_time
                if chunk_duration > 0:
                    est_motor_rpm = (20 / STEPS_PER_REV) * (60.0 / chunk_duration)
                    est_output_rpm = est_motor_rpm / gear_ratio

                    # Calculate time error per step
                    target_time_per_step = step_interval
                    actual_time_per_step = chunk_duration / 20.0
                    time_error = actual_time_per_step - target_time_per_step  # Positive = running too slow

                    # Apply a damped correction (0.5 gain) to prevent overshooting/oscillation
                    # If actual is too slow (positive error), we decrease sleep time (subtract error)
                    sleep_correction -= time_error * 0.5

                    # Clamp correction so it doesn't try to sleep a negative amount or double the interval
                    sleep_correction = max(-step_interval, min(sleep_correction, step_interval))

                    print(f"   -> Step {step_count}/{total_steps}: Motor RPM: {est_motor_rpm:.2f}, Turret RPM: {est_output_rpm:.2f},  Correction: {sleep_correction * 1000:.2f}ms")

                chunk_start_time = now

            # Sleep compensation with dynamic error correction
            elapsed = time.perf_counter() - step_start
            adjusted_interval = step_interval + sleep_correction
            sleep_time = adjusted_interval - elapsed

            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False

    total_duration = time.perf_counter() - start_time
    print(f"-> Rotated at {(step_count / 200 / total_duration) * 60:.3} RPM, {number_rotations} rotations in {total_duration:.2f} seconds.")
    return True


if __name__ == "__main__":
    kit = MotorKit(i2c=board.I2C())

    try:
        print("--- Test 1: Zero / Negative RPM ---")
        rotate_at_rpm_stepper(kit, output_rpm=0, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)
        rotate_at_rpm_stepper(kit, output_rpm=-5, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)

        requested_rpm = 20
        turret_rpm = MAX_RATED_RPM / TURRET_GEAR_REDUCTION
        turret_rpm = 5
        print(f"\n--- Test 2: Valid Direct Drive ({turret_rpm:.4f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=True)

        turret_rpm = MAX_RATED_RPM / TURRET_GEAR_REDUCTION + 0.5
        turret_rpm = 5

        print(f"\n--- Test 3: Requested RPM ({turret_rpm:.2f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=False)

        turn_off_stepper()

    except KeyboardInterrupt:
        turn_off_stepper()
