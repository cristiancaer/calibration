from typing import List
from PyQt5.QtWidgets import QWidget, QApplication
from threading import Lock
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.panel_to_save import PanelToSave
from APP.MAKEDATASET.control.stream_source.test import ImageGenerator
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455
from APP.MAKEDATASET.control.save_pair_images import SaveHandler
from APP.MAKEDATASET.control.check_parallel.through_square import ThroughSquare
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES, DataFromAcquisition, DataToSave
from APP.MAKEDATASET.views.draw_tools.draw_over_data_to_show import DrawDataToShow
from APP.MAKEDATASET.control.stream_source.stream_handler import StreamHandler
from APP.MAKEDATASET.control.loop_event_manager import LoopEventManager
from APP.MAKEDATASET.models import TEST_PATH

class SaveCheckingParallel(PanelToSave):
    name = "save"
    def __init__(self,stream_handler: StreamHandler, save_handler:SaveHandler, lock_visualization: Lock = None, type_dataset:str = None, path: str= '', top_point: List[int]= None, bottom_point: List[int]= None, parent: QWidget=None):
        """app to save images checking that the flat surface is parallel to the camera

        Args:
            stream_handler (ThreadToStream, optional): ThreadToStream from where the images are produce. Defaults to None.
            type_dataset (str, optional): check DATASET_TYPES, if dataset_type = 'At Mill' check parallel is disable . Defaults to None.
            path (str, optional): additional info, to indicate where the images are saving. Defaults to ''.
            top_point, bottom (List[int], optional): together with bottom_point are used to form a rectangle ROI. Defaults to None.
            parent (QWidget, optional): _description_. Defaults to None.
        """
        self.stream_handler = stream_handler
        self.save_handler = save_handler
        self.is_saving  = False
        if lock_visualization is not  None:
            self.lock_visualization = lock_visualization
        else:
            self.lock_visualization = Lock()
        super().__init__(parent = parent)
        self.setup(top_point, bottom_point)
        self.update_save_info(type_dataset, path)
    

    def init_gui(self):
        super().init_gui()
        self.buttom_new_dataset.clicked.connect(self.new_dataset)
        self.panel_rgb_d.set_dark_images()
        # self.showMaximized()
        
    def setup(self, top_point: List[int], bottom_point:List[int]):
        # stream config
        self.connect_stream()
        # reload stream
        self.panel_rgb_d.button_reconnect_stream.clicked.connect(self.stream_handler.set_stream)
        
        # save config
        
        self.button_save.clicked.connect(self.change_status_saving)
        self.save_handler.last_index.connect(self.line_edit_last_saved.update_text)
        
        # check config
        self.update_parallel_checking(top_point, bottom_point)
        # check threshold
        
    def update_parallel_checking(self, top_point: List[int], bottom_point: List[int]):
        """
        Args:
            top_point , bottom_point(List[int]): this points are used to form a Roi in the images
        
        """
        self.check_parallel = ThroughSquare(top_point=top_point, bottom_point= bottom_point, threshold=20, line_width= 15)
         
    def update_save_info(self, dataset_type:str , path: str):
        """ update visualization info of the saving process"""
        self.dataset_type = dataset_type
        self.save_handler.set_path(path)
        self.line_edit_last_saved.update_title(path)
        if dataset_type == DATASET_TYPES.MILL:
            self.save_handler.set_index_type(datetime_index=True)
        self.update_button_save(dataset_type)

    def update_stream_info(self):
        """ update visualization info of the stream process"""
        if hasattr(self.stream_handler.actual_stream,'depth_units'):
            self.panel_rgb_d.panel_visualization_range.set_units(self.stream_handler.actual_stream.depth_units)
    
    def process_images(self, data:DataFromAcquisition)->None:
        """ slot to stream_handler.data_ready"""
        zmin, zmax = self.panel_rgb_d.panel_visualization_range.get_range() 
        data_to_show = DrawDataToShow(data, zmin, zmax)
        if  self.dataset_type != DATASET_TYPES.MILL:
            y_status, x_status = self.check_parallel.check(data.depth)
            data_to_show.draw_parallel_information(y_status, x_status)
            data_to_show.draw_rectangle(self.check_parallel.top_point[::-1], self.check_parallel.bottom_point[::-1])# original are in array index reference [row, column]. draw has [x,y] index reference
        with self.lock_visualization:
            self.panel_rgb_d.update_rgbd(data_to_show)
    
    def save_images(self, data:DataFromAcquisition)->None:
        """ slot to stream_handler.data_ready"""
        data_to_save = DataToSave(data)
        if self.is_saving:
            self.save_handler.add_new(data_to_save)
        
        if self.dataset_type != DATASET_TYPES.MILL:
            self.is_saving = False
    
    def change_status_saving(self):
        self.is_saving = not self.is_saving
        self.button_save.set_pressed(self.is_saving)
    
    def new_dataset(self):
        self.is_saving = False
        self.panel_rgb_d.set_dark_images()
        if hasattr(self, 'function_to_going'):
            self.function_to_going()
        
    def set_function_to_going(self, function_to_going):
        self.function_to_going =  function_to_going
        
    def connect_stream(self):
        self.stream_handler.data_ready.connect(self.process_images)
        self.stream_handler.data_ready.connect(self.save_images)
        
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
    event_manager = LoopEventManager('event_manger')
    event_manager.start()
    stream_handler = StreamHandler(event_manager)
    save_handler = SaveHandler(event_manager)
    stream = ImageGenerator()
    stream_handler.add_stream(stream)
    stream_handler.update_available_streams()
    stream_handler.set_stream(stream.name)
    app = QApplication(sys.argv)
    window = SaveCheckingParallel(stream_handler,save_handler,None,DATASET_TYPES.MILL, TEST_PATH,[100,100],[-100,-100] )# Test with area
    window.show()
    app.exec_()
    event_manager.stop()
    sys.exit()
    