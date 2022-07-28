from curses import window
import sys
from types import FunctionType
from typing import List
sys.path.append('./')
from APP.CALIBRATION.models.data_objects import ImgTypeNames
from APP.CALIBRATION.views.panel_img_media import PanelImgMedia
from APP.CALIBRATION.control.files.names_handler import NamesHandler


class ImageMedia(PanelImgMedia):
    def __init__(self, names_handler: NamesHandler, process_function: FunctionType, list_img_names:List[str]) -> None:
        super().__init__( list_img_names)
        self.names_handler = names_handler
        self.process_function = process_function
        self.back_next_buttons.next.clicked.connect(self.f_button_next)
        self.back_next_buttons.back.clicked.connect(self.f_button_back)
        self.button_remove_img.clicked.connect(self.f_button_remove)
        
    def f_button_next(self):
        self.names_handler.go_next_id()
        self.update_img_data()
    
    def f_button_back(self):
        self.names_handler.go_back_id()
        self.update_img_data()

    def update_img_data(self):
        img_data = self.names_handler.read_last_pair()
        process_img_data = self.process_function(img_data)
        self.update_imgs(process_img_data)

    def f_button_remove(self):
        self.names_handler.delete_index(self.names_handler.actual_id)
        self.f_button_back()
        
#TEST
################################################################################
if __name__=='__main__':
    from APP.CALIBRATION.models.data_objects import ImgData
    from APP.models.basic_config import TEST_IMG_PATH
    from PyQt5.QtWidgets import QApplication
    from APP.control import depth2color
    from APP.models.basic_config import ZMIN, ZMAX
    
    
    def f_test_process(img_data:ImgData):
        return img_data
    names_handler = NamesHandler(TEST_IMG_PATH, rgb_prefix='rgb', depth_prefix='depth')
    app = QApplication(sys.argv)
    window = ImageMedia( names_handler, f_test_process, list_img_names=[ImgTypeNames.rgb, ImgTypeNames.depth, 'test'])
    window.show()
    sys.exit(app.exec())    
    