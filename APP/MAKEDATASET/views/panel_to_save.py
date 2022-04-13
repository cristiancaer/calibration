from PyQt5.QtWidgets import QWidget, QGridLayout
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic import  CustomLineEdit
from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
from APP.MAKEDATASET.views.basic.buttons import BasicButton
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES

        
class PanelToSave(QWidget):
    def __init__(self, type_dataset:str, path: str= '', parent: QWidget= None)->None:
        """panel to show and save rgb-d pair image 

        Args:
            type_dataset (str): to change the buttom-save description
            path (str): to indicate where te images are 
            parent (QWidget, optional): _description_. Defaults to None.
        """
        self.type_datset = type_dataset
        self.save_title = self.get_title_button_save(self.type_datset)
        self.path = path
        super().__init__(parent=parent)
        self.get_title_button_save(type_datset=type_dataset)
        self.init_gui()
        
    def init_gui(self):
        layout = QGridLayout(self)
        self.buttom_new_dataset = BasicButton('New Dataset', 'SP_BrowserReload')
        self.button_save = BasicButton(self.save_title)
        self.line_edit_last_saved = CustomLineEdit(self.path)
        self.panel_rgb_d = PanelRGBDImage()
        layout.addWidget(self.buttom_new_dataset)
        layout.addWidget(self.button_save)
        layout.addWidget(self.line_edit_last_saved)
        layout.addWidget(self.panel_rgb_d)
        
    def get_title_button_save(self, type_datset: str)-> str:
        save_title = ' TakeScreamshot'
        if type_datset == DATASET_TYPES.MILL:
            save_title = 'Save'
        return save_title
    
#Test
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    path = 'test/path/to/images'
    last_saved_name = 'image_test.jpg'
    window = PanelToSave(type_dataset=DATASET_TYPES.MILL)
    window.line_edit_last_saved.update_title(path)
    window.line_edit_last_saved.update_text(last_saved_name)
    window.panel_rgb_d.panel_visualization_range.set_units('100um')
    window.show()
    sys.exit(app.exec_())