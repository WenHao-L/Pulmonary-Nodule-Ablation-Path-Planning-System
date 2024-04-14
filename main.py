import sys
from PyQt5.QtWidgets import QApplication
from qdarkstyle import load_stylesheet
from src.main_window import MainWindow
import multiprocessing

if __name__ == "__main__":
    multiprocessing.freeze_support()
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.setWindowTitle("肺肿瘤消融规划系统")
    app.setStyleSheet(load_stylesheet(qt_api='pyqt5'))

    main_window.showMaximized()
    sys.exit(app.exec_())
