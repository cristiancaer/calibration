import sys
sys.path.append('./')
from APP.MAKEDATASET.views.panel_datset_type import PanelDatasetType
from APP.MAKEDATASET.views.panel_choose_path import PanelChoosePath
from APP.MAKEDATASET.views.panel_select_camera import PanelSelectCamera
from APP.MAKEDATASET.views.stack import StackWidget

    
class PanelBasicConfig(StackWidget):
    name = 'basic_configuration'
    function_to_going = None
    def __init__(self, parent = None)->None:
        super().__init__(parent)
        self.init_gui()
        self.setup()
        
    def init_gui(self):
        self.panel_dataset_type = PanelDatasetType()
        self.add_panel(self.panel_dataset_type)
        self.panel_choose_path = PanelChoosePath()
        self.add_panel(self.panel_choose_path)
        self.panel_select_camera = PanelSelectCamera()
        self.add_panel(self.panel_select_camera)

        # panelDatasetType
        self.panel_dataset_type.back_next_buttons.next.clicked.connect(lambda: self.go_to_panel(self.panel_choose_path))
        # PanelChoosePath
        self.panel_choose_path.back_next_buttons.next.clicked.connect(lambda: self.go_to_panel(self.panel_select_camera))
        self.panel_select_camera.back_next_buttons.next.clicked.connect(self.final_next)
        
    
    def set_function_to_going(self, function_to_going):
        self.function_to_going =  function_to_going
    
    def final_next(self):
        if self.function_to_going is not None:
            self.function_to_going()
#TEST
################################################################################
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PanelBasicConfig()
    window.show()
    sys.exit(app.exec_())