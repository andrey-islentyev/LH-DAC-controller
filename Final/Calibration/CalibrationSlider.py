from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

class CalibrationSlider:
    def __init__(self, controller):
        self.markerL = QPolygonF()
        self.markerR = QPolygonF()
        self.curChosenMarker = -1
        self.canvas = controller.canvas
        self.fieldL = controller.L
        self.fieldL.editingFinished.connect(self.field_changed)
        self.fieldR = controller.R
        self.fieldR.editingFinished.connect(self.field_changed)
        self.controller = controller
        self.posL = 300
        self.posR = 500
        
        self.canvas.paintEvent = self.paint_markers
        self.canvas.mousePressEvent = self.choose_marker
        self.canvas.mouseMoveEvent = self.move_marker
        self.canvas.mouseReleaseEvent = self.drop_marker
    
    def update_calibration(self):
        self.fieldL.setText("{0:.2f}".format(round(min(self.posL, self.posR), 2)))
        self.fieldR.setText("{0:.2f}".format(round(max(self.posL, self.posR), 2)))
        self.controller.calibrationData[-1].L = min(self.posL, self.posR)
        self.controller.calibrationData[-1].R = max(self.posL, self.posR)
        self.controller.calibrationData[-1].calculate_T()
        
    def field_changed(self):
        self.posL = min(float(self.fieldL.text()), float(self.fieldR.text()))
        self.posR = max(float(self.fieldL.text()), float(self.fieldR.text()))
        self.update_calibration()
        self.controller.paint_canvas()

    def get_polygon(self, posx, width, height):
        addPosX = self.canvas.width() / 8 + self.canvas.width() * 6 / 8 *\
            (posx - self.controller.figure.get_xlim()[0]) / (self.controller.figure.get_xlim()[1] - self.controller.figure.get_xlim()[0])
        addPosY = self.canvas.height() * 8 / 9 + 1.6 * height
        pointArr = [QPointF(addPosX - width / 2, addPosY), QPointF(addPosX + width / 2, addPosY),
                    QPointF(addPosX + width / 2, -(height) + addPosY), QPointF(addPosX, -(1.6 * height) + addPosY),
                    QPointF(addPosX - width / 2, -(height)  + addPosY)]
        return QPolygonF(pointArr)
    
    def paint_markers(self, event):
        FigureCanvas.paintEvent(self.canvas, event)
        if self.fieldL.isEnabled() and self.fieldR.isEnabled():
            qp = QPainter(self.canvas)
            qp.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            qp.setBrush(QBrush(QColor(229, 0, 0)))
            self.markerL = self.get_polygon(self.posL, 10, 14)
            qp.drawConvexPolygon(self.markerL)
            self.markerR = self.get_polygon(self.posR, 10, 14)
            qp.drawConvexPolygon(self.markerR)
    
    def choose_marker(self, event):
        FigureCanvas.mousePressEvent(self.canvas, event)
        if self.fieldL.isEnabled() and self.fieldR.isEnabled():
            if self.markerL.containsPoint(event.pos().toPointF(), Qt.FillRule.OddEvenFill):
                self.curChosenMarker = 0
            elif self.markerR.containsPoint(event.pos().toPointF(), Qt.FillRule.OddEvenFill):
                self.curChosenMarker = 1
                
    def move_marker(self, event):
        FigureCanvas.mouseMoveEvent(self.canvas, event)
        if self.curChosenMarker != -1:
            if self.curChosenMarker == 0:
                if event.pos().x() < self.canvas.width() // 8: self.posL = self.controller.figure.get_xlim()[0]
                elif event.pos().x() > self.canvas.width() * 7 // 8: self.posL = self.controller.figure.get_xlim()[1]
                else: self.posL = self.controller.figure.get_xlim()[0] + (self.controller.figure.get_xlim()[1] -\
                    self.controller.figure.get_xlim()[0]) * (event.pos().x() - self.canvas.width() // 8) / (self.canvas.width() * 6 // 8)
            elif self.curChosenMarker == 1:
                if event.pos().x() < self.canvas.width() // 8: self.posR = self.controller.figure.get_xlim()[0]
                elif event.pos().x() > self.canvas.width() * 7 // 8: self.posR = self.controller.figure.get_xlim()[1]
                else: self.posR = self.controller.figure.get_xlim()[0] + (self.controller.figure.get_xlim()[1] -\
                    self.controller.figure.get_xlim()[0]) * (event.pos().x() - self.canvas.width() // 8) / (self.canvas.width() * 6 // 8)
            self.update_calibration()
            self.controller.paint_canvas()

    def drop_marker(self, event):
        FigureCanvas.mouseReleaseEvent(self.canvas, event)
        self.curChosenMarker = -1