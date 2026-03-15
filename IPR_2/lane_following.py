###############################################################################
# File Name: lane_following.py
# Description: 
###############################################################################

# File Imports
import vision_config
import motor_control

# Library Imports
import cv2
import numpy as np
import picamera2

# Pi Camera object
pi_camera = None

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
original_frame = None
resized_frame = None
filtered_frame = None
frame_edges = None
roi_edges = None
lanes_on_frame = None

def main():
    global original_frame
    global resized_frame
    global filtered_frame
    global frame_edges
    global roi_edges
    global lanes_on_frame

    configure_camera()

    motor_control.setup_motor_controller()
    
    roi_calibration_input = input("Calibrate ROI points (Yes / No)")
    roi_calibration_input = roi_calibration_input.lower()

    # Loop until valid input is received
    while roi_calibration_input != "yes" and roi_calibration_input != "no":
        roi_calibration_input = input("Invalid input. Calibrate ROI points (Yes / No)")
        roi_calibration_input = roi_calibration_input.lower()

    if roi_calibration_input.lower() == "yes":
        calibrate_ROI_points()

    while True:
        resized_frame, validity = fetch_frame()

        if validity is False:
            break
        
        # Detecting lanes and drawing them on the original frame
        lanes_on_frame, left_lane, right_lane = detect_lanes(resized_frame)

        # Determine movement based on the detected lanes and send commands to the motor controller
        determine_movement(left_lane, right_lane)

        # Display frames based on whether debug mode is enabled or not
        if vision_config.SHOW_DEBUG_FRAMES:
            cv2.imshow('Original Frame', original_frame)
            cv2.imshow('Resized Frame', resized_frame)
            cv2.imshow('Filtered Frame', filtered_frame)
            cv2.imshow('Edges Frame', frame_edges)
            cv2.imshow('ROI Edges Frame', roi_edges)
            cv2.imshow('Lanes', lanes_on_frame)
        else:
            cv2.imshow('Resized Frame', resized_frame)
            cv2.imshow('Lanes', lanes_on_frame)


        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(10)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    shutdown_peripherals()


###############################################################################
# Function Name: configure_camera
# Description: 
###############################################################################

def configure_camera():
    global pi_camera
    
    pi_camera  = picamera2.Picamera2()
    pi_camera.configure(
        pi_camera.create_preview_configuration(
            main={
                "size": (vision_config.CAMERA_WIDTH, vision_config.CAMERA_HEIGHT),
                "format": "RGB888"
            }
        )
    )
    pi_camera.start()

    # Capturing frame and checking whether it's valid
    frame = pi_camera.capture_array()
    if frame is None:
        print("Failed to capture frame")
        exit()


###############################################################################
# Function Name: calibrate_ROI_points
# Description: 
###############################################################################

