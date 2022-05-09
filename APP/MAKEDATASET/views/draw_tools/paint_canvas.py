from multiprocessing.connection import wait
import queue
from typing import List
from PyQt5.QtWidgets import QWidget,QApplication, QDialog, QGridLayout, QPushButton, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import QPointF, QRectF, pyqtSlot, Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
import cv2
import numpy as np
from queue import Queue
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.interface_to_image import InterfaceForImage
from APP.MAKEDATASET.models.draw_objects import Line, PointsStore

class CanvasImgShow(QGraphicsView, InterfaceForImage):
    last_store_full = pyqtSignal()
    def __init__(self, parent: QWidget= None):
        QGraphicsView.__init__(self,parent)
        self.setSceneRect(QRectF())
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        InterfaceForImage.__init__(self)
        self.clear()
        self.points_buffer: List[PointsStore] = []
    
    def update_image(self, frame: np.ndarray) -> None:
        pixmap = self.frame_to_pixmap(frame)
        self.scene.addPixmap(pixmap)
        self.setScene(self.scene)

    def clear(self):
        self.black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        self.scene.clear()
        self.update_image(self.black_img)

    def mousePressEvent(self, event):
        mouse_point = QPointF(self.mapToScene(event.pos()))
        self.store_point(mouse_point)

    def store_point(self, mouse_point:QPointF):
        if self.points_buffer:
            self.points_buffer[0].add_point(mouse_point.x(), mouse_point.y())
            if self.points_buffer[0].is_full:
                self.points_buffer.pop(0)
                self.last_store_full.emit()
                
    def add_element_to_store(self, new_store: PointsStore) -> None:
        self.points_buffer.append(new_store) 


class Dialogo(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.resize(500, 500)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.paint = CanvasImgShow(self)

        self.btn_draw_line = QPushButton("draw line")

        self.btn_clear = QPushButton("Clear")
        self.line = Line()

        self.layout.addWidget(self.btn_draw_line)

        self.layout.addWidget(self.btn_clear)
        self.layout.addWidget(self.paint)

        self.btnDefault = "background-color: grey; border: 0; padding: 10px"
        self.btnActive = "background-color: orange; border: 0; padding: 10px"


        self.btn_clear.clicked.connect(self.f_clear)
        self.btn_draw_line.clicked.connect(self.f_add_line)
        self.paint.last_store_full.connect(self.f_draw_line)
        
    def f_clear(self):
        self.paint.clear()
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
