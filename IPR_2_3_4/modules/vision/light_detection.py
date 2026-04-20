
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
# Function Name: get_light_distance
# Description: Obtains the light that is currently being detected and the 
# distance of that light.
###############################################################################

def get_light_distance():
    active_light, averaged_light_area = get_light_area()

    light_distance = 0

    light_distance = light_area_to_distance(active_light, averaged_light_area)

    return active_light, light_distance


###############################################################################
# Function Name: get_light_area
# Description: This is used to obtain the area of the detected light after averaging.
#              The reason this is here is to allow for a simpler approach if the
#              calibration parameters are incorrect. If this approach is needed,
#              change the control logic to use the area value and threshold
#              instead of hte distance value and threshold. Just not at the same
#              time since they are similar.
###############################################################################

def get_light_area():
    active_light = determine_active_light()

    if active_light is None:
        return None, None

    averaged_light_area = average_light_area(active_light)

    return active_light, averaged_light_area


###############################################################################
# Function Name: light_area_to_distance
# Description: Converts detected light area to distance using interpolation 
#              based on the calibration tables.
###############################################################################

def light_area_to_distance(active_light, light_area):
    interpolated_distance = 0

    cal_table = None
    num_of_cal_points = None

    # Determine which calibration table to use based on the active light
    if active_light == "red":
        cal_table = light_detection_config.RED_CALIBRATION_TABLE
        num_of_cal_points = light_detection_config.NUMBER_OF_RED_CALIBRATION_POINTS

    elif active_light == "yellow":
        cal_table = light_detection_config.YELLOW_CALIBRATION_TABLE
        num_of_cal_points = light_detection_config.NUMBER_OF_YELLOW_CALIBRATION_POINTS
    elif active_light == "green":
        cal_table = light_detection_config.GREEN_CALIBRATION_TABLE
        num_of_cal_points = light_detection_config.NUMBER_OF_GREEN_CALIBRATION_POINTS
    # No active light so don't do interpolation
    else:
        return None
    

    if light_area is None:
        return None
    
    # Determine the correct points to interpolate between.
    if light_area <= cal_table[0].area:
        return cal_table[0].distance
    elif light_area >= cal_table[num_of_cal_points-1].area:
        return cal_table[num_of_cal_points-1].distance
    else:
        # Skip first point to allow the use of the previous point for interpolation
        for i in range(1, num_of_cal_points):
            
            if light_area <= cal_table[i].area:
                area1 = cal_table[i - 1].area
                area2 = cal_table[i].area
                distance1 = cal_table[i - 1].distance
                distance2 = cal_table[i].distance

                distance_difference = distance2 - distance1
                input_area_difference = light_area - area1
                area_difference = area2 - area1

                interpolated_distance = distance1 + (distance_difference * (input_area_difference / area_difference))
            
                break

    return interpolated_distance


###############################################################################
# Function Name: average_light_area
# Description: Averages the area of the detected light over time using an 
#              exponential moving average.
###############################################################################

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
# Function Name: determine_active_light
# Description: Determines which light is currently active based on the 
#              detected areas.
###############################################################################

def determine_active_light():
    active_light = ""

    #  Red light is active
    if red_area is not None and yellow_area is None and green_area is None:
        active_light = "red"
    #  Yellow light is active
    elif red_area is None and yellow_area is not None and green_area is None:
        active_light = "yellow"
    elif red_area is None and yellow_area is None and green_area is not None:
        active_light = "green"
    else:
        active_light = None

    return active_light


###############################################################################
# Function Name: process_lights
# Description: Goes over frame to find all lights and only shows ones that fit
#              the HSV range and area constraints. Will also return area for 
#              use later for distance calcuation. This function needs to be 
#              called for the parameters to be updated.
###############################################################################

def process_lights(frame):
    global red_mask
    global red_area
    global yellow_mask
    global yellow_area
    global green_mask
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
            # Used to return and let other functions know that a LED was detected with a given area
            # If the area parameter outside of this was returned, then we'd always get a value.
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