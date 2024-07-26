from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from Calibration.CalibrationDialog import CalibrationDialog
from GlobalData import GlobalData
import random

class MonitoringDialog(QDialog):
    def __init__(self, name, monitor, options, parent=None):
        super().__init__(parent)

        self.inf = 1e300
        
        self.setWindowTitle(name)
        self.monitor = monitor
        self.listEntryHeight = QApplication.primaryScreen().availableGeometry().height() // 60

        self.buttonBox = QDialogButtonBox(Qt.Orientation.Horizontal)
        self.buttonSave = self.buttonBox.addButton("Save", QDialogButtonBox.ButtonRole.NoRole)
        self.buttonSave.setAutoDefault(False)
        self.buttonSave.pressed.connect(self.accept)
        self.buttonSaveNew = None
        if options == 2:
            self.buttonSaveNew = self.buttonBox.addButton("Save as new", QDialogButtonBox.ButtonRole.NoRole)
            self.buttonSaveNew.pressed.connect(self.save_as_new)
            self.buttonSaveNew.setAutoDefault(False)
        self.buttonCancel = self.buttonBox.addButton("Cancel", QDialogButtonBox.ButtonRole.NoRole)
        self.buttonCancel.setAutoDefault(False)
        self.buttonCancel.pressed.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.mainLayout = QGridLayout(self)
        valueValidator = QIntValidator()
        valueValidator.setBottom(0)
        self.editName = self.line_edit()
        self.editName.setText(monitor.name)
        self.editName.textEdited.connect(self.change_name)
        self.editL = self.line_edit()
        self.editL.setText(str(monitor.L))
        self.editL.setValidator(valueValidator)
        self.editL.textEdited.connect(self.changeL)
        self.editR = self.line_edit()
        self.editR.setText(str(monitor.R))
        self.editR.textEdited.connect(self.changeR)
        self.editR.setValidator(valueValidator)
        self.folderButton = QPushButton("Folder")
        self.folderButton.setAutoDefault(False)
        self.folderButton.pressed.connect(self.select_folder)
        self.hasFolder = False
        if monitor.folder != "":
            self.hasFolder = True
        self.folderEdit = self.line_edit()
        self.folderEdit.setReadOnly(True)
        self.folderEdit.setText(self.monitor.folder)
        self.editRegex = self.line_edit()
        self.editRegex.textEdited.connect(self.change_regex)
        self.regexCheckbox = QCheckBox("Use RegEx")
        if monitor.regex != None:
            self.regexCheckbox.setChecked(True)
            self.editRegex.setText(monitor.regex)
        self.regexCheckbox.checkStateChanged.connect(self.use_regex)
        self.mainLayout.addWidget(self.label("Name"), 0, 0, 1, 2)
        self.mainLayout.addWidget(self.editName, 0, 2, 1, 4)
        self.mainLayout.addWidget(self.folderButton, 1, 0, 1, 2)
        self.mainLayout.addWidget(self.folderEdit, 1, 2, 1, 4)
        self.mainLayout.addWidget(self.label("Intensity L"), 2, 0, 1, 2)
        self.mainLayout.addWidget(self.editL, 2, 2, 1, 1)
        self.mainLayout.addWidget(self.label("Intensity R"), 2, 3, 1, 2)
        self.mainLayout.addWidget(self.editR, 2, 5, 1, 1)
        self.mainLayout.addWidget(self.label("RegEx"), 3, 0, 1, 2)
        self.mainLayout.addWidget(self.editRegex, 3, 2, 1, 3)
        self.mainLayout.addWidget(self.regexCheckbox, 3, 5, 1, 2)
        
        self.calibList = QWidget()
        self.listLayout = QGridLayout(self.calibList) 
        self.listLayout.setContentsMargins(1, 2, 2, 2)
        self.listLayout.setVerticalSpacing(1)
        self.listLayout.setHorizontalSpacing(3)
        self.scrollArea = QScrollArea()
        self.scrollArea.setStyleSheet("QScrollBar:vertical { width: 17px; }")
        self.scrollArea.resizeEvent = self.resize_area
        self.hasScrollBar = False
        self.scrollArea.verticalScrollBar().rangeChanged.connect(self.scroll_bar_appear)
        self.scrollArea.setWidget(self.calibList)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setBackgroundRole(QPalette.ColorRole.Light)
        self.mainLayout.addWidget(self.scrollArea, 4, 0, 5, -1)
        self.properTemps = True
        self.tempEditsL = []
        self.tempEditsR = []
        self.tempEditL = self.line_edit()
        self.tempEditL.setText("0")
        self.tempEditL.setReadOnly(True)
        self.tempEditR = self.line_edit()
        self.tempEditR.setText("∞")
        self.tempEditR.setReadOnly(True)
               
        self.addCalibButton = QPushButton("Add Calibration")
        self.addCalibButton.setAutoDefault(False)
        self.addCalibButton.setEnabled(len(GlobalData.globalCalibrations) > 0)
        self.addCalibButton.pressed.connect(self.add_calibration)
        self.mainLayout.addWidget(self.addCalibButton, 9, 4, 1, -1)
        self.mainLayout.addWidget(self.buttonBox, 10, 0, -1, -1)
        
        self.verify_buttons()
        self.display_calibrations()
        self.resize_list_widget()
    
    def verify_buttons(self):
        canSave = self.hasFolder and self.monitor.L <= self.monitor.R and len(self.monitor.calibrations) > 0 and self.properTemps
        self.buttonSave.setEnabled(canSave)
        if self.buttonSaveNew:
            self.buttonSaveNew.setEnabled(canSave) 
            
    def select_folder(self):
        path = QFileDialog.getExistingDirectory()
        if path:
            self.hasFolder = True
            self.monitor.folder = path
            self.folderEdit.setText(path)
            self.verify_buttons()
            
    def resize_area(self, event):
        QScrollArea.resizeEvent(self.scrollArea, event)
        if not self.hasScrollBar:
            self.calibList.setFixedWidth(self.scrollArea.width())
        else:
            self.calibList.setFixedWidth(self.scrollArea.width() - 17)
        
    def scroll_bar_appear(self, mn, mx):
        if mx != 0:
            self.hasScrollBar = True
        else: self.hasScrollBar = False
        self.resize_list_widget()
        
    def select_calibration(self, name):
        dlg = CalibrationDialog(name, [i.name for i in GlobalData.globalCalibrations], self.addCalibButton)
        return dlg.exec() - 1
    
    def resize_list_widget(self):
        count = len(self.monitor.calibrations)
        self.calibList.setFixedHeight(2 + (1 + self.listEntryHeight) * count)
        self.calibList.adjustSize()
    
    def check_temps(self):
        self.properTemps = True
        if len(self.tempEditsL) > 1:
            for i in range(len(self.tempEditsL) - 1):
                if int(self.tempEditsL[i].text()) > int(self.tempEditsR[i + 1].text()):
                    self.tempEditsL[i].setStyleSheet("background-color:#FFCCCB")
                    self.tempEditsR[i + 1].setStyleSheet("background-color:#FFCCCB")
                    self.properTemps = False
                    
    def text_changed_L(self):
        self.monitor.calibSplit.clear()
        for i in range(len(self.tempEditsL)):
            self.tempEditsR[i].setText(self.tempEditsL[i].text())
            self.tempEditsL[i].setStyleSheet("background-color:#FFF")
            self.tempEditsR[i].setStyleSheet("background-color:#FFF")
            self.monitor.calibSplit.append(int(self.tempEditsL[i].text()))
        self.check_temps()
        self.verify_buttons()
    
    def text_changed_R(self):
        self.monitor.calibSplit.clear()
        for i in range(len(self.tempEditsR)):
            self.tempEditsL[i].setText(self.tempEditsR[i].text())
            self.tempEditsL[i].setStyleSheet("background-color:#FFF")
            self.tempEditsR[i].setStyleSheet("background-color:#FFF")
            self.monitor.calibSplit.append(int(self.tempEditsR[i].text()))
        self.check_temps()
        self.verify_buttons()
    
    def use_regex(self, state):
        if state == Qt.CheckState.Checked:
            self.monitor.regex = self.editRegex.text()
        else: self.monitor.regex = None
        
    def display_calibrations(self):
        while self.listLayout.count() > 0:
            widget = self.listLayout.itemAt(0).widget()
            self.listLayout.removeWidget(widget)
            widget.setParent(None)
        self.tempEditsL.clear()
        self.tempEditsR.clear()
        
        for i, calib in enumerate(self.monitor.calibrations):
            if i == 0:
                self.listLayout.addWidget(self.tempEditL, i, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
            else: 
                self.tempEditsL.append(self.line_edit())
                self.tempEditsL[-1].setText(str(self.monitor.calibSplit[i - 1]))
                valueValidator = QIntValidator()
                valueValidator.setBottom(0)
                self.tempEditsL[-1].setValidator(valueValidator)
                self.tempEditsL[-1].editingFinished.connect(self.text_changed_L)
                self.listLayout.addWidget(self.tempEditsL[-1], i, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
            self.listLayout.addWidget(self.label(calib.name), i, 1, 1, 3, Qt.AlignmentFlag.AlignCenter)
            if i == len(self.monitor.calibrations) - 1:
                self.listLayout.addWidget(self.tempEditR, i, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
            else:
                self.tempEditsR.append(self.line_edit())
                self.tempEditsR[-1].setText(str(self.monitor.calibSplit[i]))
                valueValidator = QIntValidator()
                valueValidator.setBottom(0)
                self.tempEditsR[-1].setValidator(valueValidator)
                self.tempEditsR[-1].editingFinished.connect(self.text_changed_R)
                self.listLayout.addWidget(self.tempEditsR[-1], i, 4, 1, 1, Qt.AlignmentFlag.AlignCenter)
    
    def add_calibration(self):
        position = self.select_calibration("Edit")
        if position == -1: return
        calib = GlobalData.globalCalibrations[position].copy()
        pos = len(self.monitor.calibrations)
        if pos > 0:
            if len(self.monitor.calibSplit) == 0:
                self.monitor.calibSplit.append(0)
            else: self.monitor.calibSplit.append(self.monitor.calibSplit[-1])
        self.monitor.calibrations.append(calib)
        self.display_calibrations()
        self.resize_list_widget()
        self.verify_buttons()
    
    def change_name(self):
        self.monitor.name = self.editName.text()
    
    def change_regex(self):
        if self.regexCheckbox.isChecked():
            self.monitor.regex = self.editRegex.text()
        
    def changeL(self):
        self.monitor.L = int(self.editL.text())
        if self.monitor.L > self.monitor.R:
            self.editL.setStyleSheet("background-color:#FFCCCB")
            self.editR.setStyleSheet("background-color:#FFCCCB")
        else: 
            self.editL.setStyleSheet("background-color:#FFF")
            self.editR.setStyleSheet("background-color:#FFF")
        self.verify_buttons()
        
    def changeR(self):
        self.monitor.R = int(self.editR.text())
        if self.monitor.L > self.monitor.R:
            self.editL.setStyleSheet("background-color:#FFCCCB")
            self.editR.setStyleSheet("background-color:#FFCCCB")
        else: 
            self.editL.setStyleSheet("background-color:#FFF")
            self.editR.setStyleSheet("background-color:#FFF")
        self.verify_buttons()
        
    def label(self, text):
        res = QLabel(text)
        res.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        return res
    
    def line_edit(self):
        res = QLineEdit()
        res.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        return res
    
    def reject(self):
        super().done(0)
        
    def accept(self):
        super().done(1)
        
    def save_as_new(self):
        super().done(2)