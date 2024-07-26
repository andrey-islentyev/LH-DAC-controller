from AbstractTab import AbstractTab
from Graphics.MenuSection import MenuSection
from .AnalysisController import AnalysisController
from .ButtonPad import ButtonPad

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class AnalysisTab(AbstractTab):
    def __init__(self):
        super().__init__()
        self.viewWidget = QWidget()
        self.viewLayout = QHBoxLayout(self.viewWidget)
        self.viewLayout.setContentsMargins(0,0,0,0)
        self.viewLayout.setSpacing(0)
        self.controller = AnalysisController(self.canvas)
        self.monitoringList = self.controller.scrollArea
        self.monitoringList.setStyleSheet("QScrollArea{border-right: 2px; border-color: #AAA; border-style: solid;}")
        self.monitoringList.setHidden(True)
        self.monitoringList.setFixedWidth(QApplication.primaryScreen().availableGeometry().width() // 5)
        self.viewLayout.addWidget(self.monitoringList)
        self.viewLayout.addWidget(self.canvas)
        self.mainLayout.addWidget(self.viewWidget)
        
        self.addAnalysisSection()
        self.addMonitorSection()
        self.addViewSection()
    
    def addAnalysisSection(self):
        analysisSection = MenuSection("Analysis")
        analysisSection.mainLayout.addWidget(self.controller.calibrationButton, 0, 0, 1, 2)
        analysisSection.mainLayout.addWidget(self.controller.calibration, 0, 2, 1, 4)
        analysisSection.mainLayout.addWidget(self.controller.fileButton, 1, 0, 1, 2)
        analysisSection.mainLayout.addWidget(self.controller.file, 1, 2, 1, 4)
        analysisSection.mainLayout.addWidget(self.controller.analyseButton, 2, 3, 1, 2)
        self.menuWidget.add_section(analysisSection)
    
    def addMonitorSection(self):
        monitorSection = MenuSection("Monitoring")
        monitorSection.mainLayout.addWidget(self.controller.createButton, 0, 0, 1, 1)
        monitorSection.mainLayout.addWidget(self.controller.editButton, 1, 0, 1, 1)
        monitorSection.mainLayout.addWidget(self.controller.removeButton, 2, 0, 1, 1)
        self.menuWidget.add_section(monitorSection)
    
    def addViewSection(self):
        viewSection = MenuSection("View")
        analysisButton = QRadioButton("Analysis")
        self.controller.buttonGroup.addButton(analysisButton)
        monitorButton = QRadioButton("Monitor")
        self.controller.buttonGroup.addButton(monitorButton)
        analysisButton.setChecked(True)
        viewSection.mainLayout.addWidget(analysisButton, 0, 0, 1, 2)
        viewSection.mainLayout.addWidget(monitorButton, 1, 0, 1, 2)
        viewSection.mainLayout.addWidget(QWidget(), 2, 5, 1, 1)
        cellWidget = ButtonPad(3, 3, self.menuWidget.height() // 4, self.menuWidget.height() // 4, self.controller.viewMode)
        viewSection.mainLayout.addWidget(cellWidget, 1, 0, 1, 2, Qt.AlignmentFlag.AlignRight)
        self.menuWidget.add_section(viewSection)
    
    def label(self, text):
        res = QLabel(text)
        res.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        res.setMinimumWidth(QApplication.primaryScreen().availableGeometry().width() // 75)
        return res