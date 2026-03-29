###############################################################################
# File Name: motor_control_config.py
# Description: Constants for the motor control module.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports

# Library Imports
from enum import Enum


###############################################################################
# CONSTANTS
###############################################################################

MOTOR_CONTROLLER_I2C_ADDRESS = 0x40
MOTOR_CONTROLLER_PWM_FREQUENCY = 50 #Hz

# The PCA9685 has a 12-bit resolution for PWM duty cycle, so the maximum value is 4095
MOTOR_CONTROLLER_ABSOLUTE_MAX_PWM_DUTY = 4095

LEFT_TOP_WHEEL_IN1_PWM_CHNL = 0
LEFT_TOP_WHEEL_IN2_PWM_CHNL = 1

LEFT_BOTTOM_WHEEL_IN1_PWM_CHNL = 3
LEFT_BOTTOM_WHEEL_IN2_PWM_CHNL = 2

RIGHT_TOP_WHEEL_IN1_PWM_CHNL = 6
RIGHT_TOP_WHEEL_IN2_PWM_CHNL = 7

RIGHT_BOTTOM_WHEEL_IN1_PWM_CHNL = 4
RIGHT_BOTTOM_WHEEL_IN2_PWM_CHNL = 5

# Fastest PWM duty cycle that can be applied for realistic movement of the robot (calibratable)
BASE_PWM_DUTY = 1200

FORWARD_PWM_DUTY = 1200
BACKWARD_PWM_DUTY = -600
TURN_HIGH_PWM_DUTY = 2800
TURN_LOW_PWM_DUTY = 500
STOP_PWM_DUTY = 0


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