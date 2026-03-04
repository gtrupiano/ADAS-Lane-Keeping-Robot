import cv2
import numpy as np

def main():
    camera = cv2.VideoCapture(0)

    if camera.isOpened(): # try to get the first frame
        rval, frame = camera.read()
    else:
        rval = False

    cv2.namedWindow('ROI')
    # define a null callback function for Trackbar
    def null(x):
        pass
    # create three trackbars for B, G and R
    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("x1", "ROI", 0, 1000, null)
    cv2.createTrackbar("y1", "ROI", 0, 1000, null)

    cv2.createTrackbar("x2", "ROI", 0, 1000, null)
    cv2.createTrackbar("y2", "ROI", 0, 1000, null)


    while rval:
        if camera.isOpened(): # try to get the first frame
            rval, frame = camera.read()
        else:
            rval = False

        # read the Trackbar positions
        x1 = cv2.getTrackbarPos('x1','ROI')
        y1 = cv2.getTrackbarPos('y1','ROI')
        x2 = cv2.getTrackbarPos('x2','ROI')
        y2 = cv2.getTrackbarPos('y2','ROI')

        flip_frame = cv2.flip(frame,1) #0 is normal, 1 is flipped over y axis
        original1 = frame.copy()

        roi_frame = apply_ROI(flip_frame, x1, y1, x2, y2)

        cv2.imshow('help', roi_frame)
        key = cv2.waitKey(27)

        if key == 27: # exit on ESC (27 is ASCII for ESC)
            break

    camera.release()

    cv2.destroyWindow("mask")
    cv2.destroyWindow("original")



def apply_ROI(frame, x1, y1, x2, y2):
    r"""
    (x1,y1) ------- (x4,y4)
     \               /
      \             /
       (x2,y2) (x3,y3)
    """

    # Dimensions of image
    h = frame.shape[0]
    w = frame.shape[1]

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
        frame,
        frame,
        mask=roi
        )

    return masked_edges

main()