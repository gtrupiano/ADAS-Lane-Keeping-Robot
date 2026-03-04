###############################################################################
# File Name: IPR_1.py
# Description: 
###############################################################################

# Library Imports
import cv2
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip
import os
from pathlib import Path

last_lanes = None
averaged_left = None
averaged_right = None

ALPHA = 0.1

def main():
    #process_image("solidWhiteRight.jpg")
    process_video("solidWhiteRight.mp4")
    process_video("solidYellowLeft.mp4")
    process_video("challenge.mp4")


###############################################################################
# Function Name: process_image
# Description: 
###############################################################################

def process_image(image_name):
    image_path = (f"./Test_Images/{image_name}")
    input_image = mpimg.imread(image_path)

    result = detect_lanes(input_image)

    plt.imshow(result)
    plt.show()


###############################################################################
# Function Name: process_video
# Description: 
###############################################################################

def process_video(video_name):
    input_path = (f"./Test_Videos/{video_name}")

    clip = VideoFileClip(input_path, audio=False).subclip(0, 5)

    # moviepy will call this once per frame (frame is an RGB numpy array)
    output_clip = clip.fl_image(detect_lanes)

    # Create output folder
    output_folder = r"Test_Video_Outputs_Mine"

    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    # Build output path using input 
    output_path = f"./Test_Video_Outputs_Mine/Output_{video_name}"

    output_clip.write_videofile(
        filename=output_path,
        audio=False,
        codec="libx264",
        fps=clip.fps
    )
    
    clip.close()
    output_clip.close()


###############################################################################
# Function Name: detect_lanes
# Description: 
###############################################################################

def detect_lanes(input_frame):
    # Convert to grayscale
    gray_frame = cv2.cvtColor(
        src=input_frame,
        code=cv2.COLOR_RGB2GRAY
        )
    
    # Size of block that goes through each pixel and calculates the weighted average of the surrounding pixels. 
    # The larger the kernel size, the more blurred the image will be.
    KERNAL_SIZE = 7
    SIGMA_BLUR_CONTROL = 0
    filtered_frame = cv2.GaussianBlur(
        src=gray_frame, 
        ksize=(KERNAL_SIZE, KERNAL_SIZE),
        sigmaX=SIGMA_BLUR_CONTROL,
        sigmaY=SIGMA_BLUR_CONTROL
        )

    # Canny Edge Detection
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
    # kernel = np.ones((3, 3), np.uint8)
    # masked_edges = cv2.morphologyEx(
    #     src=masked_edges,
    #     op=cv2.MORPH_CLOSE,
    #     kernel=kernel,
    #     iterations=2
    # )

    # Fetches straight line segments from edges of image
    hough_lines = hough_transform(masked_edges)

    # Filter out lines that have non ideal slopes
    filtered_lines = filter_lines(hough_lines, 0.5, 2.5, input_frame.shape[0])

    # If this frame failed to detect lanes, reuse the last good lanes
        # If this frame failed to detect lanes, reuse the last good lanes
    global last_lanes
    global averaged_left
    global averaged_right

    if filtered_lines is None:
        filtered_lines = last_lanes
    else:
        last_lanes = filtered_lines

    # Still nothing to draw
    if filtered_lines is None:
        return input_frame

    # filtered_lines contains 1 or 2 tuples: (x1, y1, x2, y2)
    # Convert to numpy arrays so we can do elementwise EMA math
    if len(filtered_lines) >= 1:
        current_left = np.array(filtered_lines[0], dtype=np.float32)

        if averaged_left is None:
            averaged_left = current_left
        else:
            averaged_left = (ALPHA * current_left) + ((1 - ALPHA) * averaged_left)

    if len(filtered_lines) >= 2:
        current_right = np.array(filtered_lines[1], dtype=np.float32)

        if averaged_right is None:
            averaged_right = current_right
        else:
            averaged_right = (ALPHA * current_right) + ((1 - ALPHA) * averaged_right)

    averaged_lines = []

    if averaged_left is not None:
        averaged_lines.append(tuple(averaged_left.astype(int)))

    if averaged_right is not None:
        averaged_lines.append(tuple(averaged_right.astype(int)))


    # Draw lines and overly onto input image
    result = draw_lines_on_frame(
        frame=input_frame,
        edges_frame=masked_edges,
        lines=averaged_lines
        )
    
    return result


###############################################################################
# Function Name: apply_ROI
# Description: 
###############################################################################

def apply_ROI(image_edges):
    r"""
    (x1,y1) ------- (x4,y4)
     \               /
      \             /
       (x2,y2) (x3,y3)
    """

    # Dimensions of image
    h = image_edges.shape[0]
    w = image_edges.shape[1]

    # Coordinates of the vertices for the polygon that will be used as the ROI for lanes only.
    x1 = 400
    y1 = 350

    x2 = 550
    y2 = 350

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
    roi = np.zeros_like(image_edges)

    # Fill the region inside the vertices with white (255).
    cv2.fillPoly(
        img=roi, 
        pts=vertices, 
        color=255
        )

    # Perform a bitwise AND operation between the edge-detected image and the
    # mask to keep only the edges that are within the ROI.
    masked_edges = cv2.bitwise_and(
        src1=image_edges,
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
    threshold = 50 # Minimum number of supporting edge pixels required before a line is considered valid.
    min_line_len = 100 # Minimum length (in pixels) required for a detected line segment.
    max_line_gap = 40 # Maximum allowed gap between line segments that can be connected into one continuous line.

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
    # No lines found from Hough transform
    if lines is None:
        return None
    
    left_lines_slope = []
    left_lines_intercept = []

    right_lines_slope = []
    right_lines_intercept = []

    lanes = []

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

        lanes.append((x_bottom, y_bottom, x_top, y_top))

    if right_lines_slope:
        m_avg = np.median(right_lines_slope)
        b_avg = np.median(right_lines_intercept)

        x_bottom = int((y_bottom - b_avg) / m_avg)
        x_top = int((y_top - b_avg) / m_avg)

        lanes.append((x_bottom, y_bottom, x_top, y_top))

    if lanes:
        return lanes
    else:
        return None

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