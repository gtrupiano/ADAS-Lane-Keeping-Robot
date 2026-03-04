###############################################################################
# File Name: IPR_2.py
# Description: 
###############################################################################

# Library Imports
import cv2
import numpy as np
import os
from pathlib import Path


def main():
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        print("Can't open camera")
        exit()
    
    while True:
        ret, frame = camera.read()

        if not ret:
            print("Can't recieve frame. Ending")
            break
        
        cv2.imshow('Camera', frame)

        # Break the loop when 'q' key is pressed
        if cv2.waitKey(1) == ord('q'):
            break
    
    
    camera.release()
    cv2.destroyAllWindows()

###############################################################################
# Function Name: detect_lanes
# Description: 
###############################################################################

def detect_lanes(input_frame):
    gray_image = cv2.cvtColor(
        src=input_image,
        code=cv2.COLOR_RGB2GRAY
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
        image=input_image,
        edges_image=masked_edges,
        lines=hough_lines
        )
    
    return result




###############################################################################
# Function Name: apply_ROI
# Description: 
###############################################################################

def apply_ROI(image_edges):
    pass



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
    pass



def draw_lines_on_image(image, edges_image, lines):
    pass