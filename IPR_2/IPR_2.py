###############################################################################
# File Name: IPR_2.py
# Description: 
###############################################################################

# Library Imports
import cv2
import numpy as np
import os
import picamera2

pi_camera = None

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
        frame = pi_camera.capture_array()

        if frame is None:
            print("Can't recieve frame. Ending")
            break
        
        lanes_in_frame = detect_lanes(frame)

        cv2.imshow('Camera', lanes_in_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(100)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    pi_camera.stop()

    cv2.destroyAllWindows()


###############################################################################
# Function Name: configure_camera
# Description: 
###############################################################################

def configure_camera():
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
    
    # Dimensions of image
    h = frame.shape[0]
    w = frame.shape[1]
    
    return w, h


###############################################################################
# Function Name: calibrate_ROI_points
# Description: 
###############################################################################

def calibrate_ROI_points(w, h):
    # define a null callback function for Trackbar
    def null(x):
        pass
    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("x1", "ROI", 400, w, null)
    cv2.createTrackbar("y1", "ROI", 350, h, null)

    cv2.createTrackbar("x2", "ROI", 550, w, null)
    cv2.createTrackbar("y2", "ROI", 350, h, null)

    while True:
        # Capturing frame and checking whether it's valid
        frame = pi_camera.capture_array()
        if frame is None:
            print("Failed to capture frame")
            break

        x1 = cv2.getTrackbarPos("x1", "ROI")
        y1 = cv2.getTrackbarPos("y1", "ROI")
        x2 = cv2.getTrackbarPos("x2", "ROI")
        y2 = cv2.getTrackbarPos("y2", "ROI")

        roi_frame = apply_ROI(frame, x1, y1, x2, y2)

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
    filtered_image = cv2.GaussianBlur(
        src=gray_image, 
        ksize=(KERNAL_SIZE, KERNAL_SIZE),
        sigmaX=SIGMA_BLUR_CONTROL,
        sigmaY=SIGMA_BLUR_CONTROL
        )

    LOW_THRESHOLD = 50
    HIGH_THRESHOLD = 150
    image_edges = cv2.Canny(
        image=filtered_image, 
        threshold1=LOW_THRESHOLD,
        threshold2=HIGH_THRESHOLD
        )

    # Edges that are within the ROI
    masked_edges = apply_ROI(image_edges)

    # # Connect dashed lane markings by filling small gaps in edges
    # kernel = np.ones((5, 5), np.uint8)
    # masked_edges = cv2.morphologyEx(
    #     src=masked_edges,
    #     op=cv2.MORPH_CLOSE,
    #     kernel=kernel
    # )

    # Fetches straight line segments from edges of image
    hough_lines = hough_transform(masked_edges)

    # Draw lines and overly onto input image
    result = draw_lines_on_image(
        image=frame,
        edges_image=masked_edges,
        lines=hough_lines
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
    roi = np.zeros_like(frame_edges)

    # Fill the region inside the vertices with white (255).
    cv2.fillPoly(
        img=roi, 
        pts=vertices, 
        color=255
        )

    # Perform a bitwise AND operation between the edge-detected image and the
    # mask to keep only the edges that are within the ROI.
    masked_edges = cv2.bitwise_and(
        src1=frame_edges,
        src2=roi
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
# Function Name: draw_lines_on_image
# Description: 
###############################################################################

def draw_lines_on_image(frame, edges_frame, lines):
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
            x1, y1, x2, y2 = line[0]
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
