from PyQt6.QtWidgets import QApplication
from Window import Window

import ctypes
import sys

class Application:
    def __init__(self):
        self.qapp = QApplication.instance()
        if not self.qapp:
            self.qapp = QApplication(sys.argv)
        self.win = Window()
        self.win.show()
        sys.exit(self.qapp.exec())

        
if __name__ == '__main__':
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('DLS.LH-DAC')
    a = Application()