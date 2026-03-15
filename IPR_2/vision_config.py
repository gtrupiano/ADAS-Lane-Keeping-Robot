###############################################################################
# File Name: vision_config.py
# Description: Constants for the vision module
###############################################################################

# Library Imports
import numpy as np

# Camera Parameters
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720

PROCESSING_WIDTH = 640
PROCESSING_HEIGHT = 360

SHOW_DEBUG_FRAMES = False

# EMA smoothing factor
ALPHA = 0.15

# Default ROI points (these will be overwritten if calibration is enabled)
X1 = 180
Y1 = 260

X2 = 460
Y2 = 260

# Filtering parameters
# Gaussian blur parameters
BLUR_KERNEL_SIZE = 5
SIGMA_BLUR_CONTROL = 0

# Morphological operation parameters
MORPH_KERNEL_SIZE = 3 # Size of the kernel used for morphological operations (e.g., closing to connect dashed lane markings)

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

# Lane tracking parameters
# Will allow the system to keep using the last known good lane lines for up to this many consecutive frames without finding new lines before it resets and starts looking for new lanes again.
MAX_MISSED_FRAMES = 3 

# Centering parameters
CENTER_THRESHOLD = 200