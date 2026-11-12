#
"""
stepper_4_wire_bipolar_utils.py

Stepper motor utilities for precision gear-driven output gear (ex: turret motion).
Handles motion primitives, step delays, adaptive closed-loop feedback timing, and rotational tracking.

Motor Specifications (Adafruit NEMA-17, 4-wire bipolar, Product 324)
    Product Page: [Adafruit Product 324](https://www.adafruit.com/product/324)
    Overview Doc: [Adafruit DC & Stepper Motor HAT for Raspberry Pi](https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi)
    * Step Angle: 1.8° per step (5% angle accuracy)
    * Steps per Revolution: 200 steps
    * Max Rated Speed: 50.0 RPM

Low-Level Motion Primitives
    _step_motor_move(): Executes individual motor steps with delay and live position tracking.
    turn_off_stepper(): Releases holding torque on the stepper motor coils.

Direct Step & Position Control
    step_stepper(): Moves the motor a specified number of raw physical motor steps.
    move_degrees_stepper(): Rotates the output shaft by a specified angle in degrees.
    move_to_position_stepper(): Drives the output shaft to an absolute step position.
    home_stepper(): Moves the output shaft to a software-defined home position.

Adaptive Velocity & Timing Control
    rotate_at_rpm_stepper(): Rotates output gear at a target RPM with dynamic feedback error correction.
    rotate_time_between_steps_stepper(): Rotates output gear based on direct step interval timing.
"""

import math
import time

from adafruit_motor import stepper

# Motor Specifications Constants
STEP_ANGLE_DEG = 1.8
MAX_RATED_RPM_STEPPER = 50.0
STEPS_PER_REVOLUTION_STEPPER = 200
OUTPUT_GEAR_REDUCTION = 2.75
STEPS_PER_REVOLUION_TURRET = STEPS_PER_REVOLUTION_STEPPER * OUTPUT_GEAR_REDUCTION

# Global Step location module-level motor position after each successful step.
_current_motor_step_count = 0


def _step_motor_move(kit, num_steps: int, step_delay_ms: float, clockwise=True) -> bool:
    """
    Execute individual motor steps with a specified delay between steps.
    Updates the global motor position after each successfully executed step.
    """
    global _current_motor_step_count

    if clockwise:
        stepper_direction = stepper.FORWARD
        position_direction = 1
    else:
        stepper_direction = stepper.BACKWARD
        position_direction = -1

    try:
        for _ in range(num_steps):
            kit.stepper1.onestep(direction=stepper_direction, style=stepper.SINGLE)
            _current_motor_step_count += position_direction

            time.sleep(step_delay_ms / 1000.0)

    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Stepper movement halted by user.")
        print(f"Current motor position: {_current_motor_step_count}")
        return False

    return True


def step_stepper(kit, num_steps: int, step_delay_ms: float, clockwise=True) -> bool:
    """
    Move the stepper motor a specified number of individual motor steps.

    Args:
        kit: MotorKit controller instance.
        num_steps (int): Number of motor steps. Must be greater than zero.
        step_delay_ms (float): Delay between steps in milliseconds.
        clockwise (bool): True for clockwise; False for counterclockwise.

    Returns:
        bool: True if movement completes; False if inputs are invalid
              or movement is interrupted.

    Notes:
        - Maximum rated motor speed is enforced.
        - Position tracking is updated after each successful step.
    """
    print(f"step_stepper: Steps {num_steps}, Clockwise={clockwise}")
    print(f"Step Delay Ms: {step_delay_ms}")

    if not isinstance(num_steps, int) or isinstance(num_steps, bool) or num_steps <= 0:
        print(f"[ERROR] Invalid number of steps: {num_steps}. Must be a positive integer.")
        return False

    if not isinstance(step_delay_ms, (int, float)) or isinstance(step_delay_ms, bool) or not math.isfinite(
            step_delay_ms) or step_delay_ms <= 0:
        print(f"[ERROR] Invalid step delay: {step_delay_ms}. Must be greater than zero.")
        return False

    if not isinstance(clockwise, bool):
        print(f"[ERROR] Invalid direction: {clockwise}.")
        return False

    min_step_delay_ms = 60_000.0 / (MAX_RATED_RPM_STEPPER * STEPS_PER_REVOLUTION_STEPPER)

    if step_delay_ms < min_step_delay_ms:
        print(f"[WARNING] Step delay too short. Capping at {min_step_delay_ms:.3f} ms.")
        step_delay_ms = min_step_delay_ms

    return _step_motor_move(kit, num_steps, step_delay_ms, clockwise)


