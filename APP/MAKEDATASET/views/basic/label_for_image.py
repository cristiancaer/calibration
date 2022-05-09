from PyQt5.QtWidgets import  QApplication, QLabel
import sys
sys.path.append('./')
from APP.MAKEDATASET.models import TEST_IMG
from APP.MAKEDATASET.views.basic.interface_to_image import InterfaceForImage
import numpy as np

class LabelForImage(QLabel,InterfaceForImage):
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)
        InterfaceForImage.__init__(self)
        
    def update_image(self, frame: np.ndarray) -> None:
        pixmap = self.frame_to_pixmap(frame)
        self.setPixmap(pixmap)
        self.show()

#TEST
################################################################################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = LabelForImage()
    print(TEST_IMG)
    window.update_img_from_path(TEST_IMG)
    sys.exit(app.exec_())
