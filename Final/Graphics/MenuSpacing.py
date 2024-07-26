from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class MenuSpacing(QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.Shape.VLine)
        self.setFrameShadow(QFrame.Shadow.Plain)
        self.setStyleSheet("QFrame {border-width:0 1px 0 0; border-style: solid; border-color: #AAA; margin: 6px 0;}")