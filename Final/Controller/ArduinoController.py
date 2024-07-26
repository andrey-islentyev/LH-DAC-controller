from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import serial.tools.list_ports

from GlobalData import GlobalData
from Calibration.CalibrationDialog import CalibrationDialog
from .ArduinoData import ArduinoData
import time

class ArduinoController:
    def __init__(self, canvas):
        GlobalData.openTabs.append(self)
        
        self.curDisplay = -1
        self.canvas = canvas
        self.canvasLayout = QGridLayout(self.canvas)
        self.canvasLayout.setContentsMargins(5, 5, 5, 5)
        self.canvasLayout.setSpacing(1)
        self.canvasLayout.addWidget(self.label("Name:"), 0, 0, 1, 1)
        self.nameEdit = self.line_edit()
        self.nameEdit.textEdited.connect(self.name_edited)
        self.canvasLayout.addWidget(self.nameEdit, 0, 1, 1, 2)
        self.canvasLayout.addWidget(self.label("Status:"), 1, 0, 1, 1)
        self.statusEdit = self.line_edit()
        self.statusEdit.setReadOnly(True)
        self.canvasLayout.addWidget(self.statusEdit, 1, 1, 1, 2)
        self.canvasLayout.addWidget(self.label("Target Temperature:"), 2, 0, 1, 1)
        self.tempEdit = self.line_edit()
        valueValidator = QIntValidator()
        valueValidator.setBottom(0)
        self.tempEdit.setValidator(valueValidator)
        self.tempEdit.textEdited.connect(self.temp_edited)
        self.canvasLayout.addWidget(self.tempEdit, 2, 1, 1, 2)
        codeLabel = self.label("Code:")
        codeLabel.setSizePolicy( QSizePolicy.Policy.Minimum,  QSizePolicy.Policy.Fixed)
        codeLabel.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.canvasLayout.addWidget(codeLabel, 3, 0, 1, 1)
        self.codeEdit = QTextEdit()
        self.codeEdit.setTabStopDistance(QFontMetricsF(self.tempEdit.font()).horizontalAdvance(' ') * 4)
        self.codeEdit.setStyleSheet("QTextEdit{border: 2px solid #AAA}")
        self.codeEdit.textChanged.connect(self.code_edited)
        self.canvasLayout.addWidget(self.codeEdit, 4, 0, 1, -1)
        self.testButton = QPushButton("Test")
        self.testButton.setEnabled(False)
        self.testButton.pressed.connect(self.test_arduino)
        self.stopButton = QPushButton("Stop")
        self.stopButton.setEnabled(False)
        self.stopButton.pressed.connect(self.stop_arduino)
        self.canvasLayout.addWidget(self.testButton, 5, 1, 1, 1)
        self.canvasLayout.addWidget(self.stopButton, 5, 2, 1, 1)
        
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonToggled.connect(self.change_arduino)
        self.arduinoArr = []
        self.arduinoHolderList = []
        self.buttonList = []
        self.labelList = []
        self.statusList = []
        self.viewList = []
        self.readyCnt = 0
        self.runningCnt = 0
        self.listEntryHeight = QApplication.primaryScreen().availableGeometry().height() // 60

        
        self.addButton = QPushButton("Create")
        self.connectButton = QPushButton("Connect")
        self.removeButton = QPushButton("Remove")
        
        self.verify_buttons()
        
        self.listWidget = QWidget()
        self.listWidget.setFixedWidth(QApplication.primaryScreen().availableGeometry().width() // 5)
        self.listLayout = QVBoxLayout(self.listWidget) 
        self.listLayout.setContentsMargins(5, 2, 5, 0)
        self.listLayout.setSpacing(1)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.listWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setBackgroundRole(QPalette.ColorRole.Light)
        
        self.refreshTimer = QTimer()
        self.refreshTimer.timeout.connect(self.check_arduinos)
        self.refreshTimer.start(50)
        
        self.addButton.pressed.connect(self.add_arduino)
        self.connectButton.pressed.connect(self.connect_arduino)
        self.removeButton.pressed.connect(self.remove_arduino)
    
    def test_arduino(self):
        with self.arduinoArr[self.curDisplay].statusLock:
            self.arduinoArr[self.curDisplay].status = "Testing"
        self.arduinoArr[self.curDisplay].test()
    
    def stop_arduino(self):
        with self.arduinoArr[self.curDisplay].statusLock:
            self.arduinoArr[self.curDisplay].status = "Error: user interrupt"
            
    def name_edited(self):
        with self.arduinoArr[self.curDisplay].statusLock:
            self.labelList[self.curDisplay].setText(self.nameEdit.text())
            self.arduinoArr[self.curDisplay].name = self.nameEdit.text()
    
    def code_edited(self):
        if self.curDisplay == -1: return
        with self.arduinoArr[self.curDisplay].statusLock:
            self.arduinoArr[self.curDisplay].code = self.codeEdit.toPlainText()
            
    def temp_edited(self):
        with self.arduinoArr[self.curDisplay].statusLock:
            self.arduinoArr[self.curDisplay].target = int(self.tempEdit.text())
            
    def check_arduinos(self):
        readyCnt, runningCnt = 0, 0
        if self.curDisplay == -1:
            self.nameEdit.setEnabled(False)
            self.nameEdit.setText("")
            self.statusEdit.setEnabled(False)
            self.statusEdit.setText("")
            self.tempEdit.setEnabled(False)
            self.tempEdit.setText("")
            self.testButton.setEnabled(False)
            self.stopButton.setEnabled(False)
            if self.codeEdit.isEnabled():
                self.codeEdit.setEnabled(False)
                self.codeEdit.setText("")
            
        for i, arduino in enumerate(self.arduinoArr):
            with arduino.statusLock:
                if i == self.curDisplay:
                    self.nameEdit.setEnabled(arduino.status != "Running" and arduino.status != "Testing")
                    self.tempEdit.setEnabled(arduino.status != "Running" and arduino.status != "Testing")
                    self.codeEdit.setEnabled(arduino.status != "Running" and arduino.status != "Testing")
                    self.testButton.setEnabled("Error" in arduino.status or arduino.status == "Empty" or arduino.status == "Success")
                    self.stopButton.setEnabled(arduino.status == "Running")
                    if not self.statusEdit.isEnabled(): self.statusEdit.setEnabled(True)
                    if arduino.status != self.statusEdit.text():
                        self.statusEdit.setText(arduino.status)
                color = "grey"
                if "Error" in arduino.status: color = "red"
                elif arduino.status == "Testing":
                    color = "yellow"
                    runningCnt += 1
                elif arduino.status == "Success":
                    color = "blue"
                    readyCnt += 1
                elif arduino.status == "Running":
                    color = "green"
                    runningCnt += 1
                self.statusList[i].setText(arduino.status)
                self.viewList[i].setStyleSheet(f"""QFrame{{background-color: {color}; border-radius: 5px; border: 1px solid #AAA;}}""")
        if readyCnt != self.readyCnt or runningCnt != self.runningCnt:
            self.readyCnt = readyCnt
            self.runningCnt = runningCnt
            self.verify_buttons()
            
    def add_arduino_item(self, arduino): 
        container = QWidget()
        container.setFixedHeight(self.listEntryHeight)
        self.arduinoHolderList.append(container)
        containerLayout = QHBoxLayout(container)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(1)
        
        self.buttonList.append(QRadioButton())
        self.buttonGroup.addButton(self.buttonList[-1])
        self.buttonList[-1].setFixedHeight(3*self.listEntryHeight//4)
        self.buttonList[-1].setFixedWidth(3*self.listEntryHeight//4)
        self.buttonList[-1].setStyleSheet(f"""
            QRadioButton::indicator{{width: {3*self.listEntryHeight//4 - 2}px;
            height: {3*self.listEntryHeight//4 - 2}px;}}""")
        containerLayout.addWidget(self.buttonList[-1])
        
        self.labelList.append(QLabel(arduino.name))
        self.labelList[-1].setFixedHeight(self.listEntryHeight)
        containerLayout.addWidget(self.labelList[-1])
        
        self.statusList.append(QLabel("Empty"))
        self.statusList[-1].setFixedHeight(self.listEntryHeight)
        containerLayout.addWidget(self.statusList[-1])

        self.viewList.append(QFrame())
        self.viewList[-1].setFixedHeight(2 * self.listEntryHeight // 3)
        self.viewList[-1].setFixedWidth(2 * self.listEntryHeight // 3)
        containerLayout.addWidget(self.viewList[-1])
        
        self.listWidget.layout().addWidget(container)
        self.arduinoArr.append(arduino)
        if len(self.buttonList) == 1:
            self.curDisplay = 0
            self.buttonList[-1].setChecked(True)
        self.check_arduinos()
    
    def change_arduino(self, button, checked):
        if checked:
            for i, btn in enumerate(self.buttonList):
                if btn == button:
                    self.curDisplay = i
                    with self.arduinoArr[i].statusLock:
                        self.statusEdit.setText(self.arduinoArr[i].status)
                        self.nameEdit.setText(self.arduinoArr[i].name)
                        self.tempEdit.setText(str(self.arduinoArr[i].target))
                    self.codeEdit.setText(self.arduinoArr[i].code)
                    self.check_arduinos()
    
    def add_arduino(self):
        arr = [str(i) for i in serial.tools.list_ports.comports()]
        dlg = CalibrationDialog("Select port", arr, self.addButton)
        value =  dlg.exec() - 1
        if value == -1: return
        portVar = arr[value].split()[0]
        baudrate = 9600
        try:
            curArduino = ArduinoData(portVar, baudrate, 0.05)
            self.add_arduino_item(curArduino)
        except:
            print("Error connecting Arduino")
        self.resize_list_widget()

    def remove_arduino(self):
        option = []
        position = {}
        for i, arduino in enumerate(self.arduinoArr):
            with arduino.statusLock:
                if arduino.status != "Running" and arduino.status != "Testing":
                    option.append(arduino.name)
                    position[len(position)] = i
        dlg = CalibrationDialog("Remove Arduino", option, self.removeButton)
        value = dlg.exec() - 1
        if value == -1: return
        index = position[value]
        if index < self.curDisplay: self.curDisplay -= 1
        if index == self.curDisplay:
            if len(self.arduinoArr) == 1: self.curDisplay = -1
            else: self.curDisplay = 0
        self.arduinoArr.pop(index)
        
        container = self.arduinoHolderList[index]
        self.listWidget.layout().removeWidget(container)
        self.arduinoHolderList.pop(index)
        
        container.layout().removeWidget(self.buttonList[index])
        self.buttonList[index].deleteLater()
        self.buttonList.pop(index)
        
        container.layout().removeWidget(self.labelList[index])
        self.labelList[index].deleteLater()
        self.labelList.pop(index)
        
        container.layout().removeWidget(self.statusList[index])
        self.statusList[index].deleteLater()
        self.statusList.pop(index)

        container.layout().removeWidget(self.viewList[index])
        self.viewList[index].deleteLater()
        self.viewList.pop(index)
        
        container.deleteLater()
        self.resize_list_widget()
        self.check_arduinos()
        self.verify_buttons()
        
    def connect_arduino(self):
        option = []
        position = {}
        for i, arduino in enumerate(self.arduinoArr):
            with arduino.statusLock:
                if arduino.status == "Success":
                    option.append(arduino.name)
                    position[len(position)] = i
        dlg = CalibrationDialog("Select Arduino", option, self.addButton)
        value = dlg.exec() - 1
        if value == -1: return
        arduino = self.arduinoArr[position[value]]
        option = []
        position = {}
        for i, monitor in enumerate(GlobalData.globalMonitors):
            if monitor != None:
                with monitor.statusLock:
                    if not monitor.running:
                        option.append(monitor.name)
                        position[len(position)] = i
        dlg = CalibrationDialog("Select Monitor", option, self.addButton)
        value = dlg.exec() - 1
        if value == -1: return
        monitor = GlobalData.globalMonitors[position[value]]
        with monitor.dataLock:
            if monitor.arduino != None:
                with monitor.arduino.statusLock:
                    if monitor.arduino.status == "Running" or monitor.arduino.status == "Error: user interrupt":
                        monitor.arduino.status = "Success"
            monitor.arduino = arduino
            monitor.hasArduino = True
        with arduino.statusLock:
            arduino.status = "Running"
        self.verify_buttons()
        self.check_arduinos()
    
    def resize_list_widget(self):
        count = len(self.arduinoArr)
        self.listWidget.setFixedHeight(2 + (1 + self.listEntryHeight) * count)
        self.listWidget.adjustSize()
        
    def verify_buttons(self):
        self.removeButton.setEnabled(len(self.arduinoArr) - self.runningCnt > 0)
        cnt = 0
        for i in GlobalData.globalMonitors:
            if i != None: cnt += 1
        self.connectButton.setEnabled(self.readyCnt > 0 and cnt > 0)  
               
    def line_edit(self):
        res = QLineEdit()
        res.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        return res
    
    def label(self, text):
        res = QLabel(text)
        res.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
        res.setMinimumWidth(QApplication.primaryScreen().availableGeometry().width() // 75)
        return res