from PyQt5.QtWidgets import QWidget,QHBoxLayout, QApplication
import sys

import cv2
sys.path.append('./')
from APP.MAKEDATASET.views.basic.panel_one_image import PanelImage
from APP.MAKEDATASET.models import TEST_IMG
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToShow

class PanelRGBDImage(QWidget):
    def __init__(self, parent: QWidget= None):
        """Panel to show an rgb-d image pair

        Args:
            parent (QWidget, optional): widget parent. Defaults to None.
        """
        super().__init__(parent=parent)
        self.panel_rgb = PanelImage('RGB')
        self.panel_depth = PanelImage('Depth')
        self.init_gui()
        
        
    def init_gui(self):
        layout = QHBoxLayout(self)
        layout.addWidget(self.panel_rgb)
        layout.addWidget(self.panel_depth)
        
    def update_rgbd(self, data_to_show: DataToShow):
        """update rgb-d image pair

        Args:
            data_to_show (DataToShow): it has a rgb-d image pair. both image are 3-chanel numpy array with uint8 datatype
        """
        self.panel_rgb.update_image(data_to_show.rgb)
        self.panel_depth.update_image(data_to_show.depth)
        

#TEST

if __name__=='__main__':
    img_test = cv2.imread(TEST_IMG)
    data_to_show = DataToShow(DataFromAcquisition(rgb=img_test, depth=img_test), depth_mod= img_test)
    app = QApplication(sys.argv)
    window = PanelRGBDImage()
    window.update_rgbd(data_to_show)
    window.show()
    sys.exit(app.exec_())

    
    