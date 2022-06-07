from PyQt5.QtWidgets import QWidget, QGridLayout
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic import  CustomLineEdit
from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
from APP.MAKEDATASET.views.basic.buttons import BasicButton
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES

        
class PanelToSave(QWidget):
    name = 'save'
    
    def __init__(self, type_dataset:str = None, path: str= '', parent: QWidget= None)->None:
        """panel to show and save rgb-d pair image 

        Args:
            type_dataset (str): to change the buttom-save description
            path (str): to indicate where te images are 
            parent (QWidget, optional): _description_. Defaults to None.
        """
        self.path = path
        self.status_save = False
        super().__init__(parent=parent)
        self.init_gui()
        if type_dataset:
            self.update_button_save(type_dataset)
        
    def init_gui(self):
        layout = QGridLayout(self)
        self.buttom_new_dataset = BasicButton('New Dataset', 'SP_BrowserReload')
        self.button_save = BasicButton('')
        self.line_edit_last_saved = CustomLineEdit(self.path)
        self.panel_rgb_d = PanelRGBDImage()
        layout.addWidget(self.buttom_new_dataset)
        layout.addWidget(self.button_save)
        layout.addWidget(self.line_edit_last_saved)
        layout.addWidget(self.panel_rgb_d)
        self.normal_style = self.button_save.style()
        
    def update_button_save(self, type_datset: str)-> str:
        save_title = ' TakeScreamshot'
        if type_datset == DATASET_TYPES.MILL:
            save_title = 'Save'
            
        self.button_save.setText(save_title)
        
    def change_status_save(self):
        self.status_save = not self.status_save
    
#Test
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    path = 'test/path/to/images'
    last_saved_name = 'image_test.jpg'
    window = PanelToSave(type_dataset=DATASET_TYPES.Z_CALIBRATION)
    window.line_edit_last_saved.update_title(path)
    window.line_edit_last_saved.update_text(last_saved_name)
    window.panel_rgb_d.panel_visualization_range.set_units('100um')
    window.button_save.clicked.connect(window.change_status_save)
    window.show()
    sys.exit(app.exec_())