from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from .MenuSpacing import MenuSpacing

class MenuWidget(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(QApplication.primaryScreen().availableGeometry().height() // 10)
        self.setObjectName("main")
        self.setStyleSheet("""
            QFrame#main {border-style: solid; border-width: 0px 0px 2px 0px; border-color: #AAA;}
            QFrame#main > QFrame {margin-top: 3px; margin-left: 2px;}""")
        
        self.mainLayout = QHBoxLayout(self)
        self.mainLayout.setContentsMargins(0, 0, 0, 0) 
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(QWidget())
        
    def add_section(self, section):
        item = self.mainLayout.itemAt(self.mainLayout.count() - 1)
        self.mainLayout.removeItem(item)
        item.widget().deleteLater()
        self.mainLayout.addWidget(section, Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addWidget(MenuSpacing(), Qt.AlignmentFlag.AlignLeft)
        self.mainLayout.addWidget(QWidget())