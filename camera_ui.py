import sys
from PySide6.QtWidgets import QApplication
from system_controller import SystemController

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = SystemController()
    window.show()

    sys.exit(app.exec())