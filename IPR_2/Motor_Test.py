###############################################################################
# File Name: Motor_Test.py
# Description: 
###############################################################################

import Freenove_Libraries.pca9685 as pca9685
import time
from enum import Enum

MOTOR_CONTROLLER_I2C_ADDRESS = 0x40
MOTOR_CONTROLLER_PWM_FREQUENCY = 50 #Hz

LEFT_TOP_WHEEL_IN1_PWM_CHNL = 0
LEFT_TOP_WHEEL_IN2_PWM_CHNL = 1

LEFT_BOTTOM_WHEEL_IN1_PWM_CHNL = 3
LEFT_BOTTOM_WHEEL_IN2_PWM_CHNL = 2

RIGHT_TOP_WHEEL_IN1_PWM_CHNL = 6
RIGHT_TOP_WHEEL_IN2_PWM_CHNL = 7

RIGHT_BOTTOM_WHEEL_IN1_PWM_CHNL = 4
RIGHT_BOTTOM_WHEEL_IN2_PWM_CHNL = 5

FORWARD_PWM_DUTY = 2000
TURN_PWM_DUTY = 1000
STOP_PWM_DUTY = 0
MOTOR_CONTROLLER_MAX_PWM_DUTY = 4095

class Direction_t(Enum):
    FORWARD = 0
    BACKWARD = 1
    LEFT = 2
    RIGHT = 3
    STOP = 4
    INVALID = 5

motor_controller = None

def main():
    setup_motor_controller()

    motor_move_in_direction(Direction_t.FORWARD)
    time.sleep(2)

    motor_move_in_direction(Direction_t.BACKWARD)
    time.sleep(2)

    motor_move_in_direction(Direction_t.LEFT)
    time.sleep(2)

    motor_move_in_direction(Direction_t.RIGHT)
    time.sleep(2)

    motor_move_in_direction(Direction_t.STOP)
    time.sleep(2)

    shutdown_motors()


def setup_motor_controller():
    global motor_controller
    motor_controller = pca9685.PCA9685(MOTOR_CONTROLLER_I2C_ADDRESS, debug=True)
    motor_controller.set_pwm_freq(MOTOR_CONTROLLER_PWM_FREQUENCY)


def motor_move_in_direction(direction):
    match direction:
        case Direction_t.FORWARD:
            set_all_motors(
                duty_left_top= FORWARD_PWM_DUTY, 
                duty_left_bottom= FORWARD_PWM_DUTY, 
                duty_right_top= FORWARD_PWM_DUTY, 
                duty_right_bottom= FORWARD_PWM_DUTY
            )

        case Direction_t.BACKWARD:
            set_all_motors(
                duty_left_top= -FORWARD_PWM_DUTY, 
                duty_left_bottom= -FORWARD_PWM_DUTY, 
                duty_right_top= -FORWARD_PWM_DUTY, 
                duty_right_bottom= -FORWARD_PWM_DUTY
            )

        case Direction_t.LEFT:
            set_all_motors(
                duty_left_top= -TURN_PWM_DUTY, # May change to STOP_PWM_DUTY for more gentle turn
                duty_left_bottom= -TURN_PWM_DUTY, # May change to STOP_PWM_DUTY for more gentle turn
                duty_right_top= TURN_PWM_DUTY, 
                duty_right_bottom= TURN_PWM_DUTY
            ) 

        case Direction_t.RIGHT:
            set_all_motors(
                duty_left_top= TURN_PWM_DUTY, # May change to STOP_PWM_DUTY for more gentle turn
                duty_left_bottom= TURN_PWM_DUTY, # May change to STOP_PWM_DUTY for more gentle turn
                duty_right_top= -TURN_PWM_DUTY, 
                duty_right_bottom= -TURN_PWM_DUTY
            )

        case Direction_t.STOP:
            set_all_motors(
                duty_left_top= STOP_PWM_DUTY, 
                duty_left_bottom= STOP_PWM_DUTY, 
                duty_right_top= STOP_PWM_DUTY, 
                duty_right_bottom= STOP_PWM_DUTY
            )

        case _: # Apparently python doesn't have a default case for match statements, so "_" is used
            set_all_motors(
                duty_left_top=STOP_PWM_DUTY, 
                duty_left_bottom=STOP_PWM_DUTY, 
                duty_right_top=STOP_PWM_DUTY, 
                duty_right_bottom=STOP_PWM_DUTY)


def set_all_motors(duty_left_top, duty_left_bottom, duty_right_top, duty_right_bottom):
    set_motor(
        in1_chnl=LEFT_TOP_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=LEFT_TOP_WHEEL_IN2_PWM_CHNL, duty=duty_left_top
    )
    
    set_motor(
        in1_chnl=LEFT_BOTTOM_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=LEFT_BOTTOM_WHEEL_IN2_PWM_CHNL, duty=duty_left_bottom
    )
    
    set_motor(
        in1_chnl=RIGHT_TOP_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=RIGHT_TOP_WHEEL_IN2_PWM_CHNL, duty=duty_right_top
    )
    
    set_motor(
        in1_chnl=RIGHT_BOTTOM_WHEEL_IN1_PWM_CHNL, 
        in2_chnl=RIGHT_BOTTOM_WHEEL_IN2_PWM_CHNL, duty=duty_right_bottom
    )


def set_motor(in1_chnl, in2_chnl, duty):
    if duty > 0:
        if duty > MOTOR_CONTROLLER_MAX_PWM_DUTY:
            duty = MOTOR_CONTROLLER_MAX_PWM_DUTY

        motor_controller.set_motor_pwm(in1_chnl, 0)
        motor_controller.set_motor_pwm(in2_chnl, duty)
    elif duty < 0:
        if abs(duty) > MOTOR_CONTROLLER_MAX_PWM_DUTY:
            duty = -MOTOR_CONTROLLER_MAX_PWM_DUTY

        motor_controller.set_motor_pwm(in2_chnl, 0)
        motor_controller.set_motor_pwm(in1_chnl, abs(duty))
    else:
        motor_controller.set_motor_pwm(in1_chnl, STOP_PWM_DUTY)
        motor_controller.set_motor_pwm(in2_chnl, STOP_PWM_DUTY)


def shutdown_motors():
    set_all_motors(STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY)
    motor_controller.close()


if __name__ == "__main__":
    main()