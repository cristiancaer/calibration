from PyQt5.QtWidgets import  QWidget
import sys
from threading import Lock
sys.path.append('./')
from APP.MAKEDATASET.control.loop_event_manager import LoopEventManager
from APP.MAKEDATASET.views.panel_basic_config import PanelBasicConfig
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455
from APP.MAKEDATASET.control.stream_source.orbbec import Orbbec
from APP.MAKEDATASET.control.stream_source.test import ImageGenerator
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES, DatasetTypes
from APP.views.basic.stack import StackWidget
from APP.MAKEDATASET.control.app_panels.setup_mill import MillSetup
from APP.MAKEDATASET.control.app_panels.save_checking_parallel import SaveCheckingParallel
from APP.MAKEDATASET.control.loop_event_manager.futures_event_manager import FuturesLoopEventManager
from APP.MAKEDATASET.control.stream_source.stream_handler import StreamHandler
from APP.MAKEDATASET.control.save_pair_images import SaveHandler


class MakeDataset(StackWidget):
    def __init__(self, event_manager: LoopEventManager, window_name = '', parent: QWidget=None):
        self.lock_visualization = Lock()
        self.stream_handler = StreamHandler(event_manager)
        self.save_handler = SaveHandler(event_manager)
        self.window_name = window_name
        super().__init__(parent)
        self.init_gui()
        self.setup()
        
    def init_gui(self):
        self.setWindowTitle(self.window_name)
        self.panel_stack_basic_config = PanelBasicConfig()
        self.add_panel(self.panel_stack_basic_config)
        self.pane_setup_mill = MillSetup(self.stream_handler, self.lock_visualization)
        # by default if the stream data is ready start to show in panel. this avoid update the image visualization
        self.add_panel(self.pane_setup_mill)
        self.panel_save = SaveCheckingParallel(self.stream_handler, self.save_handler, self.lock_visualization,top_point=[100,100], bottom_point=[-100,-100])
        self.add_panel(self.panel_save)
        print(f'id panel save :{id(self.panel_save)}')
        # self.showMaximized()
        
    def setup(self):
        # stream config
        self.stream_handler.add_stream(Intel455())
        self.stream_handler.add_stream(Orbbec())
        self.stream_handler.add_stream(ImageGenerator())
   
        # update available streams
        # self.update_available_streams()
        self.panel_stack_basic_config.panel_select_camera.button_update_streams.clicked.connect(self.update_available_streams)
        # go at click in last next button in basic config
        self.panel_stack_basic_config.set_function_to_going(self.f_button_next_from_basic_config)
        # go at click in next button mill setup
        self.pane_setup_mill.set_function_to_going(self.at_going_to_pane_save)
        # go at click in new dataset button
        self.panel_save.set_function_to_going(self.f_button_new_dataset)
        # connect back buttons
        super().setup()
        
    def update_available_streams(self):
        self.panel_stack_basic_config.panel_select_camera.update_available_streams(self.stream_handler.get_available_stream_names())
        
    def set_stream(self):
        stream_name = self.panel_stack_basic_config.panel_select_camera.get_selected()
        self.stream_handler.set_stream(stream_name)
        
    
    def f_button_next_from_basic_config(self):
        for panel in self.list_panels:
            print(panel.name, id(panel))
        self.set_stream()
        if self.panel_stack_basic_config.panel_dataset_type.get_selected()==DatasetTypes.MILL:
            self.at_going_to_setup_mill()
        else:
            self.at_going_to_pane_save()  
        
    def f_button_new_dataset(self):
        self.stream_handler.disconnect_data_ready_slots()
        self.panel_stack_basic_config.go_to_panel(self.panel_stack_basic_config.panel_dataset_type)
        self.go_to_panel(self.panel_stack_basic_config)
        
        
    def at_going_to_setup_mill(self):
        self.go_to_panel(self.pane_setup_mill)
        self.stream_handler.disconnect_data_ready_slots()# this will disconnect all slots connected to data_ready signal
        self.pane_setup_mill.connect_stream()
        
    def at_going_to_pane_save(self):
        self.go_to_panel(self.panel_save)
        self.stream_handler.disconnect_data_ready_slots()# this will disconnect all slots connected to data_ready signal
        self.panel_save.connect_stream()
        dataset_type = self.panel_stack_basic_config.panel_dataset_type.get_selected()
        path = self.panel_stack_basic_config.panel_choose_path.path
        self.panel_save.update_save_info(dataset_type, path)
        self.panel_save.update_stream_info()
   
    def closeEvent(self, event) -> None:
        self.stream_handler.close()
        self.save_handler.close()
        return super().closeEvent(event)
    
    def resizeEvent(self, event):
        with self.lock_visualization:
            super().resizeEvent(event)

    def moveEvent(self, event):
        with self.lock_visualization:
            super().moveEvent(event)

    def paintEvent(self, event) -> None:
        with self.lock_visualization:
            super().paintEvent(event)
    
#TEST
################################################################################
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    event_manager = FuturesLoopEventManager('event_manager')
    event_manager.start()
    app = QApplication(sys.argv)
    window = MakeDataset(event_manager, 'Make Dataset')
    window.panel_save.update_parallel_checking(top_point=[100,100], bottom_point=[-100,-100])#checking trough square
    window.show()
    app.exec_()
    event_manager.stop()
    sys.exit()