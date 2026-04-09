
###############################################################################
# File Name: light_detection.py
# Description: 
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
from modules.vision import light_detection_config

# Library Imports
import cv2

###############################################################################
# GLOBAL VARIABLES
###############################################################################

red_mask = None
yellow_mask = None
green_mask = None

###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: process_lights
# Description: Goes over frame to find all lights and only shows ones that fit
#              the HSV range and area constraints.
###############################################################################

def process_lights(frame):
    global red_mask
    global yellow_mask
    global green_mask

    # Hue (H): color (red, green, yellow)
    # Saturation (S): how pure the color is
    # Value (V): brightness of the color

    # Convert color space of frame to HSV
    hsv_frame = cv2.cvtColor(
        src=frame, 
        code=cv2.COLOR_RGB2HSV
    )

    # Finds all lights in the frame and draws bounding boxes with proper text in the frame
    red_mask = detect_light(
        frame,
        hsv_frame,
        light_detection_config.RED_LIGHT
    )
    yellow_mask = detect_light(
        frame,
        hsv_frame,
        light_detection_config.YELLOW_LIGHT
    )
    green_mask = detect_light(
        frame,
        hsv_frame,
        light_detection_config.GREEN_LIGHT
    )


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

    # Looping through contours to find ones that fit the area constraint
    # With those found, draw a bounding box and add text based on the light color
    for contour in contours:
        # Create a bounding box around the detected contour
        x, y, w, h = cv2.boundingRect(contour)

        # Calculate area
        area = w * h

        # Draw the bounding box if the area is greater than the minimum
        if area >= light.light_area_min:

            # Set the color of the bounding box to the color of the light
            if light.color == "red":
                color = (255,0,0)
                text = "Red LED Detected"
            elif light.color == "yellow":
                color = (255,255,0)
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

    return mask

            
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
    morph_mask = cv2.morphologyEx(
        src=mask,
        op=cv2.MORPH_OPEN,
        kernel=light_detection_config.MORPH_KERNEL
    )

    morph_mask = cv2.morphologyEx(
        src=morph_mask,
        op=cv2.MORPH_CLOSE,
        kernel=light_detection_config.MORPH_KERNEL
    )

    return morph_mask