from typing import List
from PyQt5.QtWidgets import QWidget,QApplication, QDialog, QGridLayout, QPushButton
from PyQt5.QtCore import QPointF, pyqtSlot, pyqtSignal, QPoint
from PyQt5.QtGui import QMouseEvent
import cv2
import numpy as np
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.label_for_image import LabelForImage
from APP.MAKEDATASET.models.draw_objects import LineStore, PointsStore


class CanvasImgShow(LabelForImage):
    last_store_full = pyqtSignal()
    
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.points_buffer: List[PointsStore] = []

    def mousePressEvent(self, event: QMouseEvent):
        mouse_point = self.map_to_img(event.pos())
        self.store_point(mouse_point)

    def store_point(self, mouse_point:QPointF):
        if not self.points_buffer:
            return
        self.points_buffer[0].add_point(mouse_point.x(), mouse_point.y())
        if self.points_buffer[0].is_full:
            self.points_buffer.pop(0)
            self.last_store_full.emit()
                
    def add_element_to_store(self, new_store: PointsStore) -> None:
        self.points_buffer.append(new_store) 
    
    def map_to_img(self, point:QPoint) -> QPointF:
        """ all the images will be scaled to the canvas, then any point of canvas has different coords regard to the original image"""
        y_ratio = self.height_img/self.height()
        x_ratio = self.width_img/self.width()
        return QPointF(point.x()*x_ratio, point.y()*y_ratio)


class Dialogo(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.resize(500, 500)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.paint = CanvasImgShow(self)
        self.paint.update_image(np.zeros((640,480,3), dtype= np.uint8))
        self.paint.clear_canvas()
        self.btn_draw_line = QPushButton("draw line")

        self.btn_clear = QPushButton("Clear")
        self.line = LineStore()

        self.layout.addWidget(self.btn_draw_line)

        self.layout.addWidget(self.btn_clear)
        self.layout.addWidget(self.paint)

        self.btnDefault = "background-color: grey; border: 0; padding: 10px"
        self.btnActive = "background-color: orange; border: 0; padding: 10px"


        self.btn_clear.clicked.connect(self.f_clear)
        self.btn_draw_line.clicked.connect(self.f_add_line)
        self.paint.last_store_full.connect(self.f_draw_line)
        
    def f_clear(self):
        self.paint.clear_canvas()
        self.line.clear()
    
    def f_add_line(self):
        if not self.line.is_full:
            self.paint.add_element_to_store(self.line)
            
    def f_draw_line(self) -> None:
        if self.line.is_full:
            line_img = cv2.line(self.paint.black_img, tuple(self.line.points[0]), tuple(self.line.points[1]),(255, 255, 255), 10)
            self.paint.update_image(line_img)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    prueba = Dialogo()
    prueba.show()
    app.exec_()
