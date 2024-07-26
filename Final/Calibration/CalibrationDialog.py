from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CalibrationDialog(QDialog):
    def __init__(self, name, names, parent=None):
        super().__init__(parent)

        self.setWindowTitle(name)

        QBtn = QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Cancel
        self.listEntryHeight = QApplication.primaryScreen().availableGeometry().height() // 70

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.mainLayout = QVBoxLayout(self)
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonToggled.connect(self.change_result)
        self.buttonArr = []
        self.result = 0
        self.listWidget = QWidget()
        self.listWidget.setFixedHeight(2 + (1 + self.listEntryHeight) * len(names))
        self.listWidget.setFixedWidth(self.width())
        self.listWidget.adjustSize()
        self.listLayout = QVBoxLayout(self.listWidget) 
        self.listLayout.setContentsMargins(5, 2, 0, 0)
        self.listLayout.setSpacing(1)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.listWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setBackgroundRole(QPalette.ColorRole.Light)
        self.scrollArea.setStyleSheet("QScrollBar:vertical { width: 17px; }")
        self.scrollArea.resizeEvent = self.resize_area
        self.hasScrollBar = False
        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.scroll_bar_appear)
        for btn in names:
            self.buttonArr.append(QRadioButton(btn))
            self.buttonArr[-1].setFixedHeight(self.listEntryHeight)
            self.buttonGroup.addButton(self.buttonArr[-1])
            self.listLayout.addWidget(self.buttonArr[-1])
        self.mainLayout.addWidget(self.scrollArea)
        self.mainLayout.addWidget(self.buttonBox)
    
    def resize_area(self, event):
        QScrollArea.resizeEvent(self.scrollArea, event)
        if not self.hasScrollBar:
            self.listWidget.setFixedWidth(self.scrollArea.width())
        else:
            self.listWidget.setFixedWidth(self.scrollArea.width() - 17)
        
    def scroll_bar_appear(self, mn, mx):
        if mx != 0:
            self.hasScrollBar = True
        else: self.hasScrollBar = False
        self.resize_list_widget()
        
    def change_result(self, button, checked):
        if checked: 
            for i, btn in enumerate(self.buttonArr):
                if btn == button:
                    self.result = i + 1
                    
    def resize_list_widget(self):
        count = len(self.buttonArr)
        self.listWidget.setFixedHeight(2 + (1 + self.listEntryHeight) * count)
        self.listWidget.adjustSize()
        
    def reject(self):
        super().done(0)
        
    def accept(self):
        if self.result != 0: super().done(self.result)