def move_degrees_stepper(kit, degrees: float, gear_ratio=1.0, clockwise=True) -> bool:
    """
    Rotate the output shaft by a specified number of degrees.

    Notes:
        - Converts output shaft degrees into motor steps.
        - Uses maximum rated motor speed.
        - Fractional steps are rounded to the nearest whole step.
        - Updates the tracked motor position.

    Args:
        kit: MotorKit controller instance.
        degrees (float): Angle to rotate. Must be greater than zero.
        gear_ratio (float): Motor-to-output speed ratio. Defaults to 1.0.
        clockwise (bool): True for clockwise; False for counterclockwise.

    Returns:
        bool: True if movement completes; False if inputs are invalid or movement is interrupted.
    """
    print(f"move_degrees_stepper: Degrees {degrees}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    if not isinstance(degrees, (int, float)) or isinstance(degrees, bool) or not math.isfinite(degrees) or degrees <= 0:
        print(f"[ERROR] Invalid degrees: {degrees}. Must be greater than zero.")
        return False

    if not isinstance(clockwise, bool):
        print(f"[ERROR] Invalid direction: {clockwise}.")
        return False

    total_steps = round((degrees / 360.0) * STEPS_PER_REVOLUTION_STEPPER * gear_ratio)

    if total_steps <= 0:
        print("[ERROR] Requested movement is smaller than one motor step.")
        return False

    step_delay_ms = 60_000.0 / (MAX_RATED_RPM_STEPPER * STEPS_PER_REVOLUTION_STEPPER)
    print(f"   -> Motor Steps: {total_steps}, Step Delay: {step_delay_ms:.3f} ms")

    return _step_motor_move(kit, total_steps, step_delay_ms, clockwise)


def move_to_position_stepper(kit, target_step: int, gear_ratio=1.0, clockwise=True) -> bool:
    """
    Move the output shaft to an absolute step position, in the chosen direction.
    Warning issues if this is not the shortest distance.

    Notes:
        - Position is tracked internally in motor steps.
        - Direction must agree with the target position.
        - Uses maximum rated motor speed.
        - Software position tracking does not detect missed steps.

    Args:
        kit: MotorKit controller instance.
        target_step (int): Absolute output position in steps.
        gear_ratio (float): Motor-to-output speed ratio. Defaults to 1.0.
        clockwise (bool): Required movement direction.

    Returns:
        bool: True if target position is reached; False if inputs are invalid or movement is interrupted.
    """
    global _current_motor_step_count

    print(f"move_to_position_stepper: target_step {target_step}, gear_ratio={gear_ratio}, Clockwise={clockwise}")

    if not isinstance(target_step, int) or isinstance(target_step, bool):
        print(f"[ERROR] Invalid target position: {target_step}. Must be an integer.")
        return False

    if not isinstance(clockwise, bool):
        print(f"[ERROR] Invalid direction: {clockwise}.")
        return False

    target_motor_step = round(target_step * gear_ratio)
    step_difference = target_motor_step - _current_motor_step_count

    if step_difference == 0:
        print("[WARNING] Already at requested position.")
        return True

    required_clockwise = step_difference > 0
    motor_steps_per_revolution = round(STEPS_PER_REVOLUTION_STEPPER * gear_ratio)

    if required_clockwise != clockwise:
        print("[WARNING] Requested direction conflicts with shortest path; taking the longer path.")
        if clockwise:
            step_difference += motor_steps_per_revolution
        else:
            step_difference -= motor_steps_per_revolution

    num_steps = abs(step_difference)

    step_delay_ms = 60_000.0 / (MAX_RATED_RPM_STEPPER * STEPS_PER_REVOLUTION_STEPPER)

    print(f"   -> Current Motor Step: {_current_motor_step_count} -> Target Motor Step: {target_motor_step}")
    print(f"   -> Steps to Move: {num_steps} Step Delay: {step_delay_ms:.3f} ms")

    return _step_motor_move(kit, num_steps, step_delay_ms, clockwise)


def home_stepper(kit, home_step=0, gear_ratio=1.0, clockwise=True) -> bool:
    """
    Move the output shaft to a predefined software home position.

    Notes:
        - Uses software position tracking.
        - Does not detect a physical home switch.
        - Assumes no missed steps or external movement.

    Args:
        kit: MotorKit controller instance.
        home_step (int): Absolute home position in output steps.
        gear_ratio (float): Motor-to-output speed ratio. Defaults to 1.0.
        clockwise (bool): Required movement direction.

    Returns:
        bool: True if home position is reached; False otherwise.
    """
    print(f"home_stepper: target_step {home_step}, gear_ratio={gear_ratio}, Clockwise={clockwise}")
    return move_to_position_stepper(kit, home_step, gear_ratio, clockwise)


def turn_off_stepper(kit):
    kit.stepper1.release()
    print("\nStepper Motor released. Coils not energized.\n")



def _rotation_step_motor(kit, gear_ratio: float, total_steps: int, stepper_direction: int, batch_size: int,
                         batch_start_time, sleep_correction: float, step_count: int, step_interval: float) -> int:
    global _current_motor_step_count

    if stepper_direction == stepper.FORWARD:
        position_direction = 1
    else:
        position_direction = -1

    while step_count < total_steps:
        step_start = time.perf_counter()

        kit.stepper1.onestep(direction=stepper_direction, style=stepper.SINGLE)
        _current_motor_step_count += position_direction
        step_count += 1

        # Every batch size steps (~20 at 50 RPM), evaluate RPM and adjust sleep correction
        if step_count % batch_size == 0:
            now = time.perf_counter()
            batch_duration = now - batch_start_time
            if batch_duration > 0:
                est_motor_rpm = (batch_size / STEPS_PER_REVOLUTION_STEPPER) * (60.0 / batch_duration)
                est_output_rpm = est_motor_rpm / gear_ratio

                # Calculate time error per step, positive time_error is running too slow
                target_time_per_step = step_interval
                actual_time_per_step = batch_duration / float(batch_size)
                time_error = actual_time_per_step - target_time_per_step

                # Apply a damped correction (0.5 gain) to prevent overshooting/oscillation
                # If actual is too slow (positive error), we decrease sleep time (subtract error)
                sleep_correction -= time_error * 0.5

                # Clamp correction so it doesn't try to sleep a negative amount or double the interval
                sleep_correction = max(-step_interval, min(sleep_correction, step_interval))

                print(f"   -> Step {step_count}/{total_steps}: Output RPM: {est_output_rpm:.2f} (Motor RPM: {est_motor_rpm:.2f})  Correction: {sleep_correction * 1000:.2f}ms")

            batch_start_time = now

        # Sleep compensation with dynamic error correction
        elapsed = time.perf_counter() - step_start
        adjusted_interval = step_interval + sleep_correction
        sleep_time = adjusted_interval - elapsed

        if sleep_time > 0:
            time.sleep(sleep_time)
    return step_count


def rotate_time_between_steps_stepper(kit, step_interval_sec, output_rotations=1.0, gear_ratio=1.0,
                                      clockwise=True) -> bool:
    """
    Executes stepper motor rotation based on the direct time between steps (seconds), gear ratio, and number of rotations.

    At a calculated batch size (3 to 20) it will measure RPM and adjust slee time  using dynamic feedback error correction.
    """
    if step_interval_sec <= 0.0:
        print(f"[ERROR] Invalid step interval requested: {step_interval_sec}. Must be greater than 0.0")
        return False

    if output_rotations is None or output_rotations <= 0:
        print(f"[ERROR] Invalid number of rotations: {output_rotations}. Must be greater than 0.0")
        return False

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    # Calculate corresponding RPM values from the requested step interval
    steps_per_sec = 1.0 / step_interval_sec
    motor_rpm = (steps_per_sec * 60.0) / STEPS_PER_REVOLUTION_STEPPER
    output_rpm = motor_rpm / gear_ratio

    if motor_rpm > MAX_RATED_RPM_STEPPER:
        print(f"[WARNING] Requested step interval needs {motor_rpm:.2f} Stepper RPM, capped Stepper RPM at {MAX_RATED_RPM_STEPPER} RPM.")
        motor_rpm = MAX_RATED_RPM_STEPPER
        steps_per_sec = (motor_rpm * STEPS_PER_REVOLUTION_STEPPER) / 60.0
        step_interval_sec = 1.0 / steps_per_sec
        output_rpm = motor_rpm / gear_ratio

    total_steps = int(output_rotations * STEPS_PER_REVOLUTION_STEPPER * gear_ratio)
    single_rotation_time = STEPS_PER_REVOLUTION_STEPPER * step_interval_sec

    print(f"rotate_time_between_steps_stepper: ")
    print(f"  Step Interval = {step_interval_sec * 1000:.3f} ms ({steps_per_sec:.2f} steps/sec)")
    print(f"  Output RPM {output_rpm:.2f} {'Clockwise' if clockwise else 'Counter-clockwise'}, gear_ratio: {gear_ratio} reduction")
    print(f"  {output_rotations} rotations for {output_rotations * single_rotation_time:,.1f} secs (rotation period: {single_rotation_time:.2f}s)")
    print(f"  {steps_per_sec:.2f} steps/sec for {total_steps} total steps")

    # Calculate RPM measurement batch size based on speed (target ~0.1-0.2 sec windows, but now fewer than 3 at low RPM).
    step_count = 0
    batch_size = max(3, int(motor_rpm * 0.4))

    batch_duration_est = (batch_size * 60.0) / (motor_rpm * STEPS_PER_REVOLUTION_STEPPER)
    print(f"  batch_size: {batch_size} for {motor_rpm:.2f} RPM correction (batch duration={batch_duration_est:.4f}s)")

    sleep_correction = 0.0

    start_time = time.perf_counter()
    batch_start_time = start_time

    # loop to rotate the stepper motor
    try:
        step_count = _rotation_step_motor(kit, gear_ratio, total_steps, stepper_direction, batch_size, batch_start_time,
                                          sleep_correction, step_count, step_interval_sec)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False

    total_duration = time.perf_counter() - start_time
    actual_motor_rpm = (step_count / STEPS_PER_REVOLUTION_STEPPER / total_duration) * 60
    actual_output_rpm = actual_motor_rpm / gear_ratio
    print(f"-> {actual_output_rpm:.2f} Output RPM ({actual_motor_rpm:.2f} Motor RPM), {output_rotations} rotations in {total_duration:.2f} sec")
    print(f"-> {(1 - output_rpm / actual_output_rpm) * 100:.2f}% RPM error")
    return True


def rotate_at_rpm_stepper(kit, output_rpm, output_rotations=1.0, gear_ratio=1.0, clockwise=True) -> bool:
    """
    Rotate output gear a number of output rotations (fractional steps allowed, ex: 1.2) at a requested output RPM.
    It uses adaptive step batching and timing feedback to improve rotational speed accuracy every ~.1 sec.

    The requested output RPM is converted to motor RPM using the gear ratio.
    Motor speed is capped at MAX_RATED_RPM_STEPPER if the calculated RPM exceeds the motor's rated maximum.

        Features:
        - Error Tracking: Every 3 to 20 steps, it compares the actual_time_per_step against the target_time_per_step.
        - Damped Adjustment (Gain = 0.5): It updates sleep_correction using a 50% damping factor (time_error * 0.5).
        - Clamping: The correction is bounded so sleep time can't be below zero or into unstable negative numbers.
        - Visibility: The print statement now also shows the Correction in milliseconds.
        - Direction Control: Supports clockwise and counterclockwise rotation.
        - Speed Conversion: Calculates motor RPM from the requested output RPM and gear ratio.
        - Speed Limiting: Caps motor RPM at MAX_RATED_RPM_STEPPER. Turret rotation maybe significantly less
        - Step Calculation: Determines the total number of steps required from the requested number of output rotations.
        - Adaptive Batching Measurements: Calculate the steps/batch based on motor RPM, creating about 0.1-0.2 sec batch intervals.
        - Timing Feedback: Uses to adjust step timing and compensate for inaccuracies.
        - Interrupt Handling: Stops rotation and returns False if a KeyboardInterrupt occurs.
        - Performance Reporting: Reports calculated step rate, batch size, estimated rotation time, and measured rotation speed.

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

        Notes:
        - A zero RPM request returns True without moving the motor.
        - Negative RPM requests are rejected.

    Args:
        kit: Stepper motor instance.
        output_rpm (float): Requested revolutions per minute (RPM) at output gear. Must be non-negative.
        output_rotations (float, optional): Number of output gear rotations to perform. Defaults to 1.0. Must be greater than zero.
        gear_ratio (float, optional): Motor-to-output speed ratio. Stepper RPM is output_rpm * gear_ratio. Defaults to 1.0.
        clockwise (bool, optional): True rotates clockwise; False rotates counterclockwise. Defaults to True.

    Returns:
        bool:
            True if the requested rotation completes successfully, or if zero RPM is requested.
            False if the input RPM or rotation count is invalid, or if rotation is interrupted by a KeyboardInterrupt.
    """
    if output_rpm < 0.0:
        print(f"[ERROR] Invalid RPM requested: {output_rpm}. Speed must be positive (> 0).")
        return False
    elif output_rpm == 0.0:
        print(f"[WARNING]: No RPM requested: {output_rpm:.1f}")
        return True

    if output_rotations is None or output_rotations <= 0:
        print(f"[ERROR] Invalid number of rotations: {output_rotations}. Must be greater than 0.0")
        return False

    if clockwise:
        stepper_direction = stepper.FORWARD
    else:
        stepper_direction = stepper.BACKWARD

    motor_rpm = output_rpm * gear_ratio
    if motor_rpm > MAX_RATED_RPM_STEPPER:
        print(f"[WARNING] Requested Motor RPM ({motor_rpm:.2f} RPM), capped Motor RPM at {MAX_RATED_RPM_STEPPER} RPM.")
        motor_rpm = MAX_RATED_RPM_STEPPER
        # Recalculate target output_rpm based on the capped motor speed
        output_rpm = motor_rpm / gear_ratio

    total_steps = int(output_rotations * STEPS_PER_REVOLUTION_STEPPER * gear_ratio)
    steps_per_sec = (motor_rpm * STEPS_PER_REVOLUTION_STEPPER) / 60.0
    step_interval = 1.0 / steps_per_sec
    single_rotation_time = STEPS_PER_REVOLUTION_STEPPER * step_interval

    print(f"rotate_at_rpm_stepper: ")
    print(f"  Output RPM {output_rpm:.2f} {'Clockwise' if clockwise else 'Counter-clockwise'}, gear_ratio: {gear_ratio} reduction")
    print(f"  {output_rotations} rotations for {output_rotations * single_rotation_time:,.1f} secs (rotation period: {single_rotation_time:.2f}s)")
    print(f"  {steps_per_sec:.2f} steps/sec for {total_steps} total steps")

    # Calculate RPM measurement batch size based on speed (target ~0.1-0.2 sec windows, but now fewer than 3 at low RPM).
    step_count = 0

    batch_size = max(3, int(motor_rpm * 0.4))
    batch_duration = (batch_size * 60.0) / (motor_rpm * STEPS_PER_REVOLUTION_STEPPER)
    print(f"  batch_size: {batch_size} for {motor_rpm} RPM (batch duration={batch_duration:.4f}s)")

    sleep_correction = 0.0
    start_time = time.perf_counter()
    batch_start_time = start_time

    # rotate the stepper motor
    try:
        step_count = _rotation_step_motor(kit, gear_ratio, total_steps, stepper_direction, batch_size, batch_start_time,
                                          sleep_correction, step_count, step_interval)
    except KeyboardInterrupt:
        print("\n[INTERRUPTED] Rotation halted by user.")
        return False

    total_duration = time.perf_counter() - start_time
    actual_motor_rpm = (step_count / STEPS_PER_REVOLUTION_STEPPER / total_duration) * 60
    actual_output_rpm = actual_motor_rpm / gear_ratio
    print(
        f"-> {actual_output_rpm:.2f} Output RPM ({actual_motor_rpm:.2f} Motor RPM), {output_rotations} rotations in {total_duration:.2f} sec")
    print(f"-> {(1 - output_rpm / actual_output_rpm) * 100:.2f}% RPM error")
    return True
