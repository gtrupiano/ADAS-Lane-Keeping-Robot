###############################################################################
# File Name: IPR_1.py
# Description: 
###############################################################################

# Library Imports
import cv2
import numpy as np
import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def main():
    input_image = mpimg.imread('Test_Images/solidWhiteRight.jpg')

    gray_image = cv2.cvtColor(input_image, cv2.COLOR_RGB2GRAY)
    
    # Size of block that goes through each pixel and calculates the weighted average of the surrounding pixels. 
    # The larger the kernel size, the more blurred the image will be.
    KERNAL_SIZE = 5
    SIGMA_BLUR_CONTROL = 0
    filtered_image = cv2.GaussianBlur(gray_image, (KERNAL_SIZE, KERNAL_SIZE), SIGMA_BLUR_CONTROL)

    LOW_THRESHOLD = 50
    HIGH_THRESHOLD = 150
    image_edges = cv2.Canny(filtered_image, LOW_THRESHOLD, HIGH_THRESHOLD)

    # Edges that are within the ROI
    masked_edges = apply_ROI(image_edges)






    lines = hough_transform(input_image, masked_edges)

    # Create a blank RGB image to draw the Hough line segments
    h = masked_edges.shape[0]
    w = masked_edges.shape[1]
    line_image = np.zeros((h, w, 3), dtype=np.uint8)

    # Draw each detected line segment (if any)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 0, 0), 5)

    # Overlay the line image on the original image
    result = cv2.addWeighted(input_image, 0.8, line_image, 1.0, 0.0)

    plt.imshow(result, cmap='gray')
    plt.show()


def apply_ROI(image_edges):
    """
    (x1,y1) ------- (x4,y4)
     \               /
      \             /
       (x2,y2) (x3,y3)
    """

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

    # Define the vertices of the polygon that will be used to mask the region of interest (ROI).
    vertices = np.array([[
        (x1, y1),
        (x2, y2),
        (x4, y4),
        (x3, y3)
    ]], dtype=np.int32)

    # Create a black image of the same size as the edge-detected image
    roi_image = np.zeros_like(image_edges)

    # Fill the region inside the vertices with white (255).
    cv2.fillPoly(roi_image, vertices, 255)

    # Perform a bitwise AND operation between the edge-detected image and the mask to keep only the edges that are within the ROI.
    masked_edges = cv2.bitwise_and(image_edges, roi_image)
    
    return masked_edges


def hough_transform(input_image, masked_edges):
    # Hough transform parameters
    rho = 2 
    theta = np.pi / 180
    threshold = 15
    min_line_len = 40
    max_line_gap = 20

    lines = cv2.HoughLinesP(
        masked_edges,
        rho,
        theta,
        threshold,
        np.array([]),
        minLineLength=min_line_len,
        maxLineGap=max_line_gap
    )

    return lines

if __name__ == "__main__":
    main()