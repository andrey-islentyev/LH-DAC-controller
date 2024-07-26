from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class ButtonPad(QWidget):
    
    def __init__(self, a, b, width, height, buttonGroup):
        super().__init__()
        self.style = {"selected": """border-style: inset; border-width: 1px; border-radius: 2px;
            border-color: #69a; background-color: #7bf""", "selecting": """border-style: inset;
            border-width: 1px; border-radius: 2px; border-color: #8895AA; background-color: #ACE""",
            "unselected": """border-style: outset; border-width: 1px; border-radius: 2px;
            border-color: #AAA; background-color: #DDD""", "unselecting": """border-style: outset;
            border-width: 1px; border-radius: 2px; border-color: #8895AA; background-color: #ACE"""}
        self.a, self.b = a, b
        self.cura, self.curb = 1, 1
        self.setFixedWidth(width)
        self.setFixedHeight(height)
        cellLayout = QGridLayout(self)
        self.buttonGroup = buttonGroup
        cellLayout.setContentsMargins(0, 0, 0, 0)
        cellLayout.setSpacing(0)
        self.buttonGroup.buttonClicked.connect(self.click)
        self.buttonArr = []
        for i in range(self.a):
            self.buttonArr.append([])
            for j in range(self.b):
                curButton = QPushButton()
                curButton.setProperty("distX", i)
                curButton.setProperty("distY", j)
                curButton.setFixedHeight(self.height() // self.a)
                curButton.setFixedWidth(self.width() // self.b)
                curButton.setStyleSheet(self.style["unselected"])
                self.buttonArr[-1].append(curButton)
                curButton.enterEvent = self.get_event_handler(i, j)
                cellLayout.addWidget(curButton, i, j, 1, 1)
                self.buttonGroup.addButton(curButton)
        self.leaveEvent = lambda e: self.paint_selection(self.cura, self.curb)
        self.click(self.buttonArr[0][0])

    def get_event_handler(self, i, j):
        return lambda e: self.paint_selection(i, j)
    
    def paint_selection(self, x, y):
        for i in range(self.a):
            for j in range(self.b):
                if i > x or j > y:
                    if self.buttonArr[i][j].property("active"):
                        self.buttonArr[i][j].setStyleSheet(self.style["unselecting"])
                    else:
                        self.buttonArr[i][j].setStyleSheet(self.style["unselected"])
                else: 
                    if self.buttonArr[i][j].property("active"):
                        self.buttonArr[i][j].setStyleSheet(self.style["selected"])
                    else:
                        self.buttonArr[i][j].setStyleSheet(self.style["selecting"])
        
    def click(self, button):
        self.cura = button.property("distX")
        self.curb = button.property("distY")
        for i in range(self.a):
            for j in range(self.b):
                if i > button.property("distX") or j > button.property("distY"):
                    self.buttonArr[i][j].setProperty("active", False)
                    self.buttonArr[i][j].setStyleSheet(self.style["unselected"])
                else: 
                    self.buttonArr[i][j].setProperty("active", True)
                    self.buttonArr[i][j].setStyleSheet(self.style["selected"])