def calibrate_ROI_points():
    # define a null callback function for Trackbar
    def null(x):
        pass

    cv2.namedWindow("ROI")

    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("X1", "ROI", vision_config.X1, vision_config.PROCESSING_WIDTH, null)
    cv2.createTrackbar("Y1", "ROI", vision_config.Y1, vision_config.PROCESSING_HEIGHT, null)

    cv2.createTrackbar("X2", "ROI", vision_config.X2, vision_config.PROCESSING_WIDTH, null)
    cv2.createTrackbar("Y2", "ROI", vision_config.Y2, vision_config.PROCESSING_HEIGHT, null)

    while True:
        frame, validity = fetch_frame()

        if validity is False:
            break

        # Fetching trackbar positions for ROI points
        vision_config.X1 = cv2.getTrackbarPos("X1", "ROI")
        vision_config.Y1 = cv2.getTrackbarPos("Y1", "ROI")
        vision_config.X2 = cv2.getTrackbarPos("X2", "ROI")
        vision_config.Y2 = cv2.getTrackbarPos("Y2", "ROI")

        roi_frame = apply_ROI(frame)

        cv2.imshow("ROI", roi_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(10)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    print("Point 1 and 2 overwritten with:")
    print(f"Point 1: {vision_config.X1},{vision_config.Y1}")
    print(f"Point 2: {vision_config.X2},{vision_config.Y2}")
    print()

    cv2.destroyWindow("ROI")


###############################################################################
# Function Name: fetch_frame
# Description: 
###############################################################################

def fetch_frame():
    global original_frame
    
    validity = False

    # Capturing frame and checking whether it's valid
    original_frame = pi_camera.capture_array()

    if original_frame is None:
        print("Failed to capture frame")
        return None, validity
    
    # Camera interprets colors as RGB, but OpenCV uses BGR, so the color spaces need to be converted
    original_frame = cv2.cvtColor(
        src=original_frame,
        code=cv2.COLOR_RGB2BGR
    )

    # Resize the original frame to the dimensions specified in vision_config for processing
    resized_frame = cv2.resize(
        original_frame,
        (vision_config.PROCESSING_WIDTH, vision_config.PROCESSING_HEIGHT),
        interpolation=cv2.INTER_AREA
    )

    validity = True

    return resized_frame, validity


###############################################################################
# Function Name: detect_lanes
# Description: 
###############################################################################

def detect_lanes(frame):
    global filtered_frame
    global frame_edges
    global roi_edges

    # Size of block that goes through each pixel and calculates the weighted average of the surrounding pixels. 
    # The larger the kernel size, the more blurred the image will be.
    filtered_frame = cv2.GaussianBlur(
        src=frame, 
        ksize=(vision_config.BLUR_KERNEL_SIZE, vision_config.BLUR_KERNEL_SIZE),
        sigmaX=vision_config.SIGMA_BLUR_CONTROL,
        sigmaY=vision_config.SIGMA_BLUR_CONTROL
        )

    frame_edges = cv2.Canny(
        image=filtered_frame, 
        threshold1=vision_config.CANNY_LOW_THRESHOLD,
        threshold2=vision_config.CANNY_HIGH_THRESHOLD
        )

    # Edges that are within the ROI
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
        hough_lines=hough_lines, 
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
# Description: 
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
    
    if left_lane is not None:
        left_lane_np = np.array(left_lane, dtype=np.float32)

        if running_average_left_lane is not None:
            averaged_left_lane = (vision_config.ALPHA * left_lane_np) + ((1 - vision_config.ALPHA) * running_average_left_lane)
        else:
            averaged_left_lane = left_lane_np

        running_average_left_lane = averaged_left_lane
    elif running_average_left_lane is not None:
        averaged_left_lane = running_average_left_lane
    else:
        running_average_left_lane = None

    if right_lane is not None:
        right_lane_np = np.array(right_lane, dtype=np.float32)

        if running_average_right_lane is not None:
            averaged_right_lane = (vision_config.ALPHA * right_lane_np) + ((1 - vision_config.ALPHA) * running_average_right_lane)
        else:
            averaged_right_lane = right_lane_np

        running_average_right_lane = averaged_right_lane
    elif running_average_right_lane is not None:
        averaged_right_lane = running_average_right_lane
    else:
        running_average_right_lane = None

    if averaged_left_lane is not None:
        averaged_left_lane = tuple(averaged_left_lane.astype(int))

    if averaged_right_lane is not None:
        averaged_right_lane = tuple(averaged_right_lane.astype(int))

    return averaged_left_lane, averaged_right_lane


###############################################################################
# Function Name: draw_lines_on_frame
# Description: 
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


###############################################################################
# Function Name: determine_movement
# Description: 
###############################################################################

def determine_movement(left_lane, right_lane):
    # If no lanes are detected, stop the motors and wait for the next frame
    if left_lane is None and right_lane is None:
        motor_control.stop_motors()
        return

    frame_center_x = vision_config.PROCESSING_WIDTH / 2
    estimated_half_lane_width = vision_config.PROCESSING_WIDTH * 0.25

    if left_lane is not None and right_lane is not None:
        # Average the x-coordinates of the bottom endpoints of the left and right lanes to get the lane center
        lane_center_x = int((left_lane[0] + right_lane[0]) / 2)
    elif left_lane is not None:
        # If only the left lane is detected, assume the lane center is a fixed distance to the right of the left lane
        lane_center_x = left_lane[0] + estimated_half_lane_width
    else:
        lane_center_x = right_lane[0] - estimated_half_lane_width

    error = lane_center_x - frame_center_x

    if error < -vision_config.CENTER_THRESHOLD:
        motor_control.turn_left()
    elif error > vision_config.CENTER_THRESHOLD:
        motor_control.turn_right()
    else:
        motor_control.move_forward()


###############################################################################
# Function Name: shutdown_peripherals
# Description: 
###############################################################################

def shutdown_peripherals():
    pi_camera.stop()
    pi_camera.close()

    motor_control.shutdown_motors()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()