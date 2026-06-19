import os
import time
from datetime import datetime
import cv2
from ultralytics import YOLO
import numpy as np
import torch
import csv

from PySide6.QtWidgets import QTableWidgetItem
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QPixmap, QImage, QDesktopServices

# 다른 모듈 임포트
from camera_thread import CameraThread
from system_ui_base import SystemUIBase

class SystemController(SystemUIBase):

    def __init__(self):
        super().__init__()

        import os

        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        
        model_path = os.path.join(BASE_DIR, "best.pt") # pt > engine 로 수정해야함 jetson에서 
        

        print("MODEL =", model_path)
        print("EXISTS =", os.path.exists(model_path))

        self.model = YOLO(model_path)
        
        print("YOLO WARMUP START")
        dummy1 = np.zeros((320, 320, 3), dtype=np.uint8)
        dummy2 = np.zeros((320, 320, 3), dtype=np.uint8)

        self.model(
            [dummy1, dummy2],
            imgsz=320,
            verbose=False
        )
        print("YOLO WARMUP DONE")

        print("CUDA:", torch.cuda.is_available())

        if torch.cuda.is_available():
            print("GPU:", torch.cuda.get_device_name(0))
        else:
            print("GPU: CPU MODE")
        
        self.ok = 0
        self.ng = 0
        self.auto_mode = False

        # 부모 클래스의 UI 빌드 호출 및 이벤트 연결
        self.build_ui()
        self.connect_signals()
        
        self.setup_threads()
        self.setup_timers()

    def connect_signals(self):
        self.startBtn.clicked.connect(self.start_auto)
        self.stopBtn.clicked.connect(self.stop_all)
        self.grabBtn.clicked.connect(self.grab_once)
        self.openImgBtn.clicked.connect(self.open_image_folder)

    def setup_threads(self):
        self.cam1_thread = CameraThread(0)
        self.cam2_thread = CameraThread(2)

        self.cam1_thread.frame_signal.connect(self.update_camera1)
        self.cam2_thread.frame_signal.connect(self.update_camera2)

        self.cam1_thread.start()
        self.cam2_thread.start()
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
                    Qt.IgnoreAspectRatio, 
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

    def update_clock(self):
        self.clock.setText(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def update_camera1(self, image):
        pix = QPixmap.fromImage(image)
        self.last_frame_cam1 = pix
        if hasattr(self.cam1_thread, "last_cv_frame"):
            self.last_cv_cam1 = self.cam1_thread.last_cv_frame.copy()
        self.cam1.setPixmap(
        pix.scaled(
            self.cam1.size(),
            Qt.KeepAspectRatio,
            Qt.FastTransformation
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
                 Qt.FastTransformation
            )
        )

    def inspect(self, source="AUTO"):
        start = time.time()
        results = []

        if hasattr(self, "last_cv_cam1") and hasattr(self, "last_cv_cam2"):
            frames = [self.last_cv_cam1, self.last_cv_cam2]

            yolo_results = self.model(
                frames,
                imgsz=320,
                verbose=False
            )

            # CAM1
            ok = False
            for box in yolo_results[0].boxes:
                if float(box.conf) > 0.3:
                    ok = True
                    break
            results.append(("CAM1", "OK" if ok else "NG"))

            # CAM2
            ok = False
            for box in yolo_results[1].boxes:
                if float(box.conf) > 0.3:
                    ok = True
                    break
            results.append(("CAM2", "OK" if ok else "NG"))

        for cam, result in results:
            if cam == "CAM1":
                overlay = self.cam1_status
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
                overlay = self.cam2_status
                frame = self.cam2_frame
                if hasattr(self, "last_frame_cam2"):
                    self.ngPreview2.setPixmap(
                        self.last_frame_cam2.scaled(
                            self.ngPreview2.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )

            overlay.setText(result)

            if result == "OK":
                self.ok += 1
                frame.setStyleSheet("background:black;border:3px solid #00d084;")
                overlay.setStyleSheet("""
                    color:#00ff7f;
                    font-size:28px;
                    font-weight:bold;
                    background:rgba(0,0,0,160);
                    padding:10px;
                """)
            else:
                self.ng += 1
                frame.setStyleSheet("background:black;border:3px solid #ef4444;")
                overlay.setStyleSheet("""
                    color:#ff3b3b;
                    font-size:28px;
                    font-weight:bold;
                    background:rgba(0,0,0,160);
                    padding:10px;
                """)

            self.save_image(cam, result)

            self.save_log(cam, result)
            
            row = self.log.rowCount()
            self.log.insertRow(row)
            self.log.setItem(row, 0, QTableWidgetItem(datetime.now().strftime("%H:%M:%S")))
            self.log.setItem(row, 1, QTableWidgetItem(cam))
            self.log.setItem(row, 2, QTableWidgetItem(result))

            self.update_stats()
            print("검사시간 =", time.time() - start)

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

    def save_image(self, cam, result):
        base_folder = "images"
        date_folder = datetime.now().strftime("%Y%m%d")
        folder = os.path.join(base_folder, date_folder, "img")

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

    def update_stats(self):
        total = self.ok + self.ng
        self.okLbl.setText(f"OK : {self.ok}")
        self.ngLbl.setText(f"NG : {self.ng}")
        self.totalLbl.setText(f"TOTAL : {total}")

        if total > 0:
            self.yieldLbl.setText(f"YIELD : {self.ok / total * 100:.1f}%")
        else:
            self.yieldLbl.setText("YIELD : 0%")

    def closeEvent(self, event):
        self.cam1_thread.stop()
        self.cam2_thread.stop() 
        event.accept()

    def open_image_folder(self):
        folder = os.path.abspath("images")
        os.makedirs(folder, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(folder))

    def save_log(self, cam, result):

        os.makedirs("logs", exist_ok=True)

        file_path = os.path.join(
            "logs",
            datetime.now().strftime("%Y%m%d") + ".csv"
        )

        file_exists = os.path.exists(file_path)

        with open(
            file_path,
            "a",
            newline="",
            encoding="utf-8-sig"
        ) as f:

            writer = csv.writer(f)

            if not file_exists:
                writer.writerow(
                    ["DATE", "TIME", "CAM", "RESULT"]
                )

            writer.writerow([
                datetime.now().strftime("%Y-%m-%d"),
                datetime.now().strftime("%H:%M:%S"),
                cam,
                result
            ])