###############################################################################
# File Name: HSV_GUI_PiCam.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# Library Imports
import cv2
import numpy as np
import picamera2


###############################################################################
# GLOBAL VARIABLES
###############################################################################

# Resolution camera is set to capture at
CAMERA_WIDTH = 3840
CAMERA_HEIGHT = 2160

# Resolution that the image will be resized to for processing (to speed up processing)
PROCESSING_WIDTH = 640
PROCESSING_HEIGHT = 360

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: main
# Description: 
###############################################################################

def main():
    init()
    
    while True:
        _, frame, validity = fetch_frame()

        # Checks whether the capturing of the frame was successful. If not, exits the loop since the camera is not working.
        if validity is False:
            break

        # Read the Trackbar positions
        h_low = cv2.getTrackbarPos('H_Low','HSV')
        h_high = cv2.getTrackbarPos('H_High','HSV')
        s_low = cv2.getTrackbarPos('S_Low','HSV')
        s_high = cv2.getTrackbarPos('S_High','HSV')
        v_low = cv2.getTrackbarPos('V_Low','HSV')
        v_high = cv2.getTrackbarPos('V_High','HSV')
        min_area = cv2.getTrackbarPos("Min_Area", "HSV")

        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)

        lower = np.array([h_low, s_low, v_low], dtype="uint8") 
        upper = np.array([h_high, s_high, v_high], dtype="uint8")
        
        mask = cv2.inRange(hsv_frame, lower, upper)

        DIlATE_KERNEL_SIZE = 5
        DILATE_KERNEL = np.ones((DIlATE_KERNEL_SIZE, DIlATE_KERNEL_SIZE), np.uint8)

        ERODE_KERNEL_SIZE = 5
        ERODE_KERNEL = np.ones((ERODE_KERNEL_SIZE, ERODE_KERNEL_SIZE), np.uint8)
        
        morph_mask = cv2.dilate(
            src=mask,
            kernel=DILATE_KERNEL,
            iterations=2
        )

        morph_mask = cv2.erode(
            src=morph_mask,
            kernel=ERODE_KERNEL,
            iterations=1
        )

        cnts, _ = cv2.findContours(morph_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for c in cnts:
            x,y,w,h = cv2.boundingRect(c)

            a = w*h
            
            if a >= min_area:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (36,255,12), 2)
                break
        
        cv2.imshow('Mask', morph_mask)
        cv2.imshow('Original', frame)
        
        key = cv2.waitKey(1)

        if key == 27: # exit on ESC (27 is ASCII for ESC)
            break

    cv2.destroyAllWindows()


def init():
    configure_camera()

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


###############################################################################
# Function Name: configure_camera
# Description: Configures the Pi Camera to capture frames at the resolution 
#              specified in camera_config and starts the camera.
###############################################################################

def configure_camera():
    global pi_camera
    
    # Creating and configuring Pi Camera to capture at the resolution specified in camera_config
    pi_camera  = picamera2.Picamera2()
    pi_camera.configure(
        pi_camera.create_preview_configuration(
            main={
                "size": (CAMERA_WIDTH, CAMERA_HEIGHT),
                "format": "RGB888"
            }
        )
    )

    # Allowing the camera to start capturing frames to see if it is valid.
    pi_camera.start()

    # Resizes and fetches the first frame
    _, _, validity = fetch_frame()

    # Checks whether the capturing of the frame was successful. If not, exits the program since the camera is not working.
    if validity is False:
        print("Failed to capture frame")
        exit()
    
    # pi_camera.set_controls({
    #     "Brightness": -0.3,     # range roughly -1.0 to 1.0
    #     "ExposureValue": -1.0   # lower = darker image
    # })


###############################################################################
# Function Name: fetch_frame
# Description: Fetches a frame from the Pi Camera and resizes it for processing.
###############################################################################

def fetch_frame():
    validity = False

    # Capturing frame and checking whether it's valid
    original_frame = pi_camera.capture_array()

    # Checks whether the capturing of the frame was successful. If not, returns None and False for validity since the camera is not working.
    if original_frame is None:
        print("Failed to capture frame")
        return None, validity

    # Resize the original frame to the dimensions specified in vision_config for processing
    resized_frame = cv2.resize(
        original_frame,
        (PROCESSING_WIDTH, PROCESSING_HEIGHT),
        interpolation=cv2.INTER_AREA
    )

    validity = True

    return original_frame, resized_frame, validity


if __name__ == "__main__":
    main()