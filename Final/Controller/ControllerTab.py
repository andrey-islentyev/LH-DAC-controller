from AbstractTab import AbstractTab
from Graphics.MenuSection import MenuSection

from .ArduinoController import ArduinoController

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ControllerTab(AbstractTab):
    def __init__(self):
        super().__init__()
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background-color: white")
        self.viewWidget = QWidget()
        self.viewLayout = QHBoxLayout(self.viewWidget)
        self.viewLayout.setContentsMargins(0,0,0,0)
        self.viewLayout.setSpacing(0)
        self.controller = ArduinoController(self.canvas)
        self.monitoringList = self.controller.scrollArea
        self.monitoringList.setStyleSheet("QScrollArea{border-right: 2px; border-color: #AAA; border-style: solid;}")
        self.monitoringList.setHidden(False)
        self.monitoringList.setFixedWidth(QApplication.primaryScreen().availableGeometry().width() // 5)
        self.viewLayout.addWidget(self.monitoringList)
        self.viewLayout.addWidget(self.canvas)
        self.mainLayout.addWidget(self.viewWidget)
        self.addActionsSection()

    def addActionsSection(self):
        actionSection = MenuSection("Actions")
        actionSection.mainLayout.addWidget(self.controller.addButton, 0, 0, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.connectButton, 1, 0, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.removeButton, 2, 0, 1, 1)
        self.menuWidget.add_section(actionSection)