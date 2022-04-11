import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication, QSizePolicy
from PyQt5.QtCore import Qt
sys.path.append('./')
from APP.MAKEDATASET.views.basic.label_for_image import LabelForImage
from APP.MAKEDATASET.views.basic import LabelFont
from APP.MAKEDATASET.models import RGB_PREFIX, TEST_IMG


class PanelImage(QWidget):
    def __init__(self, title: str = None):
        super().__init__()
        self.title = title  # title of image
        self.init_gui()

    def init_gui(self):
        """set up visualization
            it has:
            a label to put a title to the image.
            a canvas label to show an image.
        """
        layout = QVBoxLayout()
        self.setLayout(layout)
        # image title
        self.label_image_title = QLabel(self.title)
        self.label_image_title.setFont(LabelFont())
        self.label_image_title.setAlignment(Qt.AlignCenter)
        self.label_image_title.setMinimumSize(1, 40)
        self.label_image_title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # canvas
        self.canvas = LabelForImage()
        self.canvas.setScaledContents(True)
        self.canvas.setMinimumSize(1, 1)
        layout.addWidget(self.label_image_title)
        layout.addWidget(self.canvas)
    
    def update_image(self, frame: np.ndarray):
        """         
        Args:
            frame (np.ndarray): an image, it must be a numpy array 3 chanel uint8 datatype
        """
        self.canvas.update_image(frame)


#TEST
################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    img = cv2.imread(TEST_IMG)
    window = PanelImage(RGB_PREFIX)
    window.canvas.update_image(img)
    window.show()
    sys.exit(app.exec_())
