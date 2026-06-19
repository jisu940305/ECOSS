import cv2
from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QImage
import os


class CameraThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self.running = True
        self.cap = cv2.VideoCapture(cam_index)
        self.camera_available = self.cap.isOpened()

        if not self.camera_available:
            print(f"Camera {cam_index} not found -> TEST MODE")
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def run(self):
       while self.running:

        if self.camera_available:

            ret, frame = self.cap.read()

            if not ret:
                self.msleep(100)
                continue

        else:

            BASE_DIR = os.path.dirname(os.path.abspath(__file__))

            img_path = os.path.join(
                BASE_DIR,
                "test_images",
                "cam1.jpg" if self.cam_index == 0 else "cam2.jpg"
            )

            # print("IMG =", img_path)
            # print("EXISTS =", os.path.exists(img_path))

            frame = cv2.imread(img_path)

            # print("FRAME =", frame is not None)

            if frame is None:
                self.msleep(1000)
                continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape

        image = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        self.last_cv_frame = frame.copy()
        self.frame_signal.emit(image)

        self.msleep(30)

    def stop(self):
        self.running = False
        self.cap.release()
        self.quit()
        self.wait()