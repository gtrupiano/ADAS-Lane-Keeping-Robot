###############################################################################
# File Name: IPR_2.py
# Description: 
###############################################################################

# Library Imports
import cv2
import numpy as np
#import picamera2

# Used to let the system work with both PiCamera and normal webcam
using_pi_camera = None

pi_camera = None
camera = None

# Last good left and right lanes
last_left_lane = None
last_right_lane = None

# Running averages for left and right lanes
running_average_left_lane = None
running_average_right_lane = None

ALPHA = 0.1

# Default ROI points (these will be overwritten if calibration is enabled)
x1 = 400
y1 = 350

x2 = 550
y2 = 350

def main():
    w, h = configure_camera()
    
    roi_calibration = input("Calibrate ROI points (Yes / No)")

    if roi_calibration.lower() == "yes":
        calibrate_ROI_points(w, h)

    while True:
        if using_pi_camera:
            frame = pi_camera.capture_array()

            if frame is None:
                print("Can't recieve frame")
                break
            
            # 0 is normal, 1 is flipped over y axis
            frame = cv2.flip(frame, 1)
        else:
            ret, frame = camera.read()

            if not ret:
                print("Can't recieve frame")
                break

            # 0 is normal, 1 is flipped over y axis
            frame = cv2.flip(frame, 1)
        
        lanes_in_frame = detect_lanes(frame)

        cv2.imshow('Camera', lanes_in_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(100)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    if using_pi_camera:
        pi_camera.stop()
        pi_camera.close()
    else:
        camera.release()

    cv2.destroyAllWindows()


###############################################################################
# Function Name: configure_camera
# Description: 
###############################################################################

def configure_camera():
    global using_pi_camera
    global pi_camera
    global camera

    using_pi_cam_response = input("Use PiCamera (Yes / No)")

    if using_pi_cam_response.lower() == "yes":
        pi_camera  = picamera2.Picamera2()
        pi_camera.configure(
            pi_camera.create_preview_configuration(
                main={"size": (640, 480)}
                )
        )
        pi_camera.start()

        # Capturing frame and checking whether it's valid
        frame = pi_camera.capture_array()
        if frame is None:
            print("Failed to capture frame")
            exit()

        using_pi_camera = True
    else: # using_pi_cam_response.lower() == "no":
        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            print("Can't open camera")
            exit()
        
        ret, frame = camera.read()

        if not ret:
            print("Can't recieve frame. Ending")
            exit()

        using_pi_camera = False

    # Dimensions of image
    h = frame.shape[0]
    w = frame.shape[1]
    
    return w, h


###############################################################################
# Function Name: calibrate_ROI_points
# Description: 
###############################################################################

def calibrate_ROI_points(w, h):
    global x1, y1, x2, y2
    global using_pi_camera

    # define a null callback function for Trackbar
    def null(x):
        pass

    cv2.namedWindow("ROI")

    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("x1", "ROI", 400, w, null)
    cv2.createTrackbar("y1", "ROI", 350, h, null)

    cv2.createTrackbar("x2", "ROI", 550, w, null)
    cv2.createTrackbar("y2", "ROI", 350, h, null)

    while True:
        # Capturing frame and checking whether it's valid
        if using_pi_camera:
            frame = pi_camera.capture_array()

            if frame is None:
                print("Failed to capture frame")
                break
            
            # 0 is normal, 1 is flipped over y axis
            frame = cv2.flip(frame, 1)
        else:
            ret, frame = camera.read()

            if not ret:
                print("Can't recieve frame")
                break
            
            # 0 is normal, 1 is flipped over y axis
            frame = cv2.flip(frame, 1)
            
        x1 = cv2.getTrackbarPos("x1", "ROI")
        y1 = cv2.getTrackbarPos("y1", "ROI")
        x2 = cv2.getTrackbarPos("x2", "ROI")
        y2 = cv2.getTrackbarPos("y2", "ROI")

        roi_frame = apply_ROI(frame)

        cv2.imshow("ROI", roi_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(100)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    print("Point 1 and 2 overwritten with")
    print(f"Point 1: {x1},{y1}")
    print(f"Point 2: {x2},{y2}")
    print()

    cv2.destroyWindow("ROI")


###############################################################################
# Function Name: detect_lanes
# Description: 
###############################################################################

def detect_lanes(frame):
    gray_image = cv2.cvtColor(
        src=frame,
        code=cv2.COLOR_BGR2GRAY
        )
    
    # Size of block that goes through each pixel and calculates the weighted average of the surrounding pixels. 
    # The larger the kernel size, the more blurred the image will be.
    KERNAL_SIZE = 5
    SIGMA_BLUR_CONTROL = 0
    filtered_frame = cv2.GaussianBlur(
        src=gray_image, 
        ksize=(KERNAL_SIZE, KERNAL_SIZE),
        sigmaX=SIGMA_BLUR_CONTROL,
        sigmaY=SIGMA_BLUR_CONTROL
        )

    LOW_THRESHOLD = 50
    HIGH_THRESHOLD = 150
    frame_edges = cv2.Canny(
        image=filtered_frame, 
        threshold1=LOW_THRESHOLD,
        threshold2=HIGH_THRESHOLD
        )

    # Edges that are within the ROI
    masked_edges = apply_ROI(frame_edges)

    # # Connect dashed lane markings by filling small gaps in edges
    # kernel = np.ones((5, 5), np.uint8)
    # masked_edges = cv2.morphologyEx(
    #     src=masked_edges,
    #     op=cv2.MORPH_CLOSE,
    #     kernel=kernel
    # )

    # Fetches straight line segments from edges of frame
    hough_lines = hough_transform(masked_edges)

    # Filter out lines that have non ideal slopes
    left_lane, right_lane = filter_lines(hough_lines, 0.5, 2.5, frame.shape[0])

    averaged_left_lane, averaged_right_lane = average_left_and_right_lanes(left_lane, right_lane)

    # Draw lines and overly onto input frame
    result = draw_lines_on_frame(
        frame=frame,
        edges_frame=masked_edges,
        lines=[averaged_left_lane, averaged_right_lane]
        )
    
    return result


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

    global x1, y1, x2, y2

    # Dimensions of image
    h = frame_edges.shape[0]
    w = frame_edges.shape[1]

    # Coordinates of the vertices for the polygon that will be used as the ROI for lanes only.
    x3 = 0
    y3 = h

    x4 = w
    y4 = h

    # Define the vertices of the polygon that will be used to mask the ROI
    vertices = np.array([[
        (x1, y1),
        (x2, y2),
        (x4, y4),
        (x3, y3)
    ]], dtype=np.int32)

    # Create a black image of the same size as the edge-detected image
    roi = np.zeros((h, w), dtype=np.uint8)
    
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
    # Hough transform parameters
    rho = 1 # Distance resolution of candidate lines (accumulator rows)
    theta = np.pi / 180 # Defines interval of how much to increment theta in line calculation.
    threshold = 30 # Minimum number of supporting edge pixels required before a line is considered valid.
    min_line_len = 50 # Minimum length (in pixels) required for a detected line segment.
    max_line_gap = 200 # Maximum allowed gap between line segments that can be connected into one continuous line.

    # Perform Probabilistic Hough Transform
    # Returns detected line segments as endpoints (x1, y1, x2, y2)
    hough_lines = cv2.HoughLinesP(
        image=masked_edges,
        rho=rho,
        theta=theta,
        threshold=threshold,
        minLineLength=min_line_len,
        maxLineGap=max_line_gap
    )

    return hough_lines


###############################################################################
# Function Name: filter_lines
# Description: 
###############################################################################

def filter_lines(lines, min_slope, max_slope, frame_height):
    global last_left_lane
    global last_right_lane

    # No lines found from Hough transform
    if lines is None:
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
    
    # Filtered left and right lanes are valid
    if left_lane is not None:
        # Update last known good left and right lanes
        last_left_lane = left_lane

    if right_lane is not None:
        last_right_lane = right_lane
    
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
    global last_left_lane
    global last_right_lane

    if left_lane is None:
        left_lane = last_left_lane

    if right_lane is None:
        right_lane = last_right_lane
    
    if left_lane is None or right_lane is None:
        return (None, None)

    left_lane_np = np.array(left_lane, dtype=np.float32)
    right_lane_np = np.array(right_lane, dtype=np.float32)

    # Applying EMA on both left and rigth lanes
    if running_average_left_lane is not None:
        averaged_left_lane = (ALPHA * left_lane_np) + ((1 - ALPHA) * running_average_left_lane)
    else:
        averaged_left_lane = left_lane_np

    if running_average_right_lane is not None:
        averaged_right_lane = (ALPHA * right_lane_np) + ((1 - ALPHA) * running_average_right_lane)
    else:
        averaged_right_lane = right_lane_np

    # Update running average references
    running_average_left_lane = averaged_left_lane
    running_average_right_lane = averaged_right_lane

    return tuple(averaged_left_lane.astype(int)), tuple(averaged_right_lane.astype(int))

###############################################################################
# Function Name: draw_lines_on_frame
# Description: 
###############################################################################

def draw_lines_on_frame(frame, edges_frame, lines):
    # Create a blank RGB image to draw the Hough line segments
    h = edges_frame.shape[0]
    w = edges_frame.shape[1]
    line_image = np.zeros(
        shape=(h, w, 3), 
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


if __name__ == "__main__":
    main()