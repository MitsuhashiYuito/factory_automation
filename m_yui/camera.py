import numpy as np
import cv2

cap = cv2.VideoCapture(0)

cap.set(3,400) # 幅
cap.set(4,300) # 高さ
cap.set(5,30)  # FPS

i=0

while True: # 無限ループを作る
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    frame =  cv2.Canny(frame, threshold1 = 150, threshold2=200)
    cv2.imshow('frame',frame)
    key = cv2.waitKey(1)&0xFF
    if key == ord('q'):
        break
    if key == ord('s'):
        i += 1
        cv2.imwrite(imabe/f"{i}.png",frame)


cap.release()
cv2.destroyAllWindows()
