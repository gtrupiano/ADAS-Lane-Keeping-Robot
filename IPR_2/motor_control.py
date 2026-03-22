###############################################################################
# File Name: motor_control.py
# Description: Functions for controlling the motors of the car.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import motor_control_config

# Library Imports
import Freenove_Libraries.pca9685 as pca9685


###############################################################################
# GLOBAL VARIABLES
###############################################################################

motor_controller = None


###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: setup_motor_controller
# Description: Initializes the motor controller with the correct I2C address 
#              and PWM frequency.
###############################################################################

def setup_motor_controller():
    global motor_controller
    motor_controller = pca9685.PCA9685(motor_control_config.MOTOR_CONTROLLER_I2C_ADDRESS, debug=True)
    motor_controller.set_pwm_freq(motor_control_config.MOTOR_CONTROLLER_PWM_FREQUENCY)


###############################################################################
# Function Name: move_forward
# Description: Moves the car forward at the predefined forward PWM duty cycle.
#              To control the speed of the car, the duty cycle parameter named:
#              "FORWARD_DUTY_CYCLE" can be adjusted in motor_control_config.py
###############################################################################

def move_forward():
    _motor_move_in_direction(motor_control_config.Direction_t.FORWARD)


###############################################################################
# Function Name: move_backward
# Description: Moves the car backward at the predefined backward PWM duty cycle.
#              To control the speed of the car, the duty cycle parameter named:
#              "BACKWARD_DUTY_CYCLE" can be adjusted in motor_control_config.py
###############################################################################

def move_backward():
    _motor_move_in_direction(motor_control_config.Direction_t.BACKWARD)


###############################################################################
# Function Name: turn_left
# Description: Turns the car left at the predefined turn PWM duty cycle.
#              To control the speed of the turn, the duty cycle parameters 
#              named:
#              "TURN_HIGH_DUTY_CYCLE" and "TURN_LOW_DUTY_CYCLE" can be adjusted
#              in motor_control_config.py. HIGH in this case refers to the right
#              motors and LOW refers to the left motors. This is because when 
#              turning left, the right motors should be at a higher duty cycle 
#              than the left motors.
#
#              If sharper turns are desired, then the disparity between the two
#              turn duty cycle parameters can be increased. If a twisting turn
#              is desired, then the turn duty cycle parameters should be 
#              opposite signs (HIGH = negative, LOW = positive).
###############################################################################

def turn_left():
    _motor_move_in_direction(motor_control_config.Direction_t.LEFT)


###############################################################################
# Function Name: turn_right
# Description: Turns the car right at the predefined turn PWM duty cycle.
#              To control the speed of the turn, the duty cycle parameters 
#              named:
#              "TURN_HIGH_DUTY_CYCLE" and "TURN_LOW_DUTY_CYCLE" can be adjusted
#              in motor_control_config.py. HIGH in this case refers to the left
#              motors and LOW refers to the right motors. This is because when 
#              turning right, the left motors should be at a higher duty cycle 
#              than the right motors.
#
#              If sharper turns are desired, then the disparity between the two
#              turn duty cycle parameters can be increased. If a twisting turn
#              is desired, then the turn duty cycle parameters should be 
#              opposite signs (HIGH = negative, LOW = positive).
###############################################################################

def turn_right():
    _motor_move_in_direction(motor_control_config.Direction_t.RIGHT)


###############################################################################
# Function Name: stop_motors
# Description: Stops all motors.
###############################################################################

def stop_motors():
    _motor_move_in_direction(motor_control_config.Direction_t.STOP)


###############################################################################
# Function Name: move_at_speed
# Description: Moves the car at the user defined PWM duty cycles.
#              Used for more explicit control of motors
###############################################################################

def move_at_speed(left_pwm_duty, right_pwm_duty):
    _set_all_motors(
        duty_left_top=left_pwm_duty, 
        duty_left_bottom=left_pwm_duty, 
        duty_right_top=right_pwm_duty, 
        duty_right_bottom=right_pwm_duty
    )


###############################################################################
# Function Name: shutdown_motors
# Description: Stops all motors and shuts down the motor controller.
###############################################################################

def shutdown_motors():
    global motor_controller

    if motor_controller is not None:
        stop_motors()
        motor_controller.close()
        motor_controller = None


###############################################################################
# LOCAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: _motor_move_in_direction
# Description: Moves the car in the specified direction at the predefined PWM
#              duty cycle for that direction.
###############################################################################

