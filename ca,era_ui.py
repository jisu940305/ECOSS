import sys
import cv2

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QImage, QPixmap


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        print("STEP 1")

        self.setWindowTitle("ECOSS AOI")

        self.label = QLabel("Starting...")
        self.label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(self.label)

        print("STEP 2")

        self.cap = cv2.VideoCapture(0)

        print("STEP 3")

        if not self.cap.isOpened():
            print("CAMERA OPEN FAILED")
        else:
            print("CAMERA OPEN SUCCESS")

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        print("STEP 4")

    def update_frame(self):

        print("FRAME")

        ret, frame = self.cap.read()

        if not ret:
            print("READ FAILED")
            return

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        h, w, ch = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            ch * w,
            QImage.Format_RGB888
        )

        pixmap = QPixmap.fromImage(image)

        self.label.setPixmap(pixmap)

    def closeEvent(self, event):

        if self.cap.isOpened():
            self.cap.release()

        event.accept()


app = QApplication(sys.argv)

print("APP START")

window = MainWindow()

print("WINDOW CREATED")

window.resize(1000, 700)

window.show()

print("WINDOW SHOW")

sys.exit(app.exec())
