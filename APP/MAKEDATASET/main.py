from PyQt5.QtWidgets import QMainWindow, QWidget
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.integration import Integration
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455
from APP.MAKEDATASET.control.stream_source.orbbec import Orbbec
from APP.MAKEDATASET.control.stream_source.thread_stream import ThreadToStream
from APP.MAKEDATASET.control.save_pair_images import ThreadToSave
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES, DataToSave, DataFromAcquisition, DatasetTypes
from APP.MAKEDATASET.views.draw_tools.draw_over_data_to_show import DrawDataToShow
from APP.MAKEDATASET.control.check_parallel.through_square import ThroughSquare

class MainWindow(QMainWindow):
    def __init__(self, window_name = '', stream_handler: ThreadToStream= None, parent: QWidget=None):
        self.stream_handler = stream_handler
        super().__init__(parent)
        self.window_name = window_name
        self.init_gui()
        self.setup()
        
    def init_gui(self):
        self.setWindowTitle(self.window_name)
        self.panels = Integration()
        self.setCentralWidget(self.panels)
        self.panels.panel_to_save.buttom_new_dataset.clicked.connect(self.new_dataset)
        self.panels.panel_to_save.panel_rgb_d.set_dark_images()
        # self.showMaximized()
        
    def setup(self):
        # stream config
        
        self.stream_handler.add_stream(Intel455())
        self.stream_handler.add_stream(Orbbec())
        self.stream_handler.start()
        self.stream_handler.data_ready.connect(self.process_images)
        self.stream_handler.data_ready.connect(self.save_images)
        self.update_available_streams()
        self.panels.panel_select_camera.button_update_streams.clicked.connect(self.update_available_streams)
        # self.panels.panel_select_camera.combobox_cameras.currentTextChanged.connect(self.set_stream)
        self.panels.panel_to_save.panel_rgb_d.button_reconnect_stream.clicked.connect(self.set_stream)
        
        # save config
        self.save_handler = ThreadToSave()
        self.save_handler.start()
        self.is_saving = False
        self.panels.panel_choose_path.back_next_buttons.next.clicked.connect(self.update_save_info)
        self.panels.panel_to_save.button_save.clicked.connect(self.change_status_saving)
        self.save_handler.last_index.connect(self.panels.panel_to_save.line_edit_last_saved.update_text)
        
        # check config
        self.check_parallel = ThroughSquare(top_point=[100,100], bottom_point=[-100,-100], threshold=10, line_width= 15)
        
    def update_save_info(self):
        path = self.panels.panel_choose_path.path
        self.save_handler.set_path(path)
        self.panels.panel_to_save.line_edit_last_saved.update_title(path)
        if self.panels.dataset_type == DATASET_TYPES.MILL:
            self.save_handler.set_index_type(datatime_index=True)
        
    def update_available_streams(self):
        self.panels.panel_select_camera.update_available_streams(self.stream_handler.get_available_stream_names())

    def set_stream(self):
        stream_name = self.panels.panel_select_camera.get_selected()
        self.stream_handler.set_stream(stream_name)
        if hasattr(self.stream_handler.actual_stream,'depth_units'):
            self.panels.panel_to_save.panel_rgb_d.panel_visualization_range.set_units(self.stream_handler.actual_stream.depth_units)
    
    def process_images(self, data:DataFromAcquisition)->None:
        dataset_type = self.panels.panel_dataset_type.get_selected()
        zmin, zmax = self.panels.panel_to_save.panel_rgb_d.panel_visualization_range.get_range() 
        data_to_show = DrawDataToShow(data, zmin, zmax)
        if dataset_type == DATASET_TYPES.AREA_CALIBRATION or dataset_type == DATASET_TYPES.Z_CALIBRATION:
            y_status, x_status = self.check_parallel.check(data.depth)
            data_to_show.draw_parallel_information(y_status, x_status)
            data_to_show.draw_rectangle(self.check_parallel.top_point[::-1], self.check_parallel.bottom_point[::-1])# original are in array index reference [row, column]. draw has [x,y] index reference
        self.panels.panel_to_save.panel_rgb_d.update_rgbd(data_to_show)
    
    def save_images(self, data:DataFromAcquisition)->None:
        data_to_save = DataToSave(data)
        if self.is_saving:
            self.save_handler.add_new(data_to_save)
        dataset_type = self.panels.panel_dataset_type.get_selected()
        if dataset_type != DATASET_TYPES.MILL:
            self.is_saving = False
    
    def change_status_saving(self):
        self.is_saving = not self.is_saving
    
    def new_dataset(self):
        self.stream_handler.reset_stream()
        self.panels.panel_to_save.panel_rgb_d.set_dark_images()
        self.panels.go_to_panel(self.panels.panel_dataset_type)
        # clear displayed path
        self.panels.panel_choose_path.back_next_buttons.next.setEnabled(False)
        self.panels.panel_choose_path.button_path.set_text('')
        
    def closeEvent(self, event) -> None:
        self.stream_handler.close()
        self.save_handler.close()
        return super().closeEvent(event)
    

#TEST
################################################################################
if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    stream_handler = ThreadToStream()
    app = QApplication(sys.argv)
    window = MainWindow('Make Dataset', stream_handler)
    window.show()
    sys.exit(app.exec_())