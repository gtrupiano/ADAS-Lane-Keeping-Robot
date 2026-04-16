###############################################################################
# File Name: control_config.py
# Description: Constants for the control module.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports

# Library Imports


###############################################################################
# CONSTANTS
###############################################################################

# Centering parameter
# Threshold for determining if the vehicle is centered in the lane (in pixels)
MIN_ERROR_THRESHOLD = 2

# Maximum lane center to frame center error (in pixels) for mapping to a PWM duty cycle.
MAX_LANE_TO_FRAME_CENTER_ERROR = 120.0

#
REVERSE_LIMIT = 10