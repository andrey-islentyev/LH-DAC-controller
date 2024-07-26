from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import numpy as np

from .CalibrationData import CalibrationData
from .CalibrationDialog import CalibrationDialog
from .CalibrationSlider import CalibrationSlider

from GlobalData import GlobalData

class CalibrationController:
    def __init__(self, canvas):
        GlobalData.openTabs.append(self)
        self.calibrationData = []
        self.checkBoxArr = []
        self.savePosition = 0
        self.hasNew = False
        self.mode = 0
        
        self.canvas = canvas
        
        self.listEntryHeight = QApplication.primaryScreen().availableGeometry().height() // 70
        
        self.temp = self.line_edit()
        tempValidator = QDoubleValidator()
        tempValidator.setBottom(0)
        self.temp.setValidator(tempValidator)
        self.temp.editingFinished.connect(self.temperature_changed)
        self.name = self.line_edit()
        self.name.textEdited.connect(self.name_changed)
        markerValidator = QDoubleValidator()
        self.L = self.line_edit()
        self.L.setValidator(markerValidator)
        self.R = self.line_edit()
        self.R.setValidator(markerValidator)
        self.calibrationSlider = CalibrationSlider(self)
        
        self.openButton = QPushButton("Open")
        self.openButton.pressed.connect(self.load_calibration)
        self.editButton = QPushButton("Edit")
        self.editButton.pressed.connect(self.edit_calibration)
        self.removeButton = QPushButton("Remove")
        self.removeButton.pressed.connect(self.remove_calibration)
        self.saveButton = QPushButton("Save")
        self.saveButton.pressed.connect(self.save_calibration)
        self.discardButton = QPushButton("Discard")
        self.discardButton.pressed.connect(self.discard_calibration)
        self.saveNewButton = QPushButton("Save as new")
        self.saveNewButton.pressed.connect(self.save_new_calibration)
        self.verify_buttons()
        
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonToggled.connect(self.change_mode)
        self.listWidget = QWidget()
        self.listWidget.setFixedWidth(QApplication.primaryScreen().availableGeometry().width() // 5)
        self.listLayout = QVBoxLayout(self.listWidget) 
        self.listLayout.setContentsMargins(5, 2, 0, 0)
        self.listLayout.setSpacing(1)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.listWidget)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setBackgroundRole(QPalette.ColorRole.Light)
    
    def line_edit(self):
        res = QLineEdit()
        res.setEnabled(False)
        res.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        return res
    
    def temperature_changed(self):
        self.calibrationData[-1].temp = float(self.temp.text())
        self.calibrationData[-1].calculate_T()
        self.paint_canvas()
    
    def name_changed(self):
        self.calibrationData[-1].name = self.name.text()
        self.checkBoxArr[-1].setText(self.name.text())
        self.paint_canvas()
        
    def change_mode(self, button, checked):
        if checked: 
            self.mode = {"View all": 0, "View selected": 1, "View last": 2}[button.text()]
            self.paint_canvas()
            
    def resize_list_widget(self):
        count = len(self.calibrationData)
        self.listWidget.setFixedHeight(2 + (1 + self.listEntryHeight) * count)
        self.listWidget.adjustSize()
        
    def set_edit_data(self, curData):
        if self.hasNew: self.calibrationData[-1] = curData
        else:
            self.hasNew = True
            self.calibrationData.append(curData)
            self.checkBoxArr.append(QCheckBox())
            self.checkBoxArr[-1].checkStateChanged.connect(self.paint_canvas)
            self.checkBoxArr[-1].setFixedHeight(self.listEntryHeight)
            self.checkBoxArr[-1].setStyleSheet("color: red;")
            self.checkBoxArr[-1].setChecked(True)
            self.listLayout.addWidget(self.checkBoxArr[-1])
            self.resize_list_widget()
        self.name.setText(curData.name)
        self.L.setText("{0:.2f}".format(round(curData.L, 2)))
        self.L.validator().setBottom(curData.l[0])
        self.L.validator().setTop(curData.l[-1])
        self.R.setText("{0:.2f}".format(round(curData.R, 2)))
        self.R.validator().setBottom(curData.l[0])
        self.R.validator().setTop(curData.l[-1])
        self.calibrationSlider.posL = curData.L
        self.calibrationSlider.posR = curData.R
        self.temp.setText(str(curData.temp))
        self.checkBoxArr[-1].setText(curData.name)
        self.verify_buttons()
        self.paint_canvas()
        
    def load_calibration(self):
        path = QFileDialog.getOpenFileName()
        if path != ('', ''):
            try:
                data = np.loadtxt(path[0])
                curData = CalibrationData()
                curData.set_data(data)
                curData.calculate_T()
                self.savePosition = len(self.calibrationData) - 1 if self.hasNew else len(self.calibrationData)
                curData.name = "Calibration" + str(self.savePosition)
                self.set_edit_data(curData)
            except:
                print("Could not parse file " + path[0])

    def select_calibration(self, name):
        if self.hasNew: dlg = CalibrationDialog(name, [i.text() for i in self.checkBoxArr[:-1]], self.openButton)
        else: dlg = CalibrationDialog(name, [i.text() for i in self.checkBoxArr], self.openButton)
        return dlg.exec() - 1
    
    def edit_calibration(self):
        position = self.select_calibration("Edit")
        if position == -1: return
        self.set_edit_data(self.calibrationData[position].copy())
        self.savePosition = position
        self.verify_buttons()
        self.paint_canvas()
    
    def remove_calibration(self):
        position = self.select_calibration("Remove")
        if position == -1: return
        if position == self.savePosition: self.savePosition = len(self.calibrationData) - 1
        if position < self.savePosition: self.savePosition -= 1
        self.calibrationData.pop(position)
        self.listLayout.removeWidget(self.checkBoxArr[position])
        self.checkBoxArr[position].deleteLater()
        self.checkBoxArr.pop(position)
        self.resize_list_widget()
        self.store_calibrations()
        self.verify_buttons()
        self.paint_canvas()
    
    def store_calibrations(self):
        GlobalData.globalCalibrations = []
        for calib in self.calibrationData:
            GlobalData.globalCalibrations.append(calib.copy())
        GlobalData.notify_all()
            
    def save_calibration(self):
        if self.savePosition + 1 == len(self.calibrationData):
            self.checkBoxArr[-1].setStyleSheet("color: black;")
        else:
            self.checkBoxArr[self.savePosition].setText(self.checkBoxArr[-1].text())
            self.calibrationData[self.savePosition] = self.calibrationData[-1].copy()
            self.calibrationData.pop()
            self.listLayout.removeWidget(self.checkBoxArr[-1])
            self.checkBoxArr[-1].deleteLater()
            self.checkBoxArr.pop()
            self.resize_list_widget()
        self.store_calibrations()
        self.hasNew = False
        self.paint_canvas()
        self.verify_buttons()
    
    def discard_calibration(self):
        self.checkBoxArr[self.savePosition].setText(self.checkBoxArr[-1].text())
        self.calibrationData[self.savePosition] = self.calibrationData[-1].copy()
        self.calibrationData.pop()
        self.listLayout.removeWidget(self.checkBoxArr[-1])
        self.checkBoxArr[-1].deleteLater()
        self.checkBoxArr.pop()
        self.resize_list_widget()
        self.hasNew = False
        self.paint_canvas()
        self.verify_buttons()
        
    def save_new_calibration(self):
        self.savePosition = len(self.calibrationData) - 1
        self.save_calibration()
        
    def verify_buttons(self):
        self.editButton.setEnabled(not(len(self.calibrationData) == 0 or (len(self.calibrationData) == 1 and self.hasNew)))
        self.removeButton.setEnabled(not(len(self.calibrationData) == 0 or (len(self.calibrationData) == 1 and self.hasNew)))
        self.saveButton.setEnabled(self.hasNew)
        self.discardButton.setEnabled(self.hasNew)
        self.saveNewButton.setEnabled(self.hasNew and self.savePosition + 1 != len(self.calibrationData))
        self.temp.setEnabled(self.hasNew)
        self.name.setEnabled(self.hasNew)
        self.L.setEnabled(self.hasNew)
        self.R.setEnabled(self.hasNew)
        if not self.hasNew:
            self.temp.setText("")
            self.name.setText("")
            self.L.setText("")
            self.R.setText("")
    
    def show_text(self, axis, text):
        axis.set_axis_off()
        axis.text((axis.get_xlim()[0] + axis.get_xlim()[1]) / 2, 
                         (axis.get_ylim()[0] + axis.get_ylim()[1]) / 2,
                         text, horizontalalignment='center', verticalalignment='center')
        
    def paint_canvas(self):
        colors = ["black", "tab:blue", "tab:orange", "tab:green", "tab:purple",
                  "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
        drawList = []
        if self.mode == 0: drawList = list(range(len(self.calibrationData)))
        elif self.mode == 2 and len(self.calibrationData) > 0: drawList = [len(self.calibrationData) - 1]
        else:
            for i, btn in enumerate(self.checkBoxArr):
                if btn.isChecked(): drawList.append(i)
        self.canvas.figure.clear()
        self.figure = self.canvas.figure.subplots()
        self.figure.set_position([1/8, 1/9, 6/8, 7/9])
        self.figure.set_ylim([0, 1.01])
        for i in drawList:
            curColor = colors[i % len(colors)]
            if self.hasNew and i == len(self.calibrationData) - 1: curColor = "tab:red"
            arrl = []
            for l in self.calibrationData[i].l:
                if self.calibrationData[i].L < l and self.calibrationData[i].R > l:
                    arrl.append(l)
            self.figure.plot(self.calibrationData[i].l, self.calibrationData[i].I, color = curColor, lw = 1, label = self.calibrationData[i].name)
            self.figure.plot(arrl, self.calibrationData[i].T, color = curColor, lw = 1, ls = "--")
        if len(drawList) > 0:
            self.figure.legend(loc="upper left")
        else: self.show_text(self.figure, "No calibration objects selected")
        self.canvas.draw()