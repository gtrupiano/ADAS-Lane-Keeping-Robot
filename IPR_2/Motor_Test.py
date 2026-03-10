import pca9685
import time
from enum import Enum

MOTOR_CONTROLLER_I2C_ADDRESS = 0x40
MOTOR_CONTROLLER_PWM_FREQUENCY = 50 #Hz

LEFT_TOP_WHEEL_CCW_PWM_CHNL = 0
LEFT_TOP_WHEEL_CW_PWM_CHNL = 1

LEFT_BOTTOM_WHEEL_CCW_PWM_CHNL = 3
LEFT_BOTTOM_WHEEL_CW_PWM_CHNL = 2

RIGHT_TOP_WHEEL_CCW_PWM_CHNL = 6
RIGHT_TOP_WHEEL_CW_PWM_CHNL = 7

RIGHT_BOTTOM_WHEEL_CCW_PWM_CHNL = 4
RIGHT_BOTTOM_WHEEL_CW_PWM_CHNL = 5

FORWARD_PWM_DUTY = 2000
TURN_PWM_DUTY = 1000
STOP_PWM_DUTY = 0
BRAKE_PWM_DUTY = 4095

motor_controller = None

class Direction_t(Enum):
    FORWARD = 0
    BACKWARD = 1
    LEFT = 2
    RIGHT = 3
    STOP = 4
    INVALID = 5

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


def setup_motor_controller():
    global motor_controller
    motor_controller = pca9685.PCA9685(MOTOR_CONTROLLER_I2C_ADDRESS, debug=True)
    motor_controller.set_pwm_freq(MOTOR_CONTROLLER_PWM_FREQUENCY)


def motor_move_in_direction(direction):
    match direction:
        case Direction_t.FORWARD:
            set_all_motors(FORWARD_PWM_DUTY, FORWARD_PWM_DUTY, FORWARD_PWM_DUTY, FORWARD_PWM_DUTY)

        case Direction_t.BACKWARD:
            set_all_motors(-FORWARD_PWM_DUTY, -FORWARD_PWM_DUTY, -FORWARD_PWM_DUTY, -FORWARD_PWM_DUTY)

        case Direction_t.LEFT:
            set_all_motors(-TURN_PWM_DUTY, -TURN_PWM_DUTY, TURN_PWM_DUTY, TURN_PWM_DUTY) # May change to 0 for - more gentle turn

        case Direction_t.RIGHT:
            set_all_motors(TURN_PWM_DUTY, TURN_PWM_DUTY, -TURN_PWM_DUTY, -TURN_PWM_DUTY) # May change to 0 for - more gentle turn

        case Direction_t.STOP:
            set_all_motors(STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY)

        case _:
            set_all_motors(STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY, STOP_PWM_DUTY)


def set_all_motors(duty_left_top, duty_left_bottom, duty_right_top, duty_right_bottom):
    set_motor(LEFT_TOP_WHEEL_CCW_PWM_CHNL, LEFT_TOP_WHEEL_CW_PWM_CHNL, duty_left_top)
    set_motor(LEFT_BOTTOM_WHEEL_CCW_PWM_CHNL, LEFT_BOTTOM_WHEEL_CW_PWM_CHNL, duty_left_bottom)
    set_motor(RIGHT_TOP_WHEEL_CCW_PWM_CHNL, RIGHT_TOP_WHEEL_CW_PWM_CHNL, duty_right_top)
    set_motor(RIGHT_BOTTOM_WHEEL_CCW_PWM_CHNL, RIGHT_BOTTOM_WHEEL_CW_PWM_CHNL, duty_right_bottom)


def set_motor(ccw_chnl, cw_chnl, duty):
    if duty > 0:
        motor_controller.set_motor_pwm(ccw_chnl, 0)
        motor_controller.set_motor_pwm(cw_chnl, duty)
    elif duty < 0:
        motor_controller.set_motor_pwm(cw_chnl, 0)
        motor_controller.set_motor_pwm(ccw_chnl, abs(duty))
    else:
        motor_controller.set_motor_pwm(ccw_chnl, BRAKE_PWM_DUTY)
        motor_controller.set_motor_pwm(cw_chnl, BRAKE_PWM_DUTY)


if __name__ == "__main__":
    main()