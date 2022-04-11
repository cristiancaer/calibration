from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication
import cv2
import numpy as np
from PyQt5.QtCore import Qt
import sys
sys.path.append('./')
from APP.MAKEDATASET.views import depth2color
from APP.MAKEDATASET.models import TEST_IMG


class LabelForImage(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.shape = None  # shape of the image to show
        self.image_format = QImage.Format_RGB888
        self.init_gui()

    def init_gui(self):
        self.setScaledContents(True)

    def update_image(self, frame: np.ndarray) -> None:
        """         
        Args:
            frame (np.ndarray): an image, it must be a numpy array 3 chanel
        """
        if frame.dtype == np.uint16:
            frame = depth2color(frame)
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


#TEST
################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelForImage()
    print(TEST_IMG)
    window.update_img_from_path(TEST_IMG)
    sys.exit(app.exec_())
