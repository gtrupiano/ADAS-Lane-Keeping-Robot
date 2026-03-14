###############################################################################
# File Name: vision_config.py
# Description: Constants for the vision module
###############################################################################

# Library Imports
import numpy as np

# Camera Parameters
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

# EMA smoothing factor
ALPHA = 0.005

# Default ROI points (these will be overwritten if calibration is enabled)
x1 = 1025
y1 = 505

x2 = 1863
y2 = 505

# Filtering parameters
# Gaussian blur parameters
BLUR_KERNEL_SIZE = 5
SIGMA_BLUR_CONTROL = 0

# Canny edge detection thresholds
CANNY_LOW_THRESHOLD = 50
CANNY_HIGH_THRESHOLD = 150

# Hough transform parameters
HOUGH_RHO = 1 # Distance resolution of candidate lines (accumulator rows)
HOUGH_THETA = np.pi / 180 # Defines interval of how much to increment theta in line calculation.
HOUGH_THRESHOLD = 30 # Minimum number of supporting edge pixels required before a line is considered valid.
HOUGH_MIN_LINE_LEN = 50 # Minimum length (in pixels) required for a detected line segment.
HOUGH_MAX_LINE_GAP = 200 # Maximum allowed gap between line segments that can be connected into one continuous line.

# Lane filtering parameters
MIN_SLOPE = 0.5
MAX_SLOPE = 2.5

# Centering parameters
CENTER_THRESHOLD = 200