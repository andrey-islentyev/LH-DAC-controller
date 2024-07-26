from threading import Lock
from watchdog.observers import Observer
from .FileWatcher import FileWatcher

import numpy as np
import random


class MonitoringData:
    def __init__(self):
        self.hasArduino = False
        self.arduino = None
        
        self.name = ""
        self.L = 0
        self.R = 100000
        self.calibrations = []
        self.calibSplit = []
        self.folder = ""
        self.regex = None
        
        self.dataLock = Lock()
        colors = ["black", "tab:blue", "tab:orange", "tab:green", "tab:purple",
                  "tab:brown", "tab:pink", "tab:gray", "tab:olive", "tab:cyan"]
        self.color = colors[random.randint(0, len(colors) - 1)]
        
        self.l = np.array([])
        self.I = np.array([])
        self.arrtmp = np.array([])
        self.actualI = np.array([])
        self.temp = np.array([])
        self.deltaTemp = np.array([])
        self.hasData = False
        
        self.statusLock = Lock()
        self.running = False
    
    def control(self):
        with self.arduino.statusLock:
            if self.arduino.status != "Running":
                if self.arduino.status == "Error: user interrupt":
                    self.arduino.status = "Success"
                self.hasArduino = False
                self.arduino = None
            else:
                tempArr = []
                if self.temp.size >= 50: tempArr = self.temp[-50:]
                else:
                    tempArr = [self.arduino.target] * (50 - self.temp.size) + list(self.temp[:])
                self.arduino.control(tempArr)
        
    def copy(self):
        res = MonitoringData()
        res.name = self.name
        res.L, res.R = self.L, self.R
        res.calibrations = self.calibrations.copy()
        res.calibSplit = self.calibSplit.copy()
        res.folder = self.folder
        res.regex = self.regex
        return res
                
    def play(self):
        with self.statusLock:
            self.running = True
            print("Running " + str(self.name))
        event_handler = FileWatcher(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, path=self.folder, recursive=False)
        self.observer.start()
        
    def pause(self):
        self.observer.stop()
        self.observer.join()
        with self.statusLock:
            self.stop = False
            self.running = False
            print("Stopped " + str(self.name))
        