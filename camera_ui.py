import sys
import cv2
import random
import os
import numpy as np

from datetime import datetime
from ultralytics import YOLO
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *



# =========================
# CAMERA THREAD
# =========================
class CameraThread(QThread):
    frame_signal = Signal(QImage)

    def __init__(self, cam_index=0):
        super().__init__()
        self.cam_index = cam_index
        self.running = True
        self.cap = cv2.VideoCapture(cam_index)
        self.model = YOLO("best.pt")

    def run(self):
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
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


# =========================
# MAIN UI
# =========================
class AOIWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ECOSS Vision Inspection System - INDUSTRIAL")
        self.resize(1200, 800)
        self.model = YOLO("best.pt")
        self.ok = 0
        self.ng = 0
        self.auto_mode = False

        self.build_ui()
        self.setup_threads()
        self.setup_timers()


    # =========================
    # UI
    # =========================
    def build_ui(self):

        cw = QWidget()
        self.setCentralWidget(cw)

        main = QVBoxLayout(cw)

        # TOP
        top = QFrame()
        top.setStyleSheet("background:#0f172a;")
        topLay = QHBoxLayout(top)

        logo = QLabel()

        logo_path = os.path.join(os.getcwd(), "logo.png")
        logo_pix = QPixmap(logo_path)

        logo.setPixmap(logo_pix.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        title = QLabel("VISION INSPECTION SYSTEM (INDUSTRIAL)")
        title.setStyleSheet("font-size:24px;color:white;font-weight:bold;")

        self.clock = QLabel()
        self.clock.setStyleSheet("font-size:18px;color:white;")

        topLay.addWidget(logo)
        topLay.addWidget(title, 1)
        topLay.addWidget(self.clock)

        main.addWidget(top)

        # CENTER
        center = QHBoxLayout()

        # LEFT
        left = QVBoxLayout()

        cams = QHBoxLayout()

       # =========================
        # CAM1
        # =========================
        self.cam1_frame = QFrame()
        self.cam1_frame.setFixedSize(900, 800)
        self.cam1_frame.setStyleSheet("""
            background:black;
            border:3px solid #00d084;
        """)

        # 중요: 오버레이를 위에 띄우기 위해 QGridLayout이나 겹치기 구조를 사용하거나, 
        # 위젯 내부 레이아웃 관리를 위해 아래와 같이 설정합니다.
        cam1_layout = QVBoxLayout(self.cam1_frame)
        cam1_layout.setContentsMargins(5, 5, 5, 5) # 테두리 안쪽 여백 최소화

        self.cam1 = QLabel()
        # self.cam1.setFixedSize(900, 800) 👈 이 줄을 삭제하여 프레임에 맞게 자동 조절되게 합니다.
        self.cam1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cam1.setAlignment(Qt.AlignCenter)

        self.cam1_overlay = QLabel("READY")
        self.cam1_overlay.setFixedSize(140, 60)
        self.cam1_overlay.setStyleSheet("""
            color:white; font-size:22px; font-weight:bold;
            background:rgba(0,0,0,160); border:none; border-radius:6px;
        """)
        self.cam1_overlay.setAlignment(Qt.AlignCenter)

        cam1_layout.addWidget(self.cam1, 1) # 카메라 영상이 대부분의 공간을 차지하도록 설정
        cam1_layout.addWidget(self.cam1_overlay, 0, Qt.AlignBottom | Qt.AlignRight)
   
        # =========================
        # CAM2
        # =========================
        self.cam2_frame = QFrame()
        self.cam2_frame.setFixedSize(900, 800)
        self.cam2_frame.setStyleSheet("""
            background:black;
            border:3px solid #00d084;
        """)

        cam2_layout = QVBoxLayout(self.cam2_frame)
        cam2_layout.setContentsMargins(5, 5, 5, 5)

        self.cam2 = QLabel()
        # self.cam2.setFixedSize(900, 800) 👈 이 줄도 삭제
        self.cam2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.cam2.setAlignment(Qt.AlignCenter)

        self.cam2_overlay = QLabel("READY")
        self.cam2_overlay.setFixedSize(140, 60)
        self.cam2_overlay.setStyleSheet("""
            color:white; font-size:22px; font-weight:bold;
            background:rgba(0,0,0,160); border:none; border-radius:6px;
        """)
        self.cam2_overlay.setAlignment(Qt.AlignCenter)

        cam2_layout.addWidget(self.cam2, 1)
        cam2_layout.addWidget(self.cam2_overlay, 0, Qt.AlignBottom | Qt.AlignRight)
        cams.addWidget(self.cam1_frame)
        cams.addWidget(self.cam2_frame)

        left.addLayout(cams)

        bottom = QHBoxLayout()

        self.ngPreview1 = QLabel()
        self.ngPreview1.setAlignment(Qt.AlignCenter)
        self.ngPreview1.setStyleSheet(
            "background:black;color:white;border:2px solid red;"
        )

        self.ngPreview2 = QLabel()
        self.ngPreview2.setAlignment(Qt.AlignCenter)
        self.ngPreview2.setStyleSheet(
            "background:black;color:white;border:2px solid red;"
        )
        self.ngPreview1.setFixedSize(300, 250)
        self.ngPreview2.setFixedSize(300, 250)

        self.log = QTableWidget(0, 3)
        self.log.setHorizontalHeaderLabels(["TIME", "CAM", "RESULT"])
        self.log.horizontalHeader().setStretchLastSection(True)
        self.log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        bottom.addWidget(self.ngPreview1, 1)
        bottom.addWidget(self.ngPreview2, 1)
        bottom.addWidget(self.log)

        left.addLayout(bottom)

        center.addLayout(left, 4)

        # RIGHT
        right = QVBoxLayout()

        self.result = QLabel("READY")
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setFixedHeight(120)
        self.result.setStyleSheet("""
            QLabel{
                background:#1e293b;
                color:white;
                font-size:16px;
                font-weight:bold;
                border:2px solid #38bdf8;
                border-radius:10px;
            }
        """)

        self.okLbl = QLabel("OK : 0")
        self.ngLbl = QLabel("NG : 0")
        self.totalLbl = QLabel("TOTAL : 0")
        self.yieldLbl = QLabel("YIELD : 0%")

        # =========================
        # NG UI (여기 추가)
        # =========================
        

  

        for w in [self.okLbl, self.ngLbl, self.totalLbl, self.yieldLbl]:
            w.setStyleSheet("font-size:22px;")

        self.startBtn = QPushButton("START AUTO")
        self.stopBtn = QPushButton("STOP")
        self.grabBtn = QPushButton("GRAB")

        self.startBtn.setStyleSheet("background:#22c55e;color:white;padding:10px;")
        self.stopBtn.setStyleSheet("background:#ef4444;color:white;padding:10px;")
        self.grabBtn.setStyleSheet("background:#3b82f6;color:white;padding:10px;")

        self.startBtn.clicked.connect(self.start_auto)
        self.stopBtn.clicked.connect(self.stop_all)
        self.grabBtn.clicked.connect(self.grab_once)

        self.saveOkLabel = QLabel("OK 이미지 저장 옵션")

# 👇 바로 아래
        self.saveOkLabel.setStyleSheet("""
            font-size:14px;
            color:#cbd5e1;
            font-weight:bold;
        """)
        self.saveOkLabel.setStyleSheet("font-size:14px;color:#94a3b8;")

        self.saveOkCheck = QCheckBox("SAVE OK IMAGES")

        self.saveOkCheck = QCheckBox("SAVE OK IMAGES")
        self.saveOkCheck.setChecked(False)

        # 👇 여기 추가
        self.saveOkCheck.setStyleSheet("""
            font-size:16px;
            color:#00d084;
            font-weight:bold;
        """)
        self.saveOkCheck.setChecked(False)
        self.saveOkCheck.setStyleSheet("font-size:16px;color:white;")

        right.addWidget(self.saveOkLabel)
        right.addWidget(self.saveOkCheck)
        

     
       

        right.addWidget(self.result)
        right.addWidget(self.okLbl)
        right.addWidget(self.ngLbl)
        right.addWidget(self.totalLbl)
        right.addWidget(self.yieldLbl)

        
        right.addWidget(self.saveOkLabel)
        right.addWidget(self.saveOkCheck)
    

        

        right.addWidget(self.startBtn)
        right.addWidget(self.grabBtn)
        right.addWidget(self.stopBtn)
        right.addStretch()

        self.openImgBtn = QPushButton("OPEN IMAGE FOLDER")
        self.openImgBtn.setStyleSheet("background:#f59e0b;color:white;padding:8px;")
        self.openImgBtn.clicked.connect(self.open_image_folder)

        right.addWidget(self.openImgBtn)

        center.addLayout(right, 1)

        main.addLayout(center)

    # =========================
    # THREAD
    # =========================
    def setup_threads(self):
        self.cam1_thread = CameraThread(0)
        self.cam2_thread = CameraThread(1)

        self.cam1_thread.frame_signal.connect(self.update_camera1)
        self.cam2_thread.frame_signal.connect(self.update_camera2)

        self.cam1_thread.start()
        self.cam2_thread.start()
        # 즉시 초기 프레임 표시용
        QTimer.singleShot(100, self.force_initial_frames)


    def force_initial_frames(self):

        def set_cam(label, frame):
            if frame is None:
                return
            pix = QPixmap.fromImage(
                QImage(
                    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB),
                    frame.shape[1],
                    frame.shape[0],
                    QImage.Format_RGB888
                )
            )
            label.setPixmap(
                pix.scaled(
                    label.size(),
                    Qt.IgnoreAspectRatio,   # ⭐ 중요 (늘어남 방지)
                    Qt.SmoothTransformation
                )
            )

        if hasattr(self.cam1_thread, "last_cv_frame"):
            set_cam(self.cam1, self.cam1_thread.last_cv_frame)

        if hasattr(self.cam2_thread, "last_cv_frame"):
            set_cam(self.cam2, self.cam2_thread.last_cv_frame)

    def setup_timers(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)

        self.inspect_timer = QTimer()
        self.inspect_timer.timeout.connect(self.auto_inspect)

    # =========================
    # CLOCK
    # =========================
    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # =========================
    # CAMERA
    # =========================
    def update_camera1(self, image):

        pix = QPixmap.fromImage(image)

        self.last_frame_cam1 = pix
        if hasattr(self.cam1_thread, "last_cv_frame"):
            self.last_cv_cam1 = self.cam1_thread.last_cv_frame.copy()
        self.cam1.setPixmap(
            pix.scaled(
                self.cam1.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )


    def update_camera2(self, image):

        pix = QPixmap.fromImage(image)

        self.last_frame_cam2 = pix
        if hasattr(self.cam2_thread, "last_cv_frame"):
             self.last_cv_cam2 = self.cam2_thread.last_cv_frame.copy()
        self.cam2.setPixmap(
            pix.scaled(
                self.cam2.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
        )

    # =========================
    # INSPECTION
    # =========================
    def inspect(self, source="AUTO"):

        results = []

        # =====================
        # CAM1 inference
        # =====================
        if hasattr(self, "last_cv_cam1"):

            yolo_result = self.model(self.last_cv_cam1, verbose=False)[0]

            ok = False
            for box in yolo_result.boxes:
                if float(box.conf) > 0.3:
                    ok = True
                    break

            results.append(("CAM1", "OK" if ok else "NG"))

        # =====================
        # CAM2 inference
        # =====================
        if hasattr(self, "last_cv_cam2"):

            yolo_result = self.model(self.last_cv_cam2, verbose=False)[0]

            ok = False
            for box in yolo_result.boxes:
                if float(box.conf) > 0.3:
                    ok = True
                    break

            results.append(("CAM2", "OK" if ok else "NG"))

        # =====================
        # UI UPDATE + LOG + SAVE
        # =====================
        for cam, result in results:

            # ---------------------
            # CAM 선택
            # ---------------------
            if cam == "CAM1":
                overlay = self.cam1_overlay
                frame = self.cam1_frame

                if hasattr(self, "last_frame_cam1"):
                    self.ngPreview1.setPixmap(
                        self.last_frame_cam1.scaled(
                            self.ngPreview1.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )

            else:
                overlay = self.cam2_overlay
                frame = self.cam2_frame

                if hasattr(self, "last_frame_cam2"):
                    self.ngPreview2.setPixmap(
                        self.last_frame_cam2.scaled(
                            self.ngPreview2.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )

            # =====================
            # OK / NG 표시 (핵심)
            # =====================
            overlay.setText(result)

            if result == "OK":

                self.ok += 1
                frame.setStyleSheet(
                    "background:black;border:3px solid #00d084;"
                )

                overlay.setStyleSheet("""
                    color:#00ff7f;
                    font-size:28px;
                    font-weight:bold;
                    background:rgba(0,0,0,160);
                    padding:10px;
                """)

            else:

                self.ng += 1
                frame.setStyleSheet(
                    "background:black;border:3px solid #ef4444;"
                )

                overlay.setStyleSheet("""
                    color:#ff3b3b;
                    font-size:28px;
                    font-weight:bold;
                    background:rgba(0,0,0,160);
                    padding:10px;
                """)

            # =====================
            # SAVE IMAGE
            # =====================
            self.save_image(cam, result)

            # =====================
            # LOG TABLE (핵심)
            # =====================
            row = self.log.rowCount()
            self.log.insertRow(row)

            self.log.setItem(
                row, 0,
                QTableWidgetItem(datetime.now().strftime("%H:%M:%S"))
            )

            self.log.setItem(row, 1, QTableWidgetItem(cam))
            self.log.setItem(row, 2, QTableWidgetItem(result))

    # =====================
    # STATS UPDATE
    # =====================
            self.update_stats()

    # =========================
    # AUTO
    # =========================
    def start_auto(self):
        self.auto_mode = True
        self.result.setText("RUNNING")
        self.inspect_timer.start(1000)

    def stop_all(self):
        self.auto_mode = False
        self.inspect_timer.stop()
        self.result.setText("STOP")

    def auto_inspect(self):
        if self.auto_mode:
            self.inspect("AUTO")

    def grab_once(self):
        self.inspect("GRAB")

    # =========================
    # NG SAVE
    # =========================
    def save_image(self, cam, result):

        base_folder = "images"

        # 날짜 폴더 생성
        date_folder = datetime.now().strftime("%Y%m%d")
        folder = os.path.join(base_folder, date_folder, "img")

        # NG / OK 분리
        if result == "NG":
            folder = os.path.join(folder, "NG")
        else:
            if not self.saveOkCheck.isChecked():
                return
            folder = os.path.join(folder, "OK")

        os.makedirs(folder, exist_ok=True)

        filename = f"{cam}_{datetime.now().strftime('%H%M%S_%f')}.png"
        path = os.path.join(folder, filename)

        if cam == "CAM1" and hasattr(self, "last_frame_cam1"):
            self.last_frame_cam1.save(path)

        elif cam == "CAM2" and hasattr(self, "last_frame_cam2"):
            self.last_frame_cam2.save(path)


    # =========================
    # STATS
    # =========================
    def update_stats(self):

        total = self.ok + self.ng

        self.okLbl.setText(f"OK : {self.ok}")
        self.ngLbl.setText(f"NG : {self.ng}")
        self.totalLbl.setText(f"TOTAL : {total}")

        if total > 0:
            self.yieldLbl.setText(f"YIELD : {self.ok / total * 100:.1f}%")
        else:
            self.yieldLbl.setText("YIELD : 0%")

    # =========================
    # CLOSE
    # =========================
    def closeEvent(self, event):
        self.cam1_thread.stop()
        self.cam2_thread.stop() 
        event.accept()

    def open_image_folder(self):
        folder = os.path.abspath("images")
        os.makedirs(folder, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))
# =========================
# RUN
# =========================
app = QApplication(sys.argv)

window = AOIWindow()
window.show()

sys.exit(app.exec())