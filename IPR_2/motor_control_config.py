###############################################################################
# File Name: motor_control_config.py
# Description: Constants for the motor control module.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# Library Imports
from enum import Enum


###############################################################################
# CONSTANTS
###############################################################################

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

FORWARD_PWM_DUTY = 1500
TURN_PWM_DUTY = 1000
STOP_PWM_DUTY = 0
MOTOR_CONTROLLER_MAX_PWM_DUTY = 4095


###############################################################################
# CLASS DEFINITIONS
###############################################################################

# Motor controller constants
class Direction_t(Enum):
    FORWARD = 0
    BACKWARD = 1
    LEFT = 2
    RIGHT = 3
    STOP = 4
    INVALID = 5