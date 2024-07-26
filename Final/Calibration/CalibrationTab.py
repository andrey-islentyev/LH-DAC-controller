from AbstractTab import AbstractTab
from Graphics.MenuSection import MenuSection
from .CalibrationController import CalibrationController

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CalibrationTab(AbstractTab):
    def __init__(self):
        super().__init__()
        self.mainLayout.addWidget(self.canvas)
        self.controller = CalibrationController(self.canvas)
        self.addParametersSection()
        self.addActionsSection()
        self.addViewSection()
    
    def addParametersSection(self):
        paramSection = MenuSection("Parameters")
        paramSection.mainLayout.addWidget(self.label("Name:"), 0, 0, 1, 2)
        paramSection.mainLayout.addWidget(self.controller.name, 0, 2, 1, 4)
        paramSection.mainLayout.addWidget(self.label("Temperature:"), 1, 0, 1, 2)
        paramSection.mainLayout.addWidget(self.controller.temp, 1, 2, 1, 4)
        paramSection.mainLayout.addWidget(self.label("L:"), 2, 0, 1, 1)
        paramSection.mainLayout.addWidget(self.controller.L, 2, 1, 1, 2)
        paramSection.mainLayout.addWidget(self.label("R:"), 2, 3, 1, 1)
        paramSection.mainLayout.addWidget(self.controller.R, 2, 4, 1, 2)
        self.menuWidget.add_section(paramSection)
    
    def addActionsSection(self):
        actionSection = MenuSection("Actions")
        actionSection.mainLayout.addWidget(self.controller.openButton, 0, 0, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.editButton, 1, 0, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.removeButton, 2, 0, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.saveButton, 0, 1, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.saveNewButton, 1, 1, 1, 1)
        actionSection.mainLayout.addWidget(self.controller.discardButton, 2, 1, 1, 1)
        self.menuWidget.add_section(actionSection)
    
    def addViewSection(self):
        viewSection = MenuSection("View")
        allButton = QRadioButton("View all")
        self.controller.buttonGroup.addButton(allButton)
        selectButton = QRadioButton("View selected")
        self.controller.buttonGroup.addButton(selectButton)
        lastButton = QRadioButton("View last")
        self.controller.buttonGroup.addButton(lastButton)
        allButton.setChecked(True)
        viewSection.mainLayout.addWidget(allButton, 0, 0, 1, 2)
        viewSection.mainLayout.addWidget(selectButton, 1, 0, 1, 2)
        viewSection.mainLayout.addWidget(lastButton, 2, 0, 1, 2)
        viewSection.mainLayout.addWidget(self.controller.scrollArea, 0, 2, 3, -1)
        self.menuWidget.add_section(viewSection)
    
    def label(self, text):
        res = QLabel(text)
        res.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        res.setMinimumWidth(QApplication.primaryScreen().availableGeometry().width() // 75)
        return res