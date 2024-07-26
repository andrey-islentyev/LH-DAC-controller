import numpy as np
import copy

from Fitter import *

class CalibrationData:
    def __init__(self):
        self.l = []
        self.I = []
        self.T = []
        self.name = ""
        self.L = 0
        self.R = 2000
        self.temp = 2524
        self.dTemp = 0
        
    def copy(self):
        return copy.deepcopy(self)
    
    def calculate_T(self):
        self.T = Fitter.calculateT(self.l, self.I, self.temp, self.L, self.R)
        
    def set_data(self, data):
        self.l = data[:, 0]
        self.I = np.abs(data[:, 1])
        self.I /= np.max(self.I)
        self.temp = 2524
        self.L, self.R = 0, 0
        curPos = 0
        while curPos < len(self.I):
            if self.I[curPos] > 0.1:
                curL, curR = curPos, curPos
                while curPos < len(self.I) and self.I[curPos] > 0.1:
                    curR += 1
                    curPos += 1
                curR -= 1
                curPos -= 1
                if curR - curL > self.R - self.L:
                    self.L, self.R = curL, curR
            curPos += 1
        
        self.L = self.l[self.L]
        self.R = self.l[self.R]
        range = self.R - self.L
        self.L -= 0.001 * range
        self.R += 0.001 * range
            
            