import cv2

cap = cv2.VideoCapture(1)

print("OPEN:", cap.isOpened())

while True:
    ret, frame = cap.read()

    if not ret:
        print("READ FAIL")
        break

    cv2.imshow("CAM", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
