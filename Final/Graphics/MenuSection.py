from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class MenuSection(QFrame):
    def __init__(self, name):
        super().__init__()
        self.setFixedWidth(QApplication.primaryScreen().availableGeometry().width() // 5)
        self.mainLayout = QGridLayout(self)
        self.mainLayout.setVerticalSpacing(1)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        
        nameField = QLabel(name)
        nameField.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        nameField.setStyleSheet("color: #777;")
        self.mainLayout.addWidget(nameField, 3, 0, 1, -1)