def _motor_move_in_direction(direction):
    match direction:
        case motor_control_config.Direction_t.FORWARD:
            _set_all_motors(
                duty_left_top= motor_control_config.FORWARD_PWM_DUTY, 
                duty_left_bottom= motor_control_config.FORWARD_PWM_DUTY, 
                duty_right_top= motor_control_config.FORWARD_PWM_DUTY, 
                duty_right_bottom= motor_control_config.FORWARD_PWM_DUTY
            )

        case motor_control_config.Direction_t.BACKWARD:
            _set_all_motors(
                duty_left_top= motor_control_config.BACKWARD_PWM_DUTY, 
                duty_left_bottom= motor_control_config.BACKWARD_PWM_DUTY, 
                duty_right_top= motor_control_config.BACKWARD_PWM_DUTY, 
                duty_right_bottom= motor_control_config.BACKWARD_PWM_DUTY
            )

        case motor_control_config.Direction_t.LEFT:
            _set_all_motors(
                duty_left_top= motor_control_config.TURN_LOW_PWM_DUTY,
                duty_left_bottom= motor_control_config.TURN_LOW_PWM_DUTY,
                duty_right_top= motor_control_config.TURN_HIGH_PWM_DUTY, 
                duty_right_bottom= motor_control_config.TURN_HIGH_PWM_DUTY
            ) 

        case motor_control_config.Direction_t.RIGHT:
            _set_all_motors(
                duty_left_top= motor_control_config.TURN_HIGH_PWM_DUTY,
                duty_left_bottom= motor_control_config.TURN_HIGH_PWM_DUTY,
                duty_right_top= motor_control_config.TURN_LOW_PWM_DUTY, 
                duty_right_bottom= motor_control_config.TURN_LOW_PWM_DUTY
            )

        case motor_control_config.Direction_t.STOP:
            _set_all_motors(
                duty_left_top= motor_control_config.STOP_PWM_DUTY, 
                duty_left_bottom= motor_control_config.STOP_PWM_DUTY, 
                duty_right_top= motor_control_config.STOP_PWM_DUTY, 
                duty_right_bottom= motor_control_config.STOP_PWM_DUTY
            )

        case _: # Apparently Python doesn't have a default case for match statements, so "_" is used
            _set_all_motors(
                duty_left_top= motor_control_config.STOP_PWM_DUTY, 
                duty_left_bottom= motor_control_config.STOP_PWM_DUTY, 
                duty_right_top= motor_control_config.STOP_PWM_DUTY, 
                duty_right_bottom= motor_control_config.STOP_PWM_DUTY
            )


###############################################################################
# Function Name: _set_all_motors
# Description: Sets the PWM duty cycle for all motors.
###############################################################################

def _set_all_motors(duty_left_top, duty_left_bottom, duty_right_top, duty_right_bottom):
    _set_motor(
        in1_chnl=motor_control_config.LEFT_TOP_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=motor_control_config.LEFT_TOP_WHEEL_IN2_PWM_CHNL, 
        duty=duty_left_top
    )
    
    _set_motor(
        in1_chnl=motor_control_config.LEFT_BOTTOM_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=motor_control_config.LEFT_BOTTOM_WHEEL_IN2_PWM_CHNL, 
        duty=duty_left_bottom
    )
    
    _set_motor(
        in1_chnl=motor_control_config.RIGHT_TOP_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=motor_control_config.RIGHT_TOP_WHEEL_IN2_PWM_CHNL, 
        duty=duty_right_top
    )
    
    _set_motor(
        in1_chnl=motor_control_config.RIGHT_BOTTOM_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=motor_control_config.RIGHT_BOTTOM_WHEEL_IN2_PWM_CHNL,
        duty=duty_right_bottom
    )


###############################################################################
# Function Name: _set_motor
# Description: Sets the PWM duty cycle for a single motor based on the specified duty.
###############################################################################

def _set_motor(in1_chnl, in2_chnl, duty):
    if motor_controller is None:
        raise RuntimeError("Motor controller not initialized")
    
    if duty > 0:
        if duty > motor_control_config.MOTOR_CONTROLLER_ABSOLUTE_MAX_PWM_DUTY:
            duty = motor_control_config.MOTOR_CONTROLLER_ABSOLUTE_MAX_PWM_DUTY

        motor_controller.set_motor_pwm(in2_chnl, 0)
        motor_controller.set_motor_pwm(in1_chnl, duty)
    elif duty < 0:
        if abs(duty) > motor_control_config.MOTOR_CONTROLLER_ABSOLUTE_MAX_PWM_DUTY:
            duty = -motor_control_config.MOTOR_CONTROLLER_ABSOLUTE_MAX_PWM_DUTY

        motor_controller.set_motor_pwm(in1_chnl, 0)
        motor_controller.set_motor_pwm(in2_chnl, abs(duty))
    else:
        motor_controller.set_motor_pwm(in1_chnl, motor_control_config.STOP_PWM_DUTY)
        motor_controller.set_motor_pwm(in2_chnl, motor_control_config.STOP_PWM_DUTY)