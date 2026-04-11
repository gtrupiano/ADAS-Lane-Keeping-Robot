###############################################################################
# File Name: ultrasonic.py
# Description: Contains the logic for interfacing with the ultrasonic sensor, 
#              including reading distance measurements and applying EMA 
#              smoothing.
###############################################################################

###############################################################################
# IMPORTS
###############################################################################

# File Imports
import modules.sensor.ultrasonic_config as ultrasonic_config

# Library Imports
import gpiozero as GPIO


###############################################################################
# GLOBAL VARIABLES
###############################################################################

ultrasonic_sensor = None
running_average_distance_cm = 0


###############################################################################
# GLOBAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: initialize_ultrasonic_sensor
# Description: 
###############################################################################

def initialize_ultrasonic_sensor():
    global ultrasonic_sensor
    global running_average_distance_cm
    
    ultrasonic_sensor = GPIO.DistanceSensor(
        echo=ultrasonic_config.ECHO_PIN,
        trigger=ultrasonic_config.TRIGGER_PIN,
        max_distance=ultrasonic_config.MAX_ULTRASONIC_DISTANCE_CM / 100.0,
    )

    running_average_distance_cm = 0


###############################################################################
# Function Name: get_ultrasonic_distance
# Description: Fetches the distance measurement from the ultrasonic sensor, 
#              applies EMA smoothing, and returns the averaged distance in CM.
###############################################################################

def get_ultrasonic_distance():
    if ultrasonic_sensor is None:
        raise RuntimeError("Ultrasonic sensor not initialized. Call initialize_ultrasonic_sensor() first.")
    
    instantaneous_distance = _obtain_and_save_distance()

    averaged_distance = _calculate_exponential_moving_average(instantaneous_distance)

    return averaged_distance


###############################################################################
# Function Name: close_ultrasonic_sensor
# Description: Closes the ultrasonic sensor object to free up resources.
###############################################################################

def close_ultrasonic_sensor():
    global ultrasonic_sensor

    if ultrasonic_sensor is not None:
        ultrasonic_sensor.close()
        ultrasonic_sensor = None


###############################################################################
# LOCAL FUNCTIONS
###############################################################################

###############################################################################
# Function Name: _obtain_and_save_distance
# Description: Fetches the instantaneous distance from the ultrasonic sensor
#              object and converts it to CM.
###############################################################################

def _obtain_and_save_distance():
    # Converting distance from M to CM
    object_distance_cm = ultrasonic_sensor.distance * ultrasonic_config.MAX_ULTRASONIC_DISTANCE_CM

    # Making sure calculated distance doesn't go over min and max distance limits
    if object_distance_cm < ultrasonic_config.MIN_ULTRASONIC_DISTANCE_CM:
        object_distance_cm = ultrasonic_config.MIN_ULTRASONIC_DISTANCE_CM
    elif object_distance_cm > ultrasonic_config.MAX_ULTRASONIC_DISTANCE_CM:
        object_distance_cm = ultrasonic_config.MAX_ULTRASONIC_DISTANCE_CM

    return object_distance_cm


###############################################################################
# Function Name: _calculate_exponential_moving_average
# Description: The purpose of the EMA calculation is to make it so new values
#              read from the sensor don't have as much of an effect on the 
#              value used to move the motor.
#              
#              The EMA calculation goes as follows:
#              new_running_average = (EMA_ALPHA * instantaneous_value) +
#                                ((1 - EMA_ALPHA) * previous_running_average)
#
#              What this calculation allows is to control the amount of impact
#              the new instantaneous value has on the running average.
###############################################################################

def _calculate_exponential_moving_average(instantaneous_distance):
    global running_average_distance_cm

    # Since this formula depends on the previous value,
    # if it's 0 (what it's initialized to), then update it to instantaneous value.
    # Then return since we don't want do the calculation due to startup bias
    if running_average_distance_cm == 0:
        running_average_distance_cm = instantaneous_distance
        return running_average_distance_cm

    # EMA formula calculation
    new_running_average = (ultrasonic_config.ULTRASONIC_EMA_ALPHA * instantaneous_distance) + ((1 - ultrasonic_config.ULTRASONIC_EMA_ALPHA) * running_average_distance_cm)

    # Update running average with new one
    running_average_distance_cm = new_running_average

    return new_running_average
