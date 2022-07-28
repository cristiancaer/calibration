import sys
sys.path.append('./')
from APP.control import depth2color
from PyQt5.QtGui import QPixmap, QImage
import cv2
import numpy as np
from PyQt5.QtCore import Qt


class InterfaceForImage():
    def __init__(self ):
        self.shape = None  # shape of the image to show
        self.image_format = QImage.Format_RGB888
        self.init_gui()

    def init_gui(self):
        if hasattr(self,'setScaledContents'):
            self.setScaledContents(True)

    def update_image(self, frame: np.ndarray) -> None:
        """         
        Args:
            frame (np.ndarray): an image, it must be a numpy array 3 chanel
        """
        pass

    def frame_to_pixmap(self, frame: np.ndarray) -> QPixmap:
        """ a QLabel need a QPimax to show an image. this function allow to convert a numpy-array image to a pixmap. 

        Args:
            frame (np.ndarray): numpy array 3 chanel image

        Returns:
            QPixmap: object to show a image into a QLabel
        """
        # the most part of time the image keep the shape
        if frame.dtype == np.uint16:
            frame = depth2color(frame)
        if self.shape != frame.shape:
            self.shape = frame.shape
            self.height_img, self.width_img, self.channels = frame.shape
            self.bytes_per_line = self.channels*self.width_img
        image = QImage(frame.data, self.width_img, self.height_img,
                       self.bytes_per_line, self.image_format)
        pixmap = QPixmap(QPixmap.fromImage(image))
        return pixmap

    def update_img_from_path(self, path_name: str):
        """
        Args:
            path (str): path and name to the file
        """
        img = cv2.imread(path_name)
        if hasattr(img, 'shape'):
            self.update_image(img)
        else:
            print('image not found')
    
    def clear_canvas(self):
        if self.shape is None:
            self.black_img = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            self.black_img = np.zeros(self.shape, dtype=np.uint8)
        self.update_image(self.black_img)
