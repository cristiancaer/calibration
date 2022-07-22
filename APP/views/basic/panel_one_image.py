import cv2
import numpy as np
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication, QSizePolicy
sys.path.append('./')
from APP.views.basic.label_for_image import LabelForImage
from APP.views.basic import CustomLabel
from APP.models.basic_config import RGB_PREFIX, TEST_IMG
from APP.MAKEDATASET.views.draw_tools.paint_canvas import CanvasImgShow


class PanelImage(QWidget):
    def __init__(self, title: str = None, allow_draw = False):
        super().__init__()
        self.title = title  # title of image
        self.allow_draw = allow_draw
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
        self.label_image_title = CustomLabel(self.title, center=True)
        self.label_image_title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        # canvas
        if self.allow_draw:
            self.canvas = CanvasImgShow(self)
        else:
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
    window = PanelImage(RGB_PREFIX, allow_draw=True)
    window.canvas.update_image(img)
    window.show()
    sys.exit(app.exec_())
