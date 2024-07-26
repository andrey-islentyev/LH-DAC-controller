from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

import numpy as np
import os

from Calibration.CalibrationDialog import CalibrationDialog
from .MonitoringDialog import MonitoringDialog
from Calibration.CalibrationData import CalibrationData
from .MonitoringData import MonitoringData
from .ButtonPadExclusive import ButtonPadExclusive
from Fitter import Fitter
from GlobalData import GlobalData

class AnalysisController:
    def __init__(self, canvas):
        GlobalData.openTabs.append(self)
        
        self.listEntryHeight = 2 * QApplication.primaryScreen().availableGeometry().height() // 70
        self.canvas = canvas
        self.figure = self.canvas.figure.subplots()
        self.mode = 0
        
        self.calibrationButton = QPushButton("Calibration")
        self.calibrationButton.pressed.connect(self.choose_calibration)
        self.calibration = self.line_edit()
        self.calibration.setReadOnly(True)
        self.fileButton = QPushButton("File")
        self.fileButton.pressed.connect(self.load_file)
        self.file = self.line_edit()
        self.file.setReadOnly(True)
        self.analyseButton = QPushButton("Analyse")
        self.analyseButton.pressed.connect(self.analyse_file)
        self.filePath = ""
        self.analysisData = CalibrationData()
        self.hasData = False
        self.calib = None
        self.hasCalib = False
        self.hasFile = False
        self.actualI = []
        
        self.monitorHolderList = []
        self.labelList = []
        self.playButtonList = []
        self.pauseButtonList = []
        self.buttonGroupList = []
        self.selectViewButtonList = []
        self.monitorData = []
        self.savePosition = 0
        self.runningCnt = 0
        self.drawTimer = QTimer()
        self.drawTimer.timeout.connect(self.paint_plots)
        self.viewa, self.viewb = 1, 1
        
        self.createButton = QPushButton("Create")
        self.createButton.pressed.connect(self.create_monitoring)
        self.editButton = QPushButton("Edit")
        self.editButton.pressed.connect(self.edit_monitoring)
        self.removeButton = QPushButton("Remove")
        self.removeButton.pressed.connect(self.remove_monitoring)
        self.verify_buttons()
        
        self.statusList = QWidget()
        self.listLayout = QVBoxLayout(self.statusList) 
        self.listLayout.setContentsMargins(5, 2, 5, 0)
        self.listLayout.setSpacing(1)
        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.statusList)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea.setBackgroundRole(QPalette.ColorRole.Light)
        
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.buttonToggled.connect(self.change_mode)
        self.viewMode = QButtonGroup()
        self.viewMode.buttonClicked.connect(self.change_view)
    
    def paint_plots(self):
        if self.mode == 1:
            position = {}
            for i, pad in enumerate(self.selectViewButtonList):
                position[(pad.cura, pad.curb)] = i
            self.canvas.figure.clear()
            axes = self.canvas.figure.subplots(self.viewa, self.viewb, squeeze = False)
            for i in range(self.viewa):
                for j in range(self.viewb):
                    if not (i, j) in position.keys(): self.show_text(axes[i][j], "No monitor connected")
                    else: 
                        pos = position[(i, j)]
                        with self.monitorData[pos].dataLock:
                            if not self.monitorData[pos].hasData:
                                self.show_text(axes[i][j], "Awaiting data")
                            else:
                                axes[i][j].set_ylim([0, 1.01])
                                axes[i][j].set_title(f"{self.monitorData[pos].name}: {self.monitorData[pos].temp[-1]:.2f} +- {self.monitorData[pos].deltaTemp[-1]:.2f}")
                                if self.monitorData[pos].temp[-1] > 1 and self.monitorData[pos].temp[-1] < 999998:
                                    arry = Fitter.normalised_spectral_intensity(self.monitorData[pos].arrtmp * 1e-9, self.monitorData[pos].temp[-1])
                                    arry /= np.max(arry)
                                    axes[i][j].plot(self.monitorData[pos].arrtmp, arry, color =  self.monitorData[pos].color, ls = "-", lw = 5, alpha = 0.2)
                                axes[i][j].plot(self.monitorData[pos].arrtmp, self.monitorData[pos].actualI, color = self.monitorData[pos].color, ls = "-", lw = 1)
            self.canvas.draw()
        
    def get_switch_handler(self, buttonPad, buttonGroup):
        def handler(e):
            if buttonPad.cura != -1 and buttonPad.curb != -1:
                for i, group in enumerate(self.buttonGroupList):
                    if group != buttonGroup:
                        if self.selectViewButtonList[i].cura == buttonPad.cura and self.selectViewButtonList[i].curb == buttonPad.curb:
                            self.selectViewButtonList[i].click(self.selectViewButtonList[i].buttonArr[buttonPad.cura][buttonPad.curb])
            self.paint_plots()
        return handler           
    
    def remake_monitor_choices(self):
        for i in range(len(self.monitorData)):
            self.monitorHolderList[i].layout().removeWidget(self.selectViewButtonList[i])
            a, b = self.selectViewButtonList[i].cura, self.selectViewButtonList[i].curb
            self.selectViewButtonList[i].deleteLater()
            self.buttonGroupList[i] = QButtonGroup()
            self.selectViewButtonList[i] = ButtonPadExclusive(self.viewa, self.viewb, 2 * self.listEntryHeight // 3,
                2 * self.listEntryHeight // 3, self.buttonGroupList[i], a, b)
            self.buttonGroupList[i].buttonClicked.connect(self.get_switch_handler(self.selectViewButtonList[i], self.buttonGroupList[i]))
            self.monitorHolderList[i].layout().addWidget(self.selectViewButtonList[i])
        self.paint_plots()
            
    def change_view(self, button):
        self.viewa, self.viewb = button.property("distX") + 1, button.property("distY") + 1
        self.remake_monitor_choices()
        
    def select_calibration(self, name):
        dlg = CalibrationDialog(name, [i.name for i in GlobalData.globalCalibrations], self.calibrationButton)
        return dlg.exec() - 1
    
    def choose_calibration(self):
        position = self.select_calibration("Edit")
        if position == -1: return
        self.hasCalib = True
        self.calib = GlobalData.globalCalibrations[position].copy()
        self.calibration.setText(GlobalData.globalCalibrations[position].name)
        self.verify_buttons()
        
    def load_file(self):
        path = QFileDialog.getOpenFileName()
        if path != ('', ''):
            self.hasFile = True
            self.filePath = path[0]
            self.file.setText(os.path.basename(path[0]))
            self.verify_buttons()

    def analyse_file(self):
        try:
            data = np.loadtxt(self.filePath)
            self.analysisData.set_data(data)
            try: 
                self.arrtmp, self.actualI = Fitter.calculate_temperature(self.calib, self.analysisData)
                self.hasData = True
            except:
                self.hasData = False
                print("Error fitting black-body curve")
        except:
            self.hasData = False
            print("Could not parse file " + self.filePath)
        self.paint_canvas()
        
    def line_edit(self):
        res = QLineEdit()
        res.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        return res
    
    def resize_list_widget(self):
        count = len(self.monitorData)
        self.statusList.setFixedWidth(self.scrollArea.width())
        self.statusList.setFixedHeight(2 + (1 + self.listEntryHeight) * count)
        self.statusList.adjustSize()
    
    def set_icon(self, button, path):
        icon = QIcon(QPixmap(path))
        button.setIcon(icon)
        button.setIconSize(QSize(button.width() - 4, button.height() - 4))
        button.setStyleSheet("""
            QPushButton{background-color: white; border-style: outset; border-width: 2px; border-color: #AAA;}
            QPushButton:pressed{border-style: inset;}""")
    
    def get_play_handler(self, monitor, play, pause):
        def handler():
            self.runningCnt += 1
            play.setEnabled(False)
            self.set_icon(play, "Final/play_disabled.png")
            pause.setEnabled(True)
            self.set_icon(pause, "Final/pause.png")
            monitor.play()
            for i in range(len(self.monitorData)):
                if self.monitorData[i] == monitor:
                    GlobalData.globalMonitors[i] = None
                    GlobalData.notify_all()
            self.verify_buttons()
        return handler
    
    def get_pause_handler(self, monitor, play, pause):
        def handler():
            self.runningCnt -= 1
            play.setEnabled(True)
            self.set_icon(play, "Final/play.png")
            pause.setEnabled(False)
            self.set_icon(pause, "Final/pause_disabled.png")
            monitor.pause()
            for i in range(len(self.monitorData)):
                if self.monitorData[i] == monitor:
                    GlobalData.globalMonitors[i] = monitor
                    GlobalData.notify_all()
            self.verify_buttons()
        return handler
    
    def add_monitor_item(self, monitor):
        container = QWidget()
        container.setFixedHeight(self.listEntryHeight)
        self.monitorHolderList.append(container)
        containerLayout = QHBoxLayout(container)
        containerLayout.setContentsMargins(0, 0, 0, 0)
        containerLayout.setSpacing(1)
        
        self.labelList.append(QLabel(monitor.name))
        self.labelList[-1].setFixedHeight(self.listEntryHeight)
        containerLayout.addWidget(self.labelList[-1])
        
        self.playButtonList.append(QPushButton())
        self.playButtonList[-1].setFixedHeight(2 * self.listEntryHeight // 3)
        self.playButtonList[-1].setFixedWidth(2 * self.listEntryHeight // 3)
        self.set_icon(self.playButtonList[-1], "Final/play.png")
        containerLayout.addWidget(self.playButtonList[-1])
        
        self.pauseButtonList.append(QPushButton())
        self.pauseButtonList[-1].setFixedHeight(2 * self.listEntryHeight // 3)
        self.pauseButtonList[-1].setFixedWidth(2 * self.listEntryHeight // 3)
        self.pauseButtonList[-1].setEnabled(False)
        self.set_icon(self.pauseButtonList[-1], "Final/pause_disabled.png")
        containerLayout.addWidget(self.pauseButtonList[-1])
        
        self.buttonGroupList.append(QButtonGroup())
        self.selectViewButtonList.append(ButtonPadExclusive(self.viewa, self.viewb, 2 * self.listEntryHeight // 3,
            2 * self.listEntryHeight // 3, self.buttonGroupList[-1]))
        containerLayout.addWidget(self.selectViewButtonList[-1])
    
        self.buttonGroupList[-1].buttonClicked.connect(self.get_switch_handler(self.selectViewButtonList[-1], self.buttonGroupList[-1]))
        self.playButtonList[-1].pressed.connect(self.get_play_handler(monitor, self.playButtonList[-1], self.pauseButtonList[-1]))
        self.pauseButtonList[-1].pressed.connect(self.get_pause_handler(monitor, self.playButtonList[-1], self.pauseButtonList[-1]))
        self.statusList.layout().addWidget(container)
        self.monitorData.append(monitor)
        GlobalData.globalMonitors.append(monitor)
        GlobalData.notify_all()
        
    def update_monitoring(self, name, monitor, saveOptions):
        dlg = MonitoringDialog(name, monitor, saveOptions, self.createButton)
        value = dlg.exec()
        if value == 1 and self.savePosition < len(self.monitorData): 
            self.playButtonList[self.savePosition].pressed.disconnect()
            self.playButtonList[self.savePosition].pressed.connect(self.get_play_handler(monitor,
                self.playButtonList[self.savePosition], self.pauseButtonList[self.savePosition]))
            self.pauseButtonList[self.savePosition].pressed.disconnect()
            self.pauseButtonList[self.savePosition].pressed.connect(self.get_pause_handler(monitor,
                self.playButtonList[self.savePosition], self.pauseButtonList[self.savePosition]))
            if self.monitorData[self.savePosition].hasArduino:
                arduino = self.monitorData[self.savePosition].arduino
                monitor.arduino = arduino
                monitor.hasArduino = True
            self.monitorData[self.savePosition] = monitor
            GlobalData.globalMonitors[self.savePosition] = monitor
            GlobalData.notify_all()
            self.labelList[self.savePosition].setText(monitor.name)
        elif value == 2 or (value == 1 and self.savePosition == len(self.monitorData)):
            self.add_monitor_item(monitor)
        self.resize_list_widget()
        self.verify_buttons()
        self.paint_canvas()
        
    def create_monitoring(self):
        data = MonitoringData()
        data.name = "Monitor" + str(len(self.monitorData))
        self.savePosition = len(self.monitorData)
        self.update_monitoring("Create", data, 1)
        
    def select_monitoring(self, name):
        option = []
        position = {}
        for i, monitor in enumerate(self.monitorData):
            with monitor.statusLock:
                if not monitor.running:
                    option.append(monitor.name)
                    position[len(position)] = i
        dlg = CalibrationDialog(name, option, self.createButton)
        value = dlg.exec() - 1
        if value == -1: return value
        else: return position[value]
    
    def edit_monitoring(self):
        position = self.select_monitoring("Edit")
        if position == -1: return
        self.savePosition = position
        self.update_monitoring("Edit", self.monitorData[position].copy(), 2)
    
    def remove_monitoring(self):
        position = self.select_monitoring("Remove")
        if position == -1: return
        self.monitorData.pop(position)
        GlobalData.globalMonitors.pop(position)
        GlobalData.notify_all()
        container = self.monitorHolderList[position]
        self.monitorHolderList.pop(position)
        self.statusList.layout().removeWidget(container)
        
        container.layout().removeWidget(self.labelList[position])
        self.labelList[position].deleteLater()
        self.labelList.pop(position)
        
        container.layout().removeWidget(self.playButtonList[position])
        self.playButtonList[position].deleteLater()
        self.playButtonList.pop(position)
        
        container.layout().removeWidget(self.pauseButtonList[position])
        self.pauseButtonList[position].deleteLater()
        self.pauseButtonList.pop(position)
        
        self.buttonGroupList[position].deleteLater()
        self.buttonGroupList.pop(position)
        
        container.layout().removeWidget(self.selectViewButtonList[position])
        self.selectViewButtonList[position].deleteLater()
        self.selectViewButtonList.pop(position)
        
        container.deleteLater()
        self.resize_list_widget()
        self.verify_buttons()
        self.paint_canvas()
        
    def change_mode(self, button, checked):
        if checked: 
            self.mode = {"Analysis": 0, "Monitor": 1}[button.text()]
            if self.mode == 1:
                self.paint_plots()
                self.drawTimer.start(50)
                self.scrollArea.setHidden(False)
            elif self.mode == 0:
                self.drawTimer.stop()
                self.scrollArea.setHidden(True)
                self.paint_canvas()
            
    def verify_buttons(self):
        self.analyseButton.setEnabled(self.hasCalib and self.hasFile)
        self.calibrationButton.setEnabled(len(GlobalData.globalCalibrations) > 0)
        self.createButton.setEnabled(len(GlobalData.globalCalibrations) > 0)
        self.editButton.setEnabled(len(self.monitorData) - self.runningCnt > 0)
        self.removeButton.setEnabled(len(self.monitorData) - self.runningCnt > 0)
    
    def show_text(self, axis, text):
        axis.set_axis_off()
        return axis.text((axis.get_xlim()[0] + axis.get_xlim()[1]) / 2, 
                         (axis.get_ylim()[0] + axis.get_ylim()[1]) / 2,
                         text, horizontalalignment='center', verticalalignment='center')
        
    def paint_canvas(self):
        if self.mode == 0:
            self.canvas.figure.clear()
            self.figure = self.canvas.figure.subplots()
            if not self.hasData: self.show_text(self.figure, "No analysis data available")
            else: 
                self.figure.set_position([1/8, 1/9, 6/8, 7/9])
                self.figure.set_ylim([0, 1.01])
                arrl = []
                arrI = []
                for i, l in enumerate(self.analysisData.l):
                    if self.calib.L < l and self.calib.R > l:
                        arrl.append(l)
                        arrI.append(self.analysisData.I[i])
                arrx = np.linspace(self.calib.L, self.calib.R, 1000, endpoint = True)
                arry = Fitter.alt_normalised_spectral_intensity(arrx * 1e-9, self.analysisData.temp)
                arry /= np.max(arry)
                self.figure.plot(arrl, self.actualI, color = "green", lw = 2, ls = "-")
                self.figure.plot(self.analysisData.l,self.analysisData.I, color = "black", lw = 0.5, ls = "--")
                self.figure.plot(arrl, self.actualI, color = "black", lw = 1, ls = "-")
                self.figure.set_title(f"{self.analysisData.temp} +- {self.analysisData.dTemp}")
            self.canvas.draw()
            