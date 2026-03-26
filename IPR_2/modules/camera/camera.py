###############################################################################
# File Name: camera.py
# Description: Contains functions for configuring the Pi Camera and fetching 
#              frames from it.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import modules.camera.camera_config as camera_config

# Library Imports
import cv2
import picamera2


###############################################################################
# GLOBAL VARIABLES
###############################################################################

# Pi Camera object
pi_camera = None


###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: configure_camera
# Description: Configures the Pi Camera to capture frames at the resolution 
#              specified in vision_config and starts the camera.
###############################################################################

def configure_camera():
    global pi_camera
    
    # Creating and configuring Pi Camera to capture at the resolution specified in vision_config
    pi_camera  = picamera2.Picamera2()
    pi_camera.configure(
        pi_camera.create_preview_configuration(
            main={
                "size": (camera_config.CAMERA_WIDTH, camera_config.CAMERA_HEIGHT),
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
        (camera_config.PROCESSING_WIDTH, camera_config.PROCESSING_HEIGHT),
        interpolation=cv2.INTER_AREA
    )

    validity = True

    return original_frame, resized_frame, validity


###############################################################################
# Function Name: shutdown_camera
# Description: Shuts down the Pi Camera to free up resources.
###############################################################################

def shutdown_camera():
    if pi_camera:
        pi_camera.stop()
        pi_camera.close()
