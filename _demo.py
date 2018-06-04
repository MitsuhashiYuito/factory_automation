import numpy as np
import cv2
import time
import subprocess
import time

#W, H = 480, 640
#cap.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
#cap.set(cv2.CAP_PROP_FRAME_WIDTH, W)
CROP_W, CROP_H = 150,200

cap = cv2.VideoCapture(0)

ret, frame = cap.read()
print(frame.shape)

while(True):
    ret, frame = cap.read()
    W, H, _ = frame.shape
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    mask = cv2.inRange(frame, (0,0,0), (200,200,200))
    frame_canny = cv2.Canny(mask, threshold1=150, threshold2=300)

    # crop RoI
    roi = frame_canny[CROP_H:-CROP_H, CROP_W:-CROP_W]

    num_white = cv2.countNonZero(roi)
    is_exist = True if num_white > 700 else False

    if is_exist:
        # find moments
        print(num_white)
        mu = cv2.moments(roi, False)
        x, y = int(mu["m10"]/mu["m00"])+CROP_W, int(mu["m01"]/mu["m00"])+CROP_H
 #       frame = cv2.circle(frame, (x, y), 20, (0, 0, 255), -1)

    output_image = np.zeros((W*2, H*2, 3))
    output_image[:W, :H] = frame/255
    output_image[W:, :H] = np.stack((mask, mask, mask), axis=-1)
    output_image[:W, H:] = np.stack((frame_canny, frame_canny, frame_canny), axis=-1)
    output_image[W+CROP_H:-CROP_H, H+CROP_W:-CROP_W] = np.stack((roi, roi, roi), axis=-1)

    cv2.imshow('demo', output_image)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    if is_exist:
#        subprocess.call(["python3", "_pick_place.py"])
        now = time.time()
        cv2.imwrite('sd_0/' + str(now) +  '.png',frame)
        print('now capture', now)
        break
        
cap.release()
cv2.destroyAllWindows()
