from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout
import sys
from APP.MAKEDATASET.models import DatasetTypes
sys.path.append('./')
from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
from APP.MAKEDATASET.views.basic.buttons import BasicButton
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES


class PanelToSave(QWidget):
    def __init__(self, type_dataset:str, parent: QWidget= None)->None:
        super().__init__(parent=parent)
        self.get_title_button_save(type_datset=type_dataset)
        self.init_gui()
        self.save_title: str = None
        
    def init_gui(self):
        layout = QVBoxLayout(self)
        self.button_save = BasicButton(self.save_title)
        self.panel_rgb_d = PanelRGBDImage()
        
    
    def get_title_button_save(self, type_datset: str)-> str:
        self.save_title = 'Screamshot'
        if type_datset == DATASET_TYPES.MILL:
            self.save_title = 'Save'
        return self.save_title