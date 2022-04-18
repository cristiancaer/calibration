from PyQt5.QtWidgets import QApplication, QDialog, QGridLayout, QPushButton, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import QPointF, QRectF, pyqtSlot, Qt
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cv2
import sys
sys.path.append('./')


class ImShowWidget(QGraphicsView):
    def __init__(self):
        QGraphicsView.__init__(self)
        self.setSceneRect(QRectF())
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.img = np.zeros((480, 640, 3), dtype=np.uint8)
        self.shape = None  # shape of the image to show
        self.image_format = QImage.Format_RGB888
        self.init_gui()
     # limpiar canvas

    def clear(self):
        self.img = np.zeros((480, 640, 3), dtype=np.uint8)
        self.scene.clear()
        self.update_image(self.img)

    def __init__(self, parent=None):
        super().__init__(parent=parent)


    def init_gui(self):
        self.setScaledContents(True)

    def update_image(self, frame: np.ndarray) -> None:
        """         
        Args:
            frame (np.ndarray): an image, it must be a numpy array 3 chanel
        """

        pixmap = self.frame_to_pixmap(frame)
        self.setPixmap(pixmap.scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.show()

    def frame_to_pixmap(self, frame: np.ndarray) -> QPixmap:
        """ a QLabel need a QPimax to show an image. this function allow to convert a numpy-array image to a pixmap. 

        Args:
            frame (np.ndarray): numpy array 3 chanel image

        Returns:
            QPixmap: object to show a image into a QLabel
        """
        # the most part of time the image keep the shape
        if self.shape != frame.shape:
            self.shape = frame.shape
            self.height_, self.width_, self.chanels = frame.shape
            self.bytes_per_line = self.chanels*self.width_
        image = QImage(frame.data, self.width_, self.height_, self.bytes_per_line, self.image_format)
        pixmap = QPixmap(QPixmap.fromImage(image))
        return pixmap

    def update_img_from_path(self, path_name: str):
        """
        Args:
            path (str): path and name to the file
        """
        img = cv2.imread(path_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        if hasattr(img, 'shape'):
            self.update_image(img)
        else:
            print('image not found')

class canvas(ImShowWidget):
    def __init__(self):
        super().__init__()
        self.listLines = []
        self.listPol = []
        self.drawing = False
        self.listBuffer = None

    def idle(self):
        return None

    def makeLine(self) -> None:
        self.drawing = True
        self.listLines.append(Line())
        self.listBuffer = self.listLines

    def makePoly(self, nsegments: int) -> None:
        self.drawing = True
        self.listPol.append(Polyn(nsegments))
        self.listBuffer = self.listPol

    def mousePressEvent(self, event):
        e = QPointF(self.mapToScene(event.pos()))
        self.getStroke(e)

    def getStroke(self, e):

        if self.drawing:
            if not self.listBuffer[-1].isComplete:
                self.listBuffer[-1].addPt([e.x(), e.y()])
                if self.listBuffer[-1].isComplete:
                    self.listBuffer = None
                    self.drawing = False
                    for l in self.listLines:
                        print(l)
                    for p in self.listPol:
                        print(p)


class Dialogo(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.resize(500, 500)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.paint = canvas()

        self.btnDrawLine = QPushButton("Dibujar V")

        self.btn_clear = QPushButton("Clear")

        self.layout.addWidget(self.btnDrawLine)

        self.layout.addWidget(self.btn_clear)
        self.layout.addWidget(self.paint)

        self.btnDefault = "background-color: grey; border: 0; padding: 10px"
        self.btnActive = "background-color: orange; border: 0; padding: 10px"

        self.btnDrawLine.setStyleSheet(self.btnDefault)
        self.btn_clear.setStyleSheet(self.btnDefault)
        self.btnDrawLine.clicked.connect(self.paint.makeLine)

        self.btn_clear.clicked.connect(self.isClear)

    def isClear(self):
        self.paint.clear()
        self.btn_clear.setStyleSheet(self.btnActive)

        self.btn_clear.setStyleSheet(self.btnDefault)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    prueba = Dialogo()
    prueba.show()
    app.exec_()
