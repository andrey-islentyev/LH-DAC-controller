from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileMovedEvent
from Calibration.CalibrationData import CalibrationData
from Fitter import Fitter
import numpy as np
import re

class FileWatcher(FileSystemEventHandler):

    def __init__(self, calculator):
        self.calculator = calculator
        self.arr = []
        
    def on_created(self, event):
        if isinstance(event, FileCreatedEvent):
            self.process_file(event)
    
    def on_moved(self, event):
        if isinstance(event, FileMovedEvent):
            self.process_file(event)
    
    def process_file(self, event):
        if self.calculator.regex == None:
            if not (".txt" in event.src_path or ".in" in event.src_path): return
        else:
            try:
                value = re.match(self.calculator.regex, event.src_path)
                if value == None: return
            except:
                print(f"RegEx error with file {event.src_path} and RegEx {self.calculator.regex}")
                return
        self.arr.append(event.src_path)
        if len(self.arr) > 1:
            lowTemp, highTemp = False, False
            try:
                data = np.loadtxt(self.arr[-2])
                if np.max(np.abs(data[:, 1])) < self.calculator.L:
                    print(f"LowTemp: {np.max(np.abs(data[:, 1])):.2f}")
                    lowTemp = True
                elif np.max(np.abs(data[:, 1])) > self.calculator.R:
                    print(f"HighTemp: {np.max(np.abs(data[:, 1])):.2f}")
                    highTemp = True
                if not highTemp and not lowTemp:
                    curData = CalibrationData()
                    curData.set_data(data)
                    try: 
                        calibPos = 0
                        if self.calculator.temp.size > 0 and len(self.calculator.calibrations) > 1:
                            while calibPos < len(self.calculator.calibSplit) and self.calculator.calibSplit[calibPos] < self.calculator.temp[-1]:
                                calibPos += 1
                        arrtmp, actualI = Fitter.calculate_temperature(self.calculator.calibrations[calibPos], curData)
                        with self.calculator.dataLock:
                            self.calculator.hasData = True
                            self.calculator.l = np.copy(curData.l)
                            self.calculator.I = np.copy(curData.I)
                            self.calculator.arrtmp = np.copy(arrtmp)
                            self.calculator.actualI = np.copy(actualI)
                            self.calculator.temp = np.append(self.calculator.temp, curData.temp)
                            self.calculator.deltaTemp = np.append(self.calculator.deltaTemp, curData.dTemp)
                    except:
                        with self.calculator.dataLock:
                            self.calculator.hasData = False
                        print("Error fitting black-body curve")
                else:
                    with self.calculator.dataLock:
                        self.calculator.hasData = True
                        self.calculator.l = data[:, 0]
                        self.calculator.arrtmp = data[:, 0]
                        if lowTemp:
                            self.calculator.I = np.zeros(self.calculator.l.size)
                            self.calculator.actualI = np.zeros(self.calculator.l.size)
                        if highTemp:
                            self.calculator.I = np.ones(self.calculator.l.size)
                            self.calculator.actualI = np.ones(self.calculator.l.size)
                        self.calculator.temp = np.append(self.calculator.temp, 0 if lowTemp else 5000)
                        self.calculator.deltaTemp = np.append(self.calculator.deltaTemp, 0)
                with self.calculator.dataLock:
                    if self.calculator.hasArduino:
                        self.calculator.control()
            except:
                with self.calculator.dataLock:
                    self.calculator.hasData = False
                print("Could not parse file " + self.arr[-2])
            self.arr = [self.arr[-1]]
