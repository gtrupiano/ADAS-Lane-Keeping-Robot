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
RED_HSV_RANGE = ColorHSVRange([114, 192, 167], [138, 255, 255])
YELLOW_HSV_RANGE = ColorHSVRange([87, 154, 190], [99, 255, 255])
GREEN_HSV_RANGE  = ColorHSVRange([59, 151, 113], [77, 255, 255])

# How large the area of the detected light needs to be before it should be detected
RED_AREA_MIN = 128
YELLOW_AREA_MIN = 128
GREEN_AREA_MIN = 128

# Constructed object to be used in the program
RED_LIGHT = Light("Red", RED_HSV_RANGE, RED_AREA_MIN)
YELLOW_LIGHT = Light("Yellow", YELLOW_HSV_RANGE, YELLOW_AREA_MIN)
GREEN_LIGHT = Light("Green", GREEN_HSV_RANGE, GREEN_AREA_MIN)


# Morphology values
DIlATE_KERNEL_SIZE = 5
DILATE_KERNEL = np.ones((DIlATE_KERNEL_SIZE, DIlATE_KERNEL_SIZE), np.uint8)

ERODE_KERNEL_SIZE = 5
ERODE_KERNEL = np.ones((ERODE_KERNEL_SIZE, ERODE_KERNEL_SIZE), np.uint8)


# Calibration tables for interpolating area to distance
RED_CALIBRATION_TABLE = [
    CalibrationPoint(area=864, distance=12),
    CalibrationPoint(area=1000, distance=11),
    CalibrationPoint(area=1120, distance=10),
    CalibrationPoint(area=1300, distance=9),
    CalibrationPoint(area=1590, distance=8),
    CalibrationPoint(area=1875, distance=7),
    CalibrationPoint(area=2500, distance=6),
    CalibrationPoint(area=3400, distance=5),
    CalibrationPoint(area=4750, distance=4),
]

YELLOW_CALIBRATION_TABLE = [
    CalibrationPoint(area=410, distance=12),
    CalibrationPoint(area=464, distance=11),
    CalibrationPoint(area=535, distance=10),
    CalibrationPoint(area=664, distance=9),
    CalibrationPoint(area=860, distance=8),
    CalibrationPoint(area=1225, distance=7),
    CalibrationPoint(area=1600, distance=6),
    CalibrationPoint(area=2350, distance=5),
    CalibrationPoint(area=3200, distance=4),
]

GREEN_CALIBRATION_TABLE = [
    CalibrationPoint(area=380, distance=12),
    CalibrationPoint(area=441, distance=11),
    CalibrationPoint(area=506, distance=10),
    CalibrationPoint(area=576, distance=9),
    CalibrationPoint(area=702, distance=8),
    CalibrationPoint(area=900, distance=7),
    CalibrationPoint(area=1122, distance=6),
    CalibrationPoint(area=1564, distance=5),
    CalibrationPoint(area=2310, distance=4),
]

NUMBER_OF_RED_CALIBRATION_POINTS = len(RED_CALIBRATION_TABLE) - 1
NUMBER_OF_YELLOW_CALIBRATION_POINTS = len(YELLOW_CALIBRATION_TABLE) - 1
NUMBER_OF_GREEN_CALIBRATION_POINTS = len(GREEN_CALIBRATION_TABLE) - 1


# EMA smoothing factor for detected light area
LIGHT_AREA_EMA_ALPHA = 0.1

# Inches
LED_STOPPING_DISTANCE = 11.9