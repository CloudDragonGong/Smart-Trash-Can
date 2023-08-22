import cv2

cap = cv2.VideoCapture(0)

_ , frame = cap.read()
cv2.imwrite('2.png',frame)
print('finished')
