###############################################################################
# File Name: light_detection.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports

# Library Imports
import numpy as np

###############################################################################
# CLASS DEFINITIONS
###############################################################################

# ColorHSVRange(
#   [hue_low, saturation_low, value_low], 
#   [hue_high, saturation_high, value_high]
# )
class ColorHSVRange:
    def __init__(self, lower, upper):
        self.lower = np.array(lower)
        self.upper = np.array(upper)

class Light:
    def __init__(self, color:str, hsv_range:ColorHSVRange, light_area_min):
        self.color = color.lower()
        self.hsv_range = hsv_range
        self.light_area_min = light_area_min

###############################################################################
# CONSTANTS
###############################################################################

# Calibratable values for HSV of red, yellow, and green
# NOTE: H only goes to 179
RED_HSV_RANGE = ColorHSVRange([0, 120, 120], [10, 255, 255])
YELLOW_HSV_RANGE = ColorHSVRange([20, 120, 147], [35, 255, 255])
GREEN_HSV_RANGE  = ColorHSVRange([40, 80, 80], [90, 255, 255])

# How large the area of the detected light needs to be before it should be detected
RED_AREA_MIN = 256
YELLOW_AREA_MIN = 64
GREEN_AREA_MIN = 128

# Constructed object to be used in the program
RED_LIGHT = Light("Red", RED_HSV_RANGE, RED_AREA_MIN)
YELLOW_LIGHT = Light("Yellow", YELLOW_HSV_RANGE, YELLOW_AREA_MIN)
GREEN_LIGHT = Light("Green", GREEN_HSV_RANGE, GREEN_AREA_MIN)


# Morphology values
MORPH_KERNEL_SIZE = 5
MORPH_KERNEL = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)