###############################################################################
# File Name: HSV_GUI.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# Library Imports
import cv2
import numpy as np

###############################################################################
# GLOBAL VARIABLES
###############################################################################

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: main
# Description: 
###############################################################################

def main():
    global vc

    rval = init()

    while rval:
        if vc.isOpened(): # try to get the first frame
            rval, frame = vc.read()
        else:
            rval = False

        # read the Trackbar positions
        h_low = cv2.getTrackbarPos('H_Low','HSV')
        h_high = cv2.getTrackbarPos('H_High','HSV')
        s_low = cv2.getTrackbarPos('S_Low','HSV')
        s_high = cv2.getTrackbarPos('S_High','HSV')
        v_low = cv2.getTrackbarPos('V_Low','HSV')
        v_high = cv2.getTrackbarPos('V_High','HSV')
        min_area = cv2.getTrackbarPos("Min_Area", "HSV")

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower = np.array([h_low, s_low, v_low], dtype="uint8") 
        upper = np.array([h_high, s_high, v_high], dtype="uint8")
        
        mask = cv2.inRange(hsv_frame, lower, upper)

        MORPH_KERNEL_SIZE = 3
        MORPH_KERNEL = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE), np.uint8)
        
        morph_mask = cv2.morphologyEx(
            src=mask,
            op=cv2.MORPH_OPEN,
            kernel=MORPH_KERNEL
        )

        morph_mask = cv2.morphologyEx(
            src=morph_mask,
            op=cv2.MORPH_CLOSE,
            kernel=MORPH_KERNEL
        )

        cnts, _ = cv2.findContours(morph_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            x,y,w,h = cv2.boundingRect(c)

            a = w*h
            
            if a >= min_area:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (36,255,12), 2)
        
        cv2.imshow('Mask', mask)
        cv2.imshow('Original', frame)
        
        key = cv2.waitKey(1)

        if key == 27: # exit on ESC (27 is ASCII for ESC)
            break

    vc.release()
    cv2.destroyAllWindows()


###############################################################################
# Function Name: init
# Description: 
###############################################################################

def init():
    global vc
    vc = cv2.VideoCapture(0)

    # Try to get the first frame
    if vc.isOpened():
        rval, frame = vc.read()
    else:
        rval = False

    cv2.namedWindow('HSV')

    # define a null callback function for Trackbar
    def null(x):
        pass

    # create three trackbars for H, S, V
    # Note: H only goes up to 179 for some reason
    # arguments: trackbar_name, window_name, default_value, max_value, callback_fn
    cv2.createTrackbar("H_Low", "HSV", 0, 179, null)
    cv2.createTrackbar("H_High", "HSV", 10, 179, null)
    cv2.createTrackbar("S_Low", "HSV", 120, 255, null)
    cv2.createTrackbar("S_High", "HSV", 255, 255, null)
    cv2.createTrackbar("V_Low", "HSV", 120, 255, null)
    cv2.createTrackbar("V_High", "HSV", 255, 255, null)
    cv2.createTrackbar("Min_Area", "HSV", 256, 5000, null)

    return rval


if __name__ == "__main__":
    main()