import cv2
import numpy as np

vc = cv2.VideoCapture(0)

# Try to get the first frame
if vc.isOpened():
    rval, image2 = vc.read()
else:
    rval = False

cv2.namedWindow('HSV')
# define a null callback function for Trackbar
def null(x):
    pass
# create three trackbars for B, G and R 
# arguments: trackbar_name, window_name, default_value, max_value, callback_fn
cv2.createTrackbar("H_Low", "HSV", 0, 255, null)
cv2.createTrackbar("H_High", "HSV", 0, 255, null)
cv2.createTrackbar("S_Low", "HSV", 0, 255, null)
cv2.createTrackbar("S_High", "HSV", 0, 255, null)
cv2.createTrackbar("V_Low", "HSV", 0, 255, null)
cv2.createTrackbar("V_High", "HSV", 0, 255, null)

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

    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower = np.array([h_low, s_low, v_low], dtype="uint8") 
    upper = np.array([h_high, s_high, v_high], dtype="uint8")
    
    mask = cv2.inRange(frame, lower, upper)

    cnts = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        x,y,w,h = cv2.boundingRect(c)

        a = w*h
        
        if a <=1800:
            c+=1
        else:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (36,255,12), 2)
    
    cv2.imshow('Mask', mask)
    cv2.imshow('Original', frame)
    
    key = cv2.waitKey(1)

    if key == 27: # exit on ESC (27 is ASCII for ESC)
        break

vc.release()
cv2.destroyAllWindows()