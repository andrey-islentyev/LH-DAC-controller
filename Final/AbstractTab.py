from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from Graphics.MenuWidget import MenuWidget
from GlobalData import GlobalData

class AbstractTab(QWidget):
    def __init__(self):
        super().__init__()
        self.isCurrentTab = False
        self.mainLayout = QVBoxLayout(self)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.menuWidget = MenuWidget()
        self.mainLayout.addWidget(self.menuWidget)
        
        self.canvas = FigureCanvas(Figure())
