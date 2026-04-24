# ADAS Lane Keeping Robotic Car
By: George Trupiano

Class: ECE-6520

## Purpose of Project
This project is about understanding, designing, and implementing a simplified Advanced Driver Assistance System (ADAS) using a Raspberry Pi 5, a camera, and an ultrasonic sensor. The purpose of this system is to simulate real-time vehicle assistance features such as lane detection, traffic light detection, object detection, and basic movement control in order to replicate how a vehicle interprets and reacts to its surrounding environment. The system follows a structured approach where all peripherals are initialized, the region of interest (ROI) is calibrated, and then the application continuously loops through capturing sensor data, processing that data, and applying control logic as described in the system flow diagrams .

Visual data is obtained from the camera and processed to detect lanes and traffic lights using image processing techniques such as grayscale conversion, edge detection, and HSV masking. Distance measurements are obtained from the ultrasonic sensor and filtered using an exponential moving average (EMA) to reduce the effect of noisy readings. That filtered data, along with detected lane positions and traffic light states, is used within a priority-based control system to determine how the robotic car should move. The system adjusts motor behavior based on object distance, traffic light conditions, and lane position using predefined thresholds and proportional logic.

The results show the ability of the system to make real-time decisions by integrating multiple sensor inputs and processing stages. This demonstrates a simplified yet effective approach to ADAS implementation while highlighting concepts such as sensor fusion, real-time processing, and modular system design without relying on more advanced control methods such as PID.