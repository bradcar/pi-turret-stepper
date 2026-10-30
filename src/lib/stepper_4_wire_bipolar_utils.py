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
MAX_RATED_RPM_STEPPER = 50.0
STEPS_PER_REVOLUION_STEPPER = 200
TURRET_GEAR_REDUCTION = 2.75
TURRET_GEAR_REDUCTION = 1.0
STEPS_PER_REVOLUION_TURRET = STEPS_PER_REVOLUION_STEPPER * TURRET_GEAR_REDUCTION


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


def _rotation_step_motor(kit, gear_ratio: float, total_steps: int, stepper_direction: int, batch_size: int,
                         batch_start_time, sleep_correction: float, step_count: int, step_interval: float) -> int:
    while step_count < total_steps:
        step_start = time.perf_counter()

        kit.stepper1.onestep(direction=stepper_direction, style=stepper.SINGLE)
        step_count += 1

        # Every batch size steps (~20 at 50 RPM), evaluate performance and adjust sleep correction
        if step_count % batch_size == 0:
            now = time.perf_counter()
            batch_duration = now - batch_start_time
            if batch_duration > 0:
                est_motor_rpm = (batch_size / STEPS_PER_REVOLUION_STEPPER) * (60.0 / batch_duration)
                est_output_rpm = est_motor_rpm / gear_ratio

                # Calculate time error per step
                target_time_per_step = step_interval
                actual_time_per_step = batch_duration / float(batch_size)
                time_error = actual_time_per_step - target_time_per_step  # Positive = running too slow

                # Apply a damped correction (0.5 gain) to prevent overshooting/oscillation
                # If actual is too slow (positive error), we decrease sleep time (subtract error)
                sleep_correction -= time_error * 0.5

                # Clamp correction so it doesn't try to sleep a negative amount or double the interval
                sleep_correction = max(-step_interval, min(sleep_correction, step_interval))

                print(
                    f"   -> Step {step_count}/{total_steps}: Motor RPM: {est_motor_rpm:.2f}, Turret RPM: {est_output_rpm:.2f},  Correction: {sleep_correction * 1000:.2f}ms")

            batch_start_time = now

        # Sleep compensation with dynamic error correction
        elapsed = time.perf_counter() - step_start
        adjusted_interval = step_interval + sleep_correction
        sleep_time = adjusted_interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)
    return step_count


