
###############################################################################
# File Name: light_detection_test.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
from modules.camera import camera
from modules.vision import light_detection_config

# Library Imports
import cv2

###############################################################################
# GLOBAL VARIABLES
###############################################################################

red_mask = None
yellow_mask = None
green_mask = None

red_area = None
yellow_area = None
green_area = None

running_average_red_area = None
running_average_yellow_area = None
running_average_green_area = None

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
        
        process_lights(frame)

        cv2.imshow("Original", frame)
        cv2.imshow("Red Mask", red_mask)
        cv2.imshow("Yellow Mask", yellow_mask)
        cv2.imshow("Green Mask", green_mask)

        # Break the loop when 'ESC' key is pressed
        key = cv2.waitKey(1)

        # Exit on ESC (27 is ASCII for ESC)
        if key == 27:
            break

    cv2.destroyAllWindows()


###############################################################################
# Function Name: process_lights
# Description: Goes over frame to find all lights and only shows ones that fit
#              the HSV range and area constraints.
###############################################################################

def process_lights(frame):
    global red_mask
    global yellow_mask
    global green_mask

    global red_area
    global yellow_area
    global green_area

    # Hue (H): color (red, green, yellow)
    # Saturation (S): how pure the color is
    # Value (V): brightness of the color

    # Convert color space of frame to HSV
    hsv_frame = cv2.cvtColor(
        src=frame, 
        code=cv2.COLOR_RGB2HSV
    )

    # Finds all lights in the frame and draws bounding boxes with proper text in the frame
    red_mask, red_area = detect_light(
        frame,
        hsv_frame,
        light_detection_config.RED_LIGHT
    )
    yellow_mask, yellow_area = detect_light(
        frame,
        hsv_frame,
        light_detection_config.YELLOW_LIGHT
    )
    green_mask, green_area = detect_light(
        frame,
        hsv_frame,
        light_detection_config.GREEN_LIGHT
    )

    if red_area is not None:
        red_average = average_light_area("red")
    else:
        red_average = 0
    
    if yellow_area is not None:
        yellow_average = average_light_area("yellow")
    else:
        yellow_average = 0

    if green_area is not None:
        green_average = average_light_area("green")
    else:
        green_average = 0
    
    print(f"Area: Red = {red_average}; Yellow = {yellow_average}; Green = {green_average}")


###############################################################################
# Function Name: detect_light
# Description: Processes the frame to look for input HSV ranges. Then locates
#              valid contours in frame based on their area. Finally, drawing
#              bounding boxes and adding text based on the color.
# ###############################################################################

def detect_light(original_frame, hsv_frame, light:light_detection_config.Light):
    # Obtains the mask based on the input HSV ranges. Applies erode and dilate morphology to allow for a cleaner binary image.
    mask = process_mask(
        hsv_frame,
        light.hsv_range
    )

    # Finding all detected items with the same HSV signature that was specified
    contours, _ = cv2.findContours(
        mask, 
        cv2.RETR_EXTERNAL, 
        cv2.CHAIN_APPROX_SIMPLE
    )

    light_area = None

    for contour in contours:
        # Create a bounding box around the detected contour
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate area
        area = w * h

        # Draw the bounding box if the area is greater than the minimum
        if area >= light.light_area_min:
            light_area = area
            # Set the color of the bounding box to the color of the light
            if light.color == "red":
                color = (0,0,255)
                text = "Red LED Detected"
            elif light.color == "yellow":
                color = (0,255,255)
                text = "Yellow LED Detected"
            elif light.color == "green":
                color = (0,255,0)
                text = "Green LED Detected"
            else:
                color = (255,255,255)
                text = "No LEDs Detected"
            
            # Draw the rectangle using the determined color
            cv2.rectangle(
                img=original_frame, 
                pt1=(x, y), 
                pt2=(x + w, y + h), 
                color=color, 
                thickness=2
            )

            # Add text that shows what color it is seeing
            cv2.putText(
                img=original_frame,
                text=text,
                org=(10, 30),
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.8,
                color=color,
                thickness=2
            )
            break

    return mask, light_area

            
###############################################################################
# Function Name: process_mask
# Description: Obtains the mask based on the input HSV ranges. Applies erode 
#              and dilate morphology to allow for a cleaner binary image.
###############################################################################

def process_mask(hsv_frame, hsv_range: light_detection_config.ColorHSVRange):
    # Create frame that are bitwise images that only contain light pixels if the color within the expected range is present
    mask = cv2.inRange(
        src=hsv_frame,
        lowerb=hsv_range.lower,
        upperb=hsv_range.upper,
    )

    # Erode and dilate the mask
    # This allows gaps to be closed for cleaner detected items
    morph_mask = cv2.dilate(
        src=mask,
        kernel=light_detection_config.DILATE_KERNEL,
        iterations=2
    )

    morph_mask = cv2.erode(
        src=morph_mask,
        kernel=light_detection_config.ERODE_KERNEL,
        iterations=1
    )

    return morph_mask


def average_light_area(active_light):
    global running_average_red_area
    global running_average_yellow_area
    global running_average_green_area

    if active_light == "red":
        if running_average_red_area is None:
            running_average_red_area = red_area
        else:
            running_average_red_area = (light_detection_config.LIGHT_AREA_EMA_ALPHA * red_area) + ((1 - light_detection_config.LIGHT_AREA_EMA_ALPHA) * running_average_red_area)

        return running_average_red_area
    
    elif active_light == "yellow":
        if running_average_yellow_area is None:
            running_average_yellow_area = yellow_area
        else:
            running_average_yellow_area = (light_detection_config.LIGHT_AREA_EMA_ALPHA * yellow_area) + ((1 - light_detection_config.LIGHT_AREA_EMA_ALPHA) * running_average_yellow_area)
        
        return running_average_yellow_area

    elif active_light == "green":
        if running_average_green_area is None:
            running_average_green_area = green_area
        else:
            running_average_green_area = (light_detection_config.LIGHT_AREA_EMA_ALPHA * green_area) + ((1 - light_detection_config.LIGHT_AREA_EMA_ALPHA) * running_average_green_area)
        
        return running_average_green_area

    else:
        return 0

###############################################################################
# Function Name: shutdown_peripherals
# Description: Shuts down all peripherals and cleans up resources.
###############################################################################

def shutdown_peripherals():
    # Stopping the camera and closing it
    camera.shutdown_camera()


if __name__ == "__main__":
    main()