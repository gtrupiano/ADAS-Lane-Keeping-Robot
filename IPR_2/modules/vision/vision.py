###############################################################################
# File Name: vision.py
# Description: Main application logic for the vision module, which includes 
#              lane detection and tracking.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import modules.vision.vision_config as vision_config
import modules.camera.camera as camera

# Library Imports
import cv2
import numpy as np

###############################################################################
# GLOBAL VARIABLES
###############################################################################

# Last good left and right lanes
last_left_lane = None
last_right_lane = None

# Number of consecutive frames each lane has been missing
left_lane_missing_count = 0
right_lane_missing_count = 0

# Running averages for left and right lanes
running_average_left_lane = None
running_average_right_lane = None

# Frame at different stages of processing
filtered_frame = None
frame_edges = None
roi_edges = None

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: calibrate_ROI_points
# Description: Allows the user to calibrate the ROI points by displaying a 
#              window with trackbars for each of the four points that define 
#              the ROI. The user can adjust the trackbars while viewing the 
#              resulting ROI in real time until they are satisfied with 
#              the placement of the ROI, at which point they can press the ESC
#              key to save those points and exit the calibration window.
###############################################################################

def calibrate_ROI_points():
    # define a null callback function for Trackbar
    def null(x):
        pass

    # Create a window for the trackbars to be displayed in
    cv2.namedWindow("ROI")

    # Creating trackbars for the ROI points
    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("X1", "ROI", vision_config.X1, vision_config.PROCESSING_WIDTH, null)
    cv2.createTrackbar("Y1", "ROI", vision_config.Y1, vision_config.PROCESSING_HEIGHT, null)

    cv2.createTrackbar("X2", "ROI", vision_config.X2, vision_config.PROCESSING_WIDTH, null)
    cv2.createTrackbar("Y2", "ROI", vision_config.Y2, vision_config.PROCESSING_HEIGHT, null)

    # Loop to continuously update the ROI frame based on the trackbar positions
    while True:
        # Resizes and fetches the current frame
        _, frame, validity = camera.fetch_frame()

        # Checks whether the capturing of the frame was successful. If not, exits the program since the camera is not working.
        if validity is False:
            break

        # Fetching trackbar positions for ROI points
        vision_config.X1 = cv2.getTrackbarPos("X1", "ROI")
        vision_config.Y1 = cv2.getTrackbarPos("Y1", "ROI")
        vision_config.X2 = cv2.getTrackbarPos("X2", "ROI")
        vision_config.Y2 = cv2.getTrackbarPos("Y2", "ROI")

        # Applying the ROI mask to the current frame to show the user how the ROI looks in real time as they adjust the trackbars
        roi_frame = apply_ROI(frame)

        cv2.imshow("ROI", roi_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(10)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    # Prints the ROI points that were set by the user
    # NOTE: These points will need to be manually updated in vision_config.py if the user wants to use those same points in future runs
    print("Point 1 and 2 overwritten with:")
    print(f"Point 1: {vision_config.X1},{vision_config.Y1}")
    print(f"Point 2: {vision_config.X2},{vision_config.Y2}")
    print()

    cv2.destroyWindow("ROI")


###############################################################################
# Function Name: detect_lanes
# Description: Detects lanes in the input frame and returns a frame with
#              the detected lanes drawn on it, as well as the coordinates 
#              of the left and right lanes.
###############################################################################

def detect_lanes(frame):
    global filtered_frame
    global frame_edges
    global roi_edges

    gray_frame = cv2.cvtColor(
        src=frame,
        code=cv2.COLOR_BGR2GRAY
    )

    gray_frame[gray_frame > 220] = 0

    # Blurs the image to reduce noise for better edge detection results
    filtered_frame = cv2.GaussianBlur(
        src=gray_frame, 
        ksize=(vision_config.BLUR_KERNEL_SIZE, vision_config.BLUR_KERNEL_SIZE),
        sigmaX=vision_config.SIGMA_BLUR_CONTROL,
        sigmaY=vision_config.SIGMA_BLUR_CONTROL
        )

    # Detects edges in the blurred image using Canny edge detection
    frame_edges = cv2.Canny(
        image=filtered_frame, 
        threshold1=vision_config.CANNY_LOW_THRESHOLD,
        threshold2=vision_config.CANNY_HIGH_THRESHOLD
        )

    # Applies edges that are within ROI
    roi_edges = apply_ROI(frame_edges)

    # Connect dashed lane markings by filling small gaps in edges
    kernel = np.ones((vision_config.MORPH_KERNEL_SIZE, vision_config.MORPH_KERNEL_SIZE), np.uint8)
    roi_edges = cv2.morphologyEx(
        src=roi_edges,
        op=cv2.MORPH_CLOSE,
        kernel=kernel
    )

    # Fetches straight line segments from edges of frame
    hough_lines = hough_transform(roi_edges)

    # Filter out lines that have non ideal slopes
    left_lane, right_lane = filter_lines(
        lines=hough_lines, 
        min_slope=vision_config.MIN_SLOPE, 
        max_slope=vision_config.MAX_SLOPE, 
        frame_height=vision_config.PROCESSING_HEIGHT,
    )

    # Apply an EMA to the left and right lane objects to smooth out the lane detection over time
    averaged_left_lane, averaged_right_lane = average_left_and_right_lanes(left_lane, right_lane)

    # Draw lines and overly onto input frame
    lanes_on_frame = draw_lines_on_frame(
        frame=frame,
        lines=[averaged_left_lane, averaged_right_lane]
        )
    
    return lanes_on_frame, averaged_left_lane, averaged_right_lane


###############################################################################
# Function Name: apply_ROI
# Description: Applies a Region of Interest (ROI) mask to the edge-detected frame.
###############################################################################

def apply_ROI(frame_edges):
    r"""
    (x1,y1) ------- (x4,y4)
     \               /
      \             /
       (x2,y2) (x3,y3)
    """

    # Fetching global variables for ROI points and dimensions of frame
    X1, Y1, X2, Y2 = vision_config.X1, vision_config.Y1, vision_config.X2, vision_config.Y2

    # Coordinates of the vertices for the polygon that will be used as the ROI for lanes only.
    X3 = 0
    Y3 = vision_config.PROCESSING_HEIGHT

    X4 = vision_config.PROCESSING_WIDTH
    Y4 = vision_config.PROCESSING_HEIGHT

    # Define the vertices of the polygon that will be used to mask the ROI
    vertices = np.array([[
        (X1, Y1),
        (X2, Y2),
        (X4, Y4),
        (X3, Y3)
    ]], dtype=np.int32)

    # Create a black image of the same size as the edge-detected image
    roi = np.zeros((vision_config.PROCESSING_HEIGHT, vision_config.PROCESSING_WIDTH), dtype=np.uint8)

    # Fill the region inside the vertices with white (255).
    cv2.fillPoly(
        img=roi, 
        pts=vertices, 
        color=255
        )

    # Perform a bitwise AND operation between the edge-detected image and the
    # mask to keep only the edges that are within the ROI.
    masked_edges = cv2.bitwise_and(
        frame_edges,
        frame_edges,
        mask=roi
        )
    
    return masked_edges


###############################################################################
# Function Name: hough_transform
# Description: Applies the Probabilistic Hough Transform to detect straight line segments
#              from the edge image.
#
#              This calculation determines where a line would need to be located in order
#              to pass through that edge pixel at the given angle.
#              
#              A line is defined by:
#              x*cos(theta) + y*sin(theta) = rho
#              
#              Theta: The orientation (angle) of the line
#              Rho: Determines the position of the line by using the shortest perpendicular distance from the image origin to that line.
#              
#              For each edge pixel, all theta (0-180) are input into the line equation one at a time. With each theta, a rho is computed giving the pair (theta,rho).
#              The pair (theta,rho) defines ONE infinite straight line.
#
#              All N pairs which give N lines (determined by the theta interval, every 1, 5, or 10 degrees). 
# 
#              An array exists which keeps track of each (theta,rho). After all edge pixels are completed,
#              the (theta,rho) with the most votes are the ones that indicate a line exists.
#
#              Then OpenCV converts those detected lines into line segments:
#              return (x1, y1, x2, y2)
###############################################################################

def hough_transform(masked_edges):
    # Perform Probabilistic Hough Transform
    # Returns detected line segments as endpoints (x1, y1, x2, y2)
    hough_lines = cv2.HoughLinesP(
        image=masked_edges,
        rho=vision_config.HOUGH_RHO,
        theta=vision_config.HOUGH_THETA,
        threshold=vision_config.HOUGH_THRESHOLD,
        minLineLength=vision_config.HOUGH_MIN_LINE_LEN,
        maxLineGap=vision_config.HOUGH_MAX_LINE_GAP
    )

    return hough_lines


###############################################################################
# Function Name: filter_lines
# Description: 
###############################################################################

def filter_lines(lines, min_slope, max_slope, frame_height):
    global last_left_lane
    global last_right_lane
    global left_lane_missing_count
    global right_lane_missing_count

    # No lines found from Hough transform
    # Should keep using the last known good lanes for a few frames before resetting and looking for new lanes again
    if lines is None:
        if last_left_lane is not None:
            left_lane_missing_count += 1

        if left_lane_missing_count > vision_config.MAX_MISSED_FRAMES:
            last_left_lane = None
            left_lane_missing_count = 0

        if last_right_lane is not None:
            right_lane_missing_count += 1

        if right_lane_missing_count > vision_config.MAX_MISSED_FRAMES:
            last_right_lane = None
            right_lane_missing_count = 0
            
        return (last_left_lane, last_right_lane)
    
    left_lines_slope = []
    left_lines_intercept = []

    right_lines_slope = []
    right_lines_intercept = []

    left_lane = None
    right_lane = None

    # Fetching slopes of all lines and assigning them to left and right
    # These aren't the final lanes, two lines will be created from the slopes
    for line in lines:
        x1, y1, x2, y2 = line[0]

        # Calculate slope
        delta_y = y2 - y1
        delta_x = x2 - x1

        # Avoid divide by zero
        if delta_x != 0:
            slope = delta_y / delta_x

            # Concerned with magnitude
            abs_slope = abs(slope)

            # Slope is within range of min and max slope
            if min_slope < abs_slope < max_slope:
                # Calculating intercept
                intercept = y1 - (slope * x1)

                # Indicates left lane due to top left corner being (0,0)
                if slope < 0:
                    left_lines_slope.append(slope)
                    left_lines_intercept.append(intercept)
                else: # slope > 0
                    right_lines_slope.append(slope)
                    right_lines_intercept.append(intercept)
    
    # Creating two lines (one left and one right) based on the many lines 
    # Averaging the slopes and using the starting intercepts to start drawing lines.
    y_bottom = frame_height
    y_top = int(frame_height * 0.62)

    # Finding average of slopes and intercepts for both right and left lines
    # The constructing left and right lines based on those averages.
    if left_lines_slope:
        m_avg = np.median(left_lines_slope)
        b_avg = np.median(left_lines_intercept)

        x_bottom = int((y_bottom - b_avg) / m_avg)
        x_top = int((y_top - b_avg) / m_avg)

        left_lane = (x_bottom, y_bottom, x_top, y_top)

    if right_lines_slope:
        m_avg = np.median(right_lines_slope)
        b_avg = np.median(right_lines_intercept)

        x_bottom = int((y_bottom - b_avg) / m_avg)
        x_top = int((y_top - b_avg) / m_avg)

        right_lane = (x_bottom, y_bottom, x_top, y_top)
    
    if left_lane is not None and right_lane is not None:
        if left_lane[0] >= right_lane[0]:
            left_lane = None
            right_lane = None

     # Left lane updating to keep last detected lane for a few frames if no new lanes are found before resetting and looking for new lanes again
    if left_lane is not None:
        last_left_lane = left_lane
        left_lane_missing_count = 0
    else:
        if last_left_lane is not None:
            left_lane_missing_count += 1

        if left_lane_missing_count > vision_config.MAX_MISSED_FRAMES:
            last_left_lane = None
            left_lane_missing_count = 0

        left_lane = last_left_lane

     # Right lane updating to keep last detected lane for a few frames if no new lanes are found before resetting and looking for new lanes again
    if right_lane is not None:
        last_right_lane = right_lane
        right_lane_missing_count = 0
    else:
        if last_right_lane is not None:
            right_lane_missing_count += 1

        if right_lane_missing_count > vision_config.MAX_MISSED_FRAMES:
            last_right_lane = None
            right_lane_missing_count = 0

        right_lane = last_right_lane

    return (left_lane, right_lane)


###############################################################################
# Function Name: average_left_and_right_lanes
# Description: Applying an EMA on the both the left and right lane objects.
#              This formula is: 
#              filtered_value = (ALPHA * current_val) + ((1 - ALPHA) * running_average)
###############################################################################

def average_left_and_right_lanes(left_lane, right_lane):
    global running_average_left_lane
    global running_average_right_lane

    averaged_left_lane = None
    averaged_right_lane = None
    
    # Applying an EMA to the left lane
    if left_lane is not None:
        left_lane_np = np.array(left_lane, dtype=np.float32)

        if running_average_left_lane is not None:
            averaged_left_lane = (vision_config.ALPHA * left_lane_np) + ((1 - vision_config.ALPHA) * running_average_left_lane)
        else:
            averaged_left_lane = left_lane_np

        running_average_left_lane = averaged_left_lane
    else:
        running_average_left_lane = None
        averaged_left_lane = None

    # Applying an EMA to the right lane
    if right_lane is not None:
        right_lane_np = np.array(right_lane, dtype=np.float32)

        if running_average_right_lane is not None:
            averaged_right_lane = (vision_config.ALPHA * right_lane_np) + ((1 - vision_config.ALPHA) * running_average_right_lane)
        else:
            averaged_right_lane = right_lane_np

        running_average_right_lane = averaged_right_lane
    else:
        running_average_right_lane = None
        averaged_right_lane = None

    # Converting the averaged lanes back to tuples of integers for drawing on the frame
    if averaged_left_lane is not None:
        averaged_left_lane = tuple(averaged_left_lane.astype(int))

    if averaged_right_lane is not None:
        averaged_right_lane = tuple(averaged_right_lane.astype(int))

    return averaged_left_lane, averaged_right_lane


###############################################################################
# Function Name: draw_lines_on_frame
# Description: Draws the detected lane lines on the input frame
###############################################################################

def draw_lines_on_frame(frame, lines):
    # Create a blank RGB image to draw the Hough line segments

    line_image = np.zeros(
        shape=(vision_config.PROCESSING_HEIGHT, vision_config.PROCESSING_WIDTH, 3),
        dtype=np.uint8
        )

    # Draw each detected line segment (if any)
    if lines is not None:
        for line in lines:
            if line is not None:
                x1, y1, x2, y2 = line
                cv2.line(
                    img=line_image,
                    pt1=(x1, y1),
                    pt2=(x2, y2),
                    color=(255, 0, 0),
                    thickness=5
                    )

    # Overlay the line image on the original image
    result = cv2.addWeighted(
        src1=frame, 
        alpha=0.8, 
        src2=line_image, 
        beta=1.0, 
        gamma=0.0
        )
    
    return result