def rotate_time_between_steps_stepper(kit, step_interval_sec, number_rotations=1.0, gear_ratio=1.0,
                                      clockwise=True) -> bool:
    """
    Executes stepper motor rotation based on the direct time between steps (seconds),
    gear ratio, and number of rotations, using dynamic feedback error correction on sleep time.
    """
    if step_interval_sec <= 0.0:
        print(f"[ERROR] Invalid step interval requested: {step_interval_sec}. Must be greater than 0.")
        return False

    if number_rotations is None or number_rotations <= 0:
        print(f"[ERROR] Invalid number of rotations: {number_rotations}. Must be greater than 0.")
        return False

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    # Calculate corresponding RPM values from the requested step interval
    steps_per_sec = 1.0 / step_interval_sec
    motor_rpm = (steps_per_sec * 60.0) / STEPS_PER_REVOLUION_STEPPER
    output_rpm = motor_rpm / gear_ratio

    if motor_rpm > MAX_RATED_RPM_STEPPER:
        print(
            f"[WARNING] Requested step interval yields {motor_rpm:.2f} RPM, capping speed at {MAX_RATED_RPM_STEPPER} RPM.")
        motor_rpm = MAX_RATED_RPM_STEPPER
        steps_per_sec = (motor_rpm * STEPS_PER_REVOLUION_STEPPER) / 60.0
        step_interval_sec = 1.0 / steps_per_sec
        output_rpm = motor_rpm / gear_ratio

    print(f"rotate_time_between_steps_stepper: Step Interval = {step_interval_sec * 1000:.3f} ms ({steps_per_sec:.2f} steps/sec)")
    print(f"   -> Derived Motor RPM: {motor_rpm:.2f}, Turret RPM: {output_rpm:.2f}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    total_steps = int(number_rotations * STEPS_PER_REVOLUION_STEPPER)
    single_rotation_time = STEPS_PER_REV * step_interval_sec
    print(f"rotate_time_between_steps_stepper: for {number_rotations} rotations ({total_steps} total steps).")
    print(f"rotate_time_between_steps_stepper: Single rotation time: {single_rotation_time:.3f}s")

    # Calculate adaptive batch size based on speed (target ~0.1-0.2 sec windows)
    step_count = 0
    batch_size = max(3, int(motor_rpm * 0.4))

    batch_duration_est = (batch_size * 60.0) / (motor_rpm * STEPS_PER_REVOLUION_STEPPER)
    print(f"batch_size: {batch_size} for {motor_rpm:.2f} RPM (batch duration={batch_duration_est:.4f}s)")

    sleep_correction = 0.0

    start_time = time.perf_counter()
    batch_start_time = start_time

    # loop to rotate the stepper motor
    try:
        step_count = _rotation_step_motor(kit, gear_ratio, total_steps, stepper_direction, batch_size, batch_start_time,
                                          sleep_correction, step_count, step_interval)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False

    total_duration = time.perf_counter() - start_time
    actual_avg_rpm = (step_count / 200 / total_duration) * 60
    print(f"-> Rotated at {actual_avg_rpm:.2f} RPM, {number_rotations} rotations in {total_duration:.2f} seconds.")
    return True


def rotate_at_rpm_stepper(kit, output_rpm, number_rotations=1.0, gear_ratio=1.0, clockwise=True) -> bool:
    """
    Executes stepper motor rotation based on output RPM, gear ratio, and number of rotations,
    using dynamic feedback error correction on sleep time.

    * Error Tracking: Every 20 steps, it compares the actual_time_per_step against the target_time_per_step.
    * Damped Adjustment (Gain = 0.5): It updates sleep_correction using a 50% damping factor (time_error * 0.5).
    * Clamping: The correction is bounded so sleep time can't be below zero or into unstable negative numbers.
    * Visibility: The print statement now also shows the Correction in milliseconds.

        Motor RPM  Batch Size   Batch Duration
         0.1 RPM        3          9.00  sec
         0.5 RPM        3          1.80  sec
         1.0 RPM        3          0.90  sec
         2.5 RPM        3          0.36  sec
         5.0 RPM        3          0.18  sec
         7.5 RPM        3          0.12  sec
        10.0 RPM        4          0.12  sec
        15.0 RPM        6          0.12  sec
        20.0 RPM        8          0.12  sec
        25.0 RPM       10          0.12  sec
        50.0 RPM       20          0.12  sec

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

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    motor_rpm = output_rpm * gear_ratio
    if motor_rpm > MAX_RATED_RPM_STEPPER:
        print(f"[WARNING] Requested speed ({motor_rpm:.2f} RPM), capping speed at {MAX_RATED_RPM_STEPPER} RPM.")
        motor_rpm = MAX_RATED_RPM_STEPPER

    print(f"rotate_at_rpm_stepper: Desired RPM {motor_rpm}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    total_steps = int(number_rotations * STEPS_PER_REVOLUION_STEPPER)
    steps_per_sec = (motor_rpm * STEPS_PER_REVOLUION_STEPPER) / 60.0
    step_interval = 1.0 / steps_per_sec

    print(f"rotate_at_rpm_stepper: {steps_per_sec:.2f} steps/sec for {number_rotations} rotations ({total_steps} total steps).")

    total_steps = int(number_rotations * STEPS_PER_REVOLUION_STEPPER)
    single_rotation_time = STEPS_PER_REV * step_interval_sec
    print(f"rotate_time_between_steps_stepper: for {number_rotations} rotations ({total_steps} total steps).")
    print(f"rotate_time_between_steps_stepper: Single rotation time: {single_rotation_time:.3f}s")

    # Calculate adaptive batch size based on speed (target ~0.1-0.2 sec windows), for sleep time correction
    step_count = 0
    batch_size = max(3, int(motor_rpm * 0.4))

    print(f"batch_size: {batch_size} for {motor_rpm} RPM (batch duration={batch_duration:.4f}s)")
    sleep_correction = 0.0

    start_time = time.perf_counter()
    batch_start_time = start_time

    # loop to rotate the stepper motor
    try:
        step_count = _rotation_step_motor(kit, gear_ratio, total_steps, stepper_direction, batch_size, batch_start_time,
                                          sleep_correction, step_count, step_interval)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False

    total_duration = time.perf_counter() - start_time
    print(
        f"-> Rotated at {(step_count / 200 / total_duration) * 60:.3} RPM, {number_rotations} rotations in {total_duration:.2f} seconds.")
    return True


if __name__ == "__main__":
    kit = MotorKit(i2c=board.I2C())

    try:
        print("--- Test 1: Zero / Negative RPM ---")
        rotate_at_rpm_stepper(kit, output_rpm=0, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)
        rotate_at_rpm_stepper(kit, output_rpm=-5, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION, clockwise=True)

        requested_rpm = 20
        turret_rpm = MAX_RATED_RPM_STEPPER / TURRET_GEAR_REDUCTION
        turret_rpm = 5
        print(f"\n--- Test 2: Valid Direct Drive ({turret_rpm:.4f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=True)

        turret_rpm = MAX_RATED_RPM_STEPPER / TURRET_GEAR_REDUCTION + 0.5
        turret_rpm = 5

        print(f"\n--- Test 3: Requested RPM ({turret_rpm:.2f} RPM) ---")
        rotate_at_rpm_stepper(kit, output_rpm=turret_rpm, number_rotations=2, gear_ratio=TURRET_GEAR_REDUCTION,
                              clockwise=False)

        turn_off_stepper()

    except KeyboardInterrupt:
        turn_off_stepper()
