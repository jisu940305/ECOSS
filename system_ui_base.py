import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFrame, QLabel, QTableWidget, QHeaderView,
    QPushButton, QCheckBox, QSizePolicy,
    QStackedLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap


class SystemUIBase(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ECOSS Vision Inspection System - INDUSTRIAL")
        self.resize(1280, 720)
        self.setMinimumSize(1024, 768)

    def build_ui(self):

        cw = QWidget()
        self.setCentralWidget(cw)

        main = QVBoxLayout(cw)

        # ================= TOP =================
        top = QFrame()
        top.setStyleSheet("background:#0f172a;")
        topLay = QHBoxLayout(top)

        logo = QLabel()
        logo_path = os.path.join(os.getcwd(), "logo_1.png")

        if os.path.exists(logo_path):
            pix = QPixmap(logo_path)
            logo.setPixmap(pix.scaled(120, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        logo.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        title = QLabel("Smart Edge AI Vision System")
        title.setStyleSheet("font-size:22px;color:white;font-weight:bold;")

        self.clock = QLabel()
        self.clock.setStyleSheet("font-size:18px;color:white;")

        topLay.addWidget(logo)
        topLay.addWidget(title, 1)
        topLay.addWidget(self.clock)

        main.addWidget(top)

        # ================= CENTER =================
        center = QHBoxLayout()

        left = QVBoxLayout()
        cams = QHBoxLayout()

        cams.setStretch(0, 1)
        cams.setStretch(1, 1)

        # ================= CAM1 =================
        self.cam1_frame = QFrame()
        self.cam1_frame.setStyleSheet("""
            background:black;
            border:3px solid #00d084;
        """)

        self.cam1 = QLabel()
        self.cam1.setAlignment(Qt.AlignCenter)
        self.cam1.setScaledContents(False)
        self.cam1.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.cam1_status = QLabel("")
        self.cam1_status.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.cam1_status.setStyleSheet("""
            color:white;
            font-size:22px;
            font-weight:bold;
            background:rgba(0,0,0,160);
            padding:6px 10px;
            border-radius:6px;
        """)

        cam1_stack = QStackedLayout()
        cam1_stack.setStackingMode(QStackedLayout.StackAll)
        cam1_stack.addWidget(self.cam1)
        cam1_stack.addWidget(self.cam1_status)

        self.cam1_frame.setLayout(cam1_stack)

        # ================= CAM2 =================
        self.cam2_frame = QFrame()
        self.cam2_frame.setStyleSheet("""
            background:black;
            border:3px solid #00d084;
        """)

        self.cam2 = QLabel()
        self.cam2.setAlignment(Qt.AlignCenter)
        self.cam2.setScaledContents(False)
        self.cam2.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self.cam2_status = QLabel("")
        self.cam2_status.setAlignment(Qt.AlignTop | Qt.AlignRight)
        self.cam2_status.setStyleSheet("""
            color:white;
            font-size:22px;
            font-weight:bold;
            background:rgba(0,0,0,160);
            padding:6px 10px;
            border-radius:6px;
        """)

        cam2_stack = QStackedLayout()
        cam2_stack.setStackingMode(QStackedLayout.StackAll)
        cam2_stack.addWidget(self.cam2)
        cam2_stack.addWidget(self.cam2_status)

        self.cam2_frame.setLayout(cam2_stack)

        cams.addWidget(self.cam1_frame, 1)
        cams.addWidget(self.cam2_frame, 1)

        left.addLayout(cams, 6)

        # ================= BOTTOM =================
        bottom = QHBoxLayout()
        bottom.setStretch(0, 1)  # NG1
        bottom.setStretch(1, 1)  # NG2
        bottom.setStretch(2, 3)  # log 크게
        self.ngPreview1 = QLabel("NG1")
        self.ngPreview2 = QLabel("NG2")

        # 🔥 핵심: 절대 안 커지게 고정
        for w in [self.ngPreview1, self.ngPreview2]:
            w.setFixedSize(180, 120)
            w.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            w.setAlignment(Qt.AlignCenter)
            w.setStyleSheet("""
                background:black;
                color:white;
                border:2px solid red;
            """)

        self.log = QTableWidget(0, 3)
        self.log.setHorizontalHeaderLabels(["TIME", "CAM", "RESULT"])
        self.log.horizontalHeader().setStretchLastSection(True)
        self.log.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        bottom.addWidget(self.ngPreview1, 1)
        bottom.addWidget(self.ngPreview2, 1)
        bottom.addWidget(self.log, 3)

        left.addLayout(bottom, 2)

        center.addLayout(left, 4)

        # ================= RIGHT =================
        right = QVBoxLayout()
        self.right_panel = QFrame()
        self.right_panel.setFixedWidth(260)
        self.right_panel.setStyleSheet("background:transparent;")

        right = QVBoxLayout(self.right_panel)
        right.setSpacing(8)
        right.setContentsMargins(10, 10, 10, 10)
        self.result = QLabel("READY") 
        self.result.setAlignment(Qt.AlignCenter)
        self.result.setMinimumHeight(100)
        self.result.setStyleSheet("""
            background:#1e293b;
            color:white;
            font-size:18px;
            font-weight:bold;
            border:2px solid #38bdf8;
            border-radius:10px;
        """)

        self.okLbl = QLabel("OK : 0")
        self.ngLbl = QLabel("NG : 0")
        self.totalLbl = QLabel("TOTAL : 0")
        self.yieldLbl = QLabel("YIELD : 0%")

        for w in [self.okLbl, self.ngLbl, self.totalLbl, self.yieldLbl]:
            w.setStyleSheet("font-size:20px;")

        self.startBtn = QPushButton("START AUTO")
        self.stopBtn = QPushButton("STOP")
        self.grabBtn = QPushButton("GRAB")

        self.startBtn.setStyleSheet("background:#22c55e;color:white;padding:10px;")
        self.stopBtn.setStyleSheet("background:#ef4444;color:white;padding:10px;")
        self.grabBtn.setStyleSheet("background:#3b82f6;color:white;padding:10px;")

        self.saveOkCheck = QCheckBox("SAVE OK IMAGES")
        self.saveOkCheck.setStyleSheet("font-size:14px;color:white;")

        self.openImgBtn = QPushButton("OPEN IMAGE FOLDER") 
        self.openImgBtn.setStyleSheet("background:#f59e0b;color:white;padding:8px;")

        right.addWidget(self.result)
        right.addWidget(self.okLbl)
        right.addWidget(self.ngLbl)
        right.addWidget(self.totalLbl)
        right.addWidget(self.yieldLbl)
        right.addWidget(self.saveOkCheck)

        right.addWidget(self.startBtn)
        right.addWidget(self.grabBtn)
        right.addWidget(self.stopBtn)

        right.addStretch()
        right.addWidget(self.openImgBtn)

        center.addWidget(self.right_panel, 1)

        main.addLayout(center)

        cw.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main.setContentsMargins(0, 0, 0, 0)
        main.setSpacing(6)
        
    
    # ================= IMAGE UPDATE =================
    def set_cam1_image(self, pixmap: QPixmap):
        self.cam1.setPixmap(
            pixmap.scaled(self.cam1.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    def set_cam2_image(self, pixmap: QPixmap):
        self.cam2.setPixmap(
            pixmap.scaled(self.cam2.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

    # ================= STATUS =================
    def set_cam1_status(self, text: str):
        self.cam1_status.setText(text)

    def set_cam2_status(self, text: str):
        self.cam2_status.setText(text)