from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from Calibration.CalibrationTab import CalibrationTab
from Analysis.AnalysisTab import AnalysisTab
from Controller.ControllerTab import ControllerTab

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        rect = QApplication.primaryScreen().availableGeometry()
        self.maxw = rect.width()
        self.maxh = rect.height()
        
        self.setWindowTitle("Laser Heater Controller")
        self.setWindowIcon(QIcon("Final/icon.png"))
        self.setGeometry(self.maxw // 4, self.maxh // 4, self.maxw // 2, self.maxh // 2)
        self.initUI()

    def initUI(self):
        self.rootWidget = QTabWidget()
        self.rootWidget.setStyleSheet("QTabWidget::pane {border: 2px solid #AAA;} QTabWidget::tab-bar {left:10px}")
        self.rootWidget.tabBar().setStyleSheet("""
            QTabBar::tab {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #DDD,
            stop: 0.25 #D8D8D8, stop: 0.5 #EEE, stop: 0.75 #D8D8D8, stop: 1.0 #DDD); border: 2px solid #AAA;
            border-top-left-radius: 4px; border-top-right-radius: 4px; min-width: 100 rem; padding: 2px; bottom: -2px}
            QTabBar::tab:selected {background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFF,
            stop: 0.25 #F8F8F8, stop: 0.5 #EEE, stop: 0.75 #F8F8F8, stop: 1.0 #FFF); border-color: #666;
            border-bottom-color: #AAA; margin-left: -4px; margin-right: -4px;}
            QTabBar::tab:first:selected {margin-left: 0px;}
            QTabBar::tab:last:selected {margin-right: 0px;}
            QTabBar::tab:only-one {margin: 0px;}
            QTabBar::tab:!selected {margin-top: 3px}""")

        self.setCentralWidget(self.rootWidget)
        self.rootWidget.setTabsClosable(False)
        self.rootWidget.addTab(CalibrationTab(), "Calibration")
        self.rootWidget.addTab(AnalysisTab(), "Analysis")
        self.rootWidget.addTab(ControllerTab(), "Control")