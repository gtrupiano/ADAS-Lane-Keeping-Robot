
###############################################################################
# File Name: light_detection_test.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
from modules.camera import camera

# Library Imports
import cv2

###############################################################################
# GLOBAL VARIABLES
###############################################################################

RED_MASK_LOW = 0
RED_MASK_HIGH = 1

YELLOW_MASK_LOW = 0
YELLOW_MASK_HIGH = 1

GREEN_MASK_LOW = 0
GREEN_MASK_HIGH = 1

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: main
# Description: 
###############################################################################

def main():
    camera.configure_camera()

    while True:
        _, frame, validity = camera.fetch_frame()

        # Checks whether the capturing of the frame was successful. If not, exits the loop since the camera is not working.
        if validity is False:
            break
        


        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(1)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break



###############################################################################
# Function Name: 
# Description: 
###############################################################################

###############################################################################
# Function Name: shutdown_peripherals
# Description: Shuts down all peripherals and cleans up resources.
###############################################################################

def shutdown_peripherals():
    # Stopping the camera and closing it
    camera.shutdown_camera()


if __name__ == "__main__":
    main()