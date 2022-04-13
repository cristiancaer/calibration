from ast import arg
from tkinter import Widget
from typing import List
from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.panel_datset_type import PanelDatasetType
from APP.MAKEDATASET.views.panel_choose_path import PanelChoosePath
from APP.MAKEDATASET.views.panel_select_camera import PanelSelectCamera
from APP.MAKEDATASET.views.panel_to_save import PanelToSave


class Integration(QWidget):
    name = 'integration'
    
    def __init__(self, parent: QWidget= None):
        """panel that  consider all panels availables like pages. the page change is through  back and next buttons

        Args:
            parent (QWidget, optional): _description_. Defaults to None.
        """
        super().__init__(parent=parent)
        self.list_panels: List[str] = []
        self.init_gui()
    
    def init_gui(self):
        layout = QGridLayout(self)
        self.stack = QStackedWidget ()
        layout.addWidget(self.stack)
        self.panel_dataset_type = PanelDatasetType()
        self.add_panel(self.panel_dataset_type)
        self.panel_choose_path = PanelChoosePath()
        self.add_panel(self.panel_choose_path)
        self.panel_select_camera = PanelSelectCamera()
        self.add_panel(self.panel_select_camera)
        self.panel_to_save = PanelToSave()
        self.add_panel(self.panel_to_save)
        
        
    def add_panel(self, panel: QWidget):
        self.list_panels.append(panel.name)
        self.stack.addWidget(panel)
    
    def go_to_panel(self, panel: QWidget):
        self.update_info_at_change_panel()
        index = self.list_panels.index(panel.name)
        self.stack.setCurrentIndex(index)
    
    def update_info_at_change_panel(self):
        pass
        
#test
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = Integration()
    window.panel_dataset_type.back_next_buttons.next.clicked.connect(lambda : window.go_to_panel(window.panel_choose_path))
    window.panel_choose_path.back_next_buttons.next.clicked.connect(lambda : window.go_to_panel(window.panel_select_camera))
    window.panel_select_camera.back_next_buttons.next.clicked.connect(lambda : window.go_to_panel(window.panel_to_save))
    window.show()
    sys.exit(app.exec_())