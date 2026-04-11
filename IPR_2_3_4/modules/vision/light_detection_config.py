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
from typing import List

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

class CalibrationPoint:
    def __init__(self, area, distance):
        self.area = area # Pixels
        self.distance = distance # Inches


###############################################################################
# CONSTANTS
###############################################################################

# Calibratable values for HSV of red, yellow, and green
# NOTE: H only goes to 179
RED_HSV_RANGE = ColorHSVRange([106, 183, 239], [133, 255, 255])
YELLOW_HSV_RANGE = ColorHSVRange([78, 207, 154], [109, 255, 255])
GREEN_HSV_RANGE  = ColorHSVRange([32, 84, 126], [69, 255, 255])

# How large the area of the detected light needs to be before it should be detected
RED_AREA_MIN = 128
YELLOW_AREA_MIN = 128
GREEN_AREA_MIN = 128

# Constructed object to be used in the program
RED_LIGHT = Light("Red", RED_HSV_RANGE, RED_AREA_MIN)
YELLOW_LIGHT = Light("Yellow", YELLOW_HSV_RANGE, YELLOW_AREA_MIN)
GREEN_LIGHT = Light("Green", GREEN_HSV_RANGE, GREEN_AREA_MIN)


# Morphology values
MORPH_KERNEL_SIZE = 3
MORPH_KERNEL = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)


# EMA smoothing factor for detected light area
LIGHT_AREA_EMA_ALPHA = 0.40


# Calibration table for interpolating area to distance
NUMBER_OF_CALIBRATION_POINTS = 8

CALIBRATION_TABLE = [
    CalibrationPoint(area=16, distance=16),
    CalibrationPoint(area=18, distance=14),
    CalibrationPoint(area=24, distance=11),
    CalibrationPoint(area=32, distance=9),
    CalibrationPoint(area=40, distance=7),
    CalibrationPoint(area=50, distance=5),
    CalibrationPoint(area=64, distance=3),
    CalibrationPoint(area=80, distance=2),
]