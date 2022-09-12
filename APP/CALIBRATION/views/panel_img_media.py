from typing import Dict, List
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSlot
import sys
sys.path.append('./')
from APP.views.basic.panel_one_image import PanelImage
from APP.views.basic.buttons import BackNextButtons, BasicButton
from APP.CALIBRATION.models.data_objects import ImgData, ImgTypeNames


class PanelImgMedia(QWidget):
    def __init__(self, list_img_panel_names:List[str],parent: QWidget=None)->None:
        super().__init__(parent)
        self.list_img_panel_names = list_img_panel_names
        self.last_images = None
        self.dict_image_panels:Dict[str, PanelImage] = {}
        self.init_gui()
        
    def add_image_panel(self, panel_name: str, allow_draw:bool= False):
        new_img_panel = PanelImage(panel_name, allow_draw)
        self.dict_image_panels.update({panel_name:new_img_panel})
        self.images_layout.addWidget(new_img_panel)
    
    def get_img_panel(self, name):
        return self.dict_image_panels.get(name)
        
    def init_gui(self):
        group_images = QGroupBox()
        self.images_layout = QHBoxLayout(group_images)
        for name in self.list_img_panel_names:
            self.add_image_panel(name)
        
        main_layout = QGridLayout(self)
        main_layout.addWidget(group_images,0,0, 1,4)
        self.button_remove_img = BasicButton('Remove img','SP_TrashIcon')
        main_layout.addWidget(self.button_remove_img,1,3,1,1)
        self.back_next_buttons = BackNextButtons()
        self.back_next_buttons.back.setText('Last img')
        self.back_next_buttons.next.setText('Next img')
        self.back_next_buttons.setMaximumHeight(70)
        main_layout.addWidget(self.back_next_buttons, 1,0, 1,3)
        self.button_skip = BasicButton('Skip')
        self.button_skip.setVisible(False)
        main_layout.addWidget(self.button_skip, 2, 0, 1,4)
    
    def update_imgs(self, data: ImgData):
        for img_name, img in data.images.items():
            img_panel = self.get_img_panel(img_name)
            if img_panel:
                img_panel.update_image(img)
    
    def show_skip_button(self):
        self.button_skip.setVisible(True)
        
    

#TEST
################################################################################
if __name__=='__main__':
    app = QApplication(sys.argv)
    window = PanelImgMedia([ImgTypeNames.rgb, ImgTypeNames.depth, ImgTypeNames.undistorted])
    window.show()
    sys.exit(app.exec())
    
        