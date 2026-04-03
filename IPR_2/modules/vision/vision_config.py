###############################################################################
# File Name: vision_config.py
# Description: Constants for the vision module
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# Library Imports
import numpy as np


###############################################################################
# CONSTANTS
###############################################################################

# Whether to display debug frames (e.g., edge detection, lane markings) during processing
SHOW_DEBUG_FRAMES = False

# EMA smoothing factor for left and right lanes
LANE_EMA_ALPHA = 0.36

# Default ROI points (these will be overwritten if calibration is enabled)
X1 = 94
Y1 = 196

X2 = 546
Y2 = 196

# Resolution that the image will be resized to for processing (to speed up processing)
PROCESSING_WIDTH = 640
PROCESSING_HEIGHT = 360

# Filtering parameters
# Gaussian blur parameters
BLUR_KERNEL_SIZE = 5 # Size of block that goes through each pixel and calculates the weighted average of the surrounding pixels. The larger the kernel size, the more blurred the image will be.
SIGMA_BLUR_CONTROL = 0

# Morphological operation parameters
# Size of the kernel used for morphological operations (e.g., closing to connect dashed lane markings)
MORPH_KERNEL_SIZE = 3

# Canny edge detection thresholds
CANNY_LOW_THRESHOLD = 30
CANNY_HIGH_THRESHOLD = 150

# Hough transform parameters
HOUGH_RHO = 1 # Distance resolution of candidate lines (accumulator rows)
HOUGH_THETA = np.pi / 180 # Defines interval of how much to increment theta in line calculation.
HOUGH_THRESHOLD = 30 # Minimum number of supporting edge pixels required before a line is considered valid.
HOUGH_MIN_LINE_LEN = 50 # Minimum length (in pixels) required for a detected line segment.
HOUGH_MAX_LINE_GAP = 200 # Maximum allowed gap between line segments that can be connected into one continuous line.

# Lane filtering parameters
MIN_SLOPE = 0.5
MAX_SLOPE = 3.5

# Lane tracking parameters
# Maximum number of consecutive frames a lane can be missed before it's considered lost
MAX_MISSED_FRAMES = 3 

# Maximum distance in CM that the car should react and stop for
MAX_REACTION_DISTANCE = 50