from cgitb import text
from tkinter import font
from turtle import title
from typing import Tuple
from PyQt5.QtWidgets import QWidget,QGridLayout, QApplication, QGroupBox, QHBoxLayout
import sys

import cv2
sys.path.append('./')
from APP.MAKEDATASET.views.basic.panel_one_image import PanelImage
from APP.MAKEDATASET.views.basic import CustomSpinBox, CustomLabel, LabelFont
from APP.MAKEDATASET.models import TEST_IMG, ZMIN, ZMAX
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToShow

class PanelMinMaxEdit( QWidget):
    def __init__(self, units: int= None, parent: QWidget= None)->None:
        super().__init__(parent=parent)
        main_layout = QHBoxLayout(self)
        self.title = 'Depth Visualization Range'
        self.group_box = QGroupBox(self.title, font=LabelFont())
        self.set_units(units=units)
        layout = QHBoxLayout(self.group_box)
        #spinbox
        self.spin_box_min = CustomSpinBox('Min')
        self.spin_box_min.set_value(ZMIN)
        layout.addWidget(self.spin_box_min)
        self.spin_box_max = CustomSpinBox('Max')
        self.spin_box_max.set_value(ZMAX)
        layout.addWidget(self.spin_box_max)
        self.setMaximumHeight(100)
        main_layout.addWidget(self.group_box)
        
    def get_range(self)-> Tuple[int]:
        min = self.spin_box_min.get_value()
        max = self.spin_box_max.get_value()
        return min,max
    
    def set_units(self, units: int):
        text = self.title + f' [{units}]'
        self.group_box.setTitle(text)
 
class PanelRGBDImage(QWidget):
    def __init__(self, parent: QWidget= None):
        """Panel to show an rgb-d image pair

        Args:
            parent (QWidget, optional): widget parent. Defaults to None.
        """
        super().__init__(parent=parent)
        self.init_gui()
        
        
    def init_gui(self):
        self.panel_visualization_range = PanelMinMaxEdit()
        self.panel_rgb = PanelImage('RGB')
        self.panel_depth = PanelImage('Depth')
        layout = QGridLayout(self)
        layout.addWidget(self.panel_visualization_range, 0, 0, 1, 2)
        layout.addWidget(self.panel_rgb, 1, 0, 2, 1)
        layout.addWidget(self.panel_depth, 1, 1, 2, 1)
        
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
    window.panel_visualization_range.set_units('100 um')
    window.update_rgbd(data_to_show)
    window.show()
    sys.exit(app.exec_())

    
    