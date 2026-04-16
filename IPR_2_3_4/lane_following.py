###############################################################################
# File Name: lane_following.py
# Description: Main application logic for the lane following algorithm.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import modules.camera.camera as camera
import modules.vision.vision as vision
import modules.vision.vision_config as vision_config
import modules.control.control as control
import modules.motor.motor_control as motor_control
import modules.sensor.ultrasonic as ultrasonic
import modules.vision.light_detection_config as light_detection_config
import modules.vision.light_detection as light_detection

# Library Imports
import cv2

###############################################################################
# GLOBAL VARIABLES
###############################################################################

# Frame at different stages of processing
original_frame = None
resized_frame = None
lanes_on_frame = None


###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: main
# Description: Application level logic for the lane following algorithm.
###############################################################################

def main():
    global original_frame
    global resized_frame
    global lanes_on_frame

    # Initialization
    ultrasonic.initialize_ultrasonic_sensor()
    camera.configure_camera()
    motor_control.setup_motor_controller()
    
    # Capturing input on whether user wants to calibrate the ROI points or not before starting the main loop for lane detection and movement control
    roi_calibration_input = input("Calibrate ROI points (Yes / No)")
    roi_calibration_input = roi_calibration_input.lower()

    # Loop until valid input is received
    while roi_calibration_input != "yes" and roi_calibration_input != "no":
        roi_calibration_input = input("Invalid input. Calibrate ROI points (Yes / No)")
        roi_calibration_input = roi_calibration_input.lower()

    # Go into ROI calibration if user input is "yes".
    if roi_calibration_input.lower() == "yes":
        vision.calibrate_ROI_points()


    # Main loop for lane detection and movement control
    while True:
        # Sensor readings:
        
        # Fetching frame from camera
        original_frame, resized_frame, validity = camera.fetch_frame()

        # Fetching distance reading from ultrasonic sensor
        object_distance_cm = ultrasonic.get_ultrasonic_distance()

        # Checks whether the capturing of the frame was successful. If not, exits the loop since the camera is not working.
        if validity is False:
            break
        
        # Find light in frame and draw them on original frame.
        light_detection.process_lights(original_frame)

        # Obtains active light and it's current distance
        active_light, light_distance = light_detection.get_light_distance()

        if (active_light is None) or (light_distance is None):
            print("No light detected")

        # Detecting lanes and drawing them on the original frame
        lanes_on_frame, left_lane, right_lane = vision.detect_lanes(resized_frame)

        # Determine movement based on the detected lanes and send commands to the motor controller
        control.determine_movement(left_lane, right_lane, object_distance_cm, active_light, light_distance)

        # Display frames based on whether debug mode is enabled or not
        if vision_config.SHOW_DEBUG_FRAMES:
            cv2.imshow('Original Frame', original_frame)
            cv2.imshow('Resized Frame', resized_frame)
            cv2.imshow('Red Light Mask', light_detection.red_mask)
            cv2.imshow('Yellow Light Mask', light_detection.yellow_mask)
            cv2.imshow('Green Light Mask', light_detection.green_mask)
            cv2.imshow('Filtered Frame', vision.filtered_frame)
            cv2.imshow('Edges Frame', vision.frame_edges)
            cv2.imshow('ROI Edges Frame', vision.roi_edges)
            cv2.imshow('Lanes', lanes_on_frame)
        else:
            cv2.imshow('Resized Frame', resized_frame)
            cv2.imshow('Lanes', lanes_on_frame)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(1)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break
    
    shutdown_peripherals()


###############################################################################
# Function Name: shutdown_peripherals
# Description: Shuts down all peripherals and cleans up resources.
###############################################################################

def shutdown_peripherals():
    # Closing ultrasonic sensor
    ultrasonic.close_ultrasonic_sensor()

    # Stopping the camera and closing it
    camera.shutdown_camera()
    
    # Stopping the motors and closing the motor controller
    motor_control.shutdown_motors()

    # Closing all OpenCV windows
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()