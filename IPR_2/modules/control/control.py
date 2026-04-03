###############################################################################
# File Name: control.py
# Description: Contains the main control logic for determining the movement of 
#              the robot based on the detected lanes from the vision module 
#              and sending commands to the motor controller.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import modules.control.control_config as control_config
import modules.vision.vision_config as vision_config
import modules.motor.motor_control as motor_control
import modules.motor.motor_control_config as motor_control_config

# Library Imports


###############################################################################
# GLOBAL VARIABLES
###############################################################################

reverse_flag = False
reverse_counter = 0

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################


###############################################################################
# Function Name: determine_movement
# Description: Determines the direction of movement based on the position
#              of the detected lanes relative to the center of the frame 
#              and sends commands to the motor controller.
###############################################################################

def determine_movement(left_lane, right_lane, object_distance_cm):
    global reverse_flag
    global reverse_counter
    
    # Stopping conditions:

    # If no lanes are detected, stop and wait for the next frame
    if left_lane is None and right_lane is None:
        if reverse_flag:
            motor_control.move_backward()

            if reverse_counter > control_config.REVERSE_LIMIT:
                reverse_flag = False
                reverse_counter = 0
            else:
                reverse_counter += 1
            
            return
        else:
            motor_control.stop_motors()
            return
    
    reverse_flag = True
    reverse_counter = 0
    

    # If an object is detected within X CM, stop
    if object_distance_cm is not None and object_distance_cm < vision_config.MAX_REACTION_DISTANCE:
        if reverse_flag:
            motor_control.move_backward()

            if reverse_counter > control_config.REVERSE_LIMIT:
                reverse_flag = False
                reverse_counter = 0
            else:
                reverse_counter += 1
            
            return
        else:
            motor_control.stop_motors()
            return
    
    reverse_flag = True
    reverse_counter = 0


    # Fallback conditions:
    
    # If only one lane is detected, commit to that recovery action and return
    # This prevents later logic from overriding the turn command in the same frame
    #    Assumptions: 
    #    Only left lane is visible, then car is likely too far left and should turn right
    #    Only right lane is visible, then car is likely too far right and should turn left
    if left_lane is not None and right_lane is None:
        motor_control.turn_right()
        return

    if right_lane is not None and left_lane is None:
        motor_control.turn_left()
        return


    # Frame center x coordinent used for ideal allignment of the car.
    frame_center_x = vision_config.PROCESSING_WIDTH / 2

    # Both lanes exist, so now compute lane center normally
    lane_center_x = int((left_lane[0] + right_lane[0]) / 2)

    # Error is the distance from the frame center to the lane center.
    # Positive error means frame center is to the right of lane center
    error = frame_center_x - lane_center_x

    # Go straight when close enough
    if abs(error) <= control_config.MIN_ERROR_THRESHOLD:
        motor_control.move_forward()
        return


    # Mapping the error to a PWM duty cycle for the inside motors when turning.
    # The larger the error, the slower the inside motors should go to allow for sharper turns.
    error_ratio = abs(error) / control_config.MAX_LANE_TO_FRAME_CENTER_ERROR

    # Clamping error ratio to be between 0 and 1 to avoid negative PWM duty cycles or PWM duty cycles that are too high
    if error_ratio > 1.0:
        error_ratio = 1.0
    elif error_ratio < 0.0:
        error_ratio = 0.0

    # The inside motors should slow down based on the error ratio.
    # This means it will be at full speed when the error is 0 
    # (lane center is perfectly aligned with frame center) and 
    # will slow down to 0 when the error is at or above the maximum
    # lane to frame center error.
    inside_pwm_duty = int((1.0 - error_ratio) * motor_control_config.BASE_PWM_DUTY)

    # Constraining the minimum PWM duty cycle
    if inside_pwm_duty < motor_control_config.BASE_LOW_PWM_DUTY:
        inside_pwm_duty = motor_control_config.BASE_LOW_PWM_DUTY


    # Negative error means lane center is to the right of frame center
    # Turn right if lane center is to the right of frame center
    # When turning right, then the left motors should be at full speed and the right motors should be slowed down based on the error.
    if error < 0:
        left_pwm_duty = motor_control_config.BASE_PWM_DUTY
        right_pwm_duty = inside_pwm_duty
        motor_control.move_at_speed(left_pwm_duty, right_pwm_duty)

    # Positive error means lane center is to the left of frame center
    # Turn left if lane center is to the left of frame center
    # When turning left, then the right motors should be at full speed and the left motors should be slowed down based on the error.
    elif error > 0:
        left_pwm_duty = inside_pwm_duty
        right_pwm_duty = motor_control_config.BASE_PWM_DUTY
        motor_control.move_at_speed(left_pwm_duty, right_pwm_duty)