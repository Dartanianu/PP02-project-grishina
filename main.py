import sys

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from app.main_window import MainWindow
from config import APP_NAME
from styles import FONT_FAMILY, STYLESHEET

def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    app.setFont(QFont(FONT_FAMILY, 11))
    app.setStyleSheet(STYLESHEET)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__=="__main__":
    main()