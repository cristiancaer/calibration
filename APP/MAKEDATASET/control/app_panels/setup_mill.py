from time import sleep
from typing import List
from PyQt5.QtWidgets import QWidget, QApplication, QGroupBox, QHBoxLayout
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.control.stream_source.thread_stream import ThreadToStream
from APP.MAKEDATASET.control.stream_source.test import ImageGenerator
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455
from APP.MAKEDATASET.control.check_parallel.through_plane import ThroughPlane
from APP.MAKEDATASET.views.panel_mill_setup import PanelMillSetup
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToSave
from APP.MAKEDATASET.views.draw_tools.draw_over_data_to_show import DrawDataToShow
from APP.MAKEDATASET.models.draw_objects import PointsStore, LineStore


class PanelSetupMill(PanelMillSetup):
    def __init__(self, stream_handler: ThreadToStream,parent= None)->None:
        self.stream_handler = stream_handler
        super().__init__(parent)
        self.setup()
    
    def setup(self):
         # stream config
        self.stream_handler.data_ready.connect(self.process_images)
        self.button_screenshot.clicked.connect(self.take_screenshot)
        # reload stream
        self.button_reconnect_stream.clicked.connect(self.stream_handler.set_stream)
        
        #check parallel config
        ################################################################################
        self.left_line = LineStore()
        self.button_left_line.clicked.connect(self.f_button_left_line)
        
        self.right_line = LineStore()
        self.button_right_line.clicked.connect(self.f_button_right_line)
        
        # update angle info when lines are full
        self.panel_rgb.canvas.last_store_full.connect(self.update_info_at_full)
        
        self.list_polygons: List[PointsStore] = []
        self.button_add_polygon.clicked.connect(self.f_button_add_polygon)
        
        self.check_parallel = ThroughPlane(threshold=20)
        self.button_get_inclination.clicked.connect(self.process_screenshot)
    
    def process_images(self, data:DataFromAcquisition) -> None:
        """
        Args:
            data (DataFromAcquisition): Generated data in ThreadToStream
        """
        zmin, zmax = self.panel_visualization_range.get_range() 
        data_to_show = DrawDataToShow(data, zmin, zmax)
        if self.left_line.is_full:
            data_to_show.draw_line_over(self.left_line.points, in_rgb=True)
        if self.right_line.is_full:
            data_to_show.draw_line_over(self.right_line.points, in_rgb= True)
            
        self.update_rgbd(data_to_show)
        self.last_data = data
    
    def process_screenshot(self):
        self.button_get_inclination.setEnabled(False)
        if self.list_polygons[-1].is_full:
            y_status, x_status, depth_model_img = self.check_parallel.check(self.last_data.depth, self.list_polygons)
            last_data = self.last_data.copy()
            last_data.depth = depth_model_img
            zmin, zmax = self.panel_visualization_range.get_range() 
            data_to_show = DrawDataToShow(last_data, zmin, zmax)
            data_to_show.draw_parallel_information(y_status, x_status)
        
        self.update_rgbd(data_to_show)
        self.list_polygons = []
        
    
    def take_screenshot(self):
        status = not self.button_screenshot.status
        self.button_screenshot.status = status
        self.stream_handler.set_stop(status)
        self.button_screenshot.set_pressed(status)
        self.button_add_polygon.setEnabled(status)
        self.button_left_line.setEnabled(not status)
        self.button_right_line.setEnabled(not status)
        if not status:
            self.button_get_inclination.setEnabled(False)
            self.list_polygons = []
            self.button_add_polygon.set_pressed(False)
        sleep(0.01)

    
    def update_info_at_full(self):
        if self.left_line.is_full:
            self.label_left_angle.update_text(f'{self.left_line.get_angle():.2f}')
            self.button_left_line.set_pressed(False)#
        
        if self.right_line.is_full:
            self.label_right_angle.update_text(f'{self.right_line.get_angle():.2f}')
            self.button_right_line.set_pressed(False)#
        
        if self.list_polygons:
            if self.list_polygons[-1].is_full:
                self.button_add_polygon.set_pressed(False)
                self.button_get_inclination.setEnabled(True)
                zmin, zmax = self.panel_visualization_range.get_range() 
                data_to_show = DrawDataToShow(self.last_data, zmin, zmax)
                for polygon in self.list_polygons:
                    data_to_show.draw_polygon_over(polygon.points, in_rgb=True)
                self.update_rgbd(data_to_show)
        
        if not self.button_screenshot.status:
            self.button_left_line.setEnabled(True)
            self.button_right_line.setEnabled(True)
            
    def f_button_left_line(self):
        self.left_line.clear()
        self.panel_rgb.canvas.add_element_to_store(self.left_line)
        self.button_left_line.set_pressed(True)
        self.button_right_line.setEnabled(False)
        self.button_add_polygon.setEnabled(False)
    
    def f_button_right_line(self):
        self.right_line.clear()
        self.panel_rgb.canvas.add_element_to_store(self.right_line)
        self.button_right_line.set_pressed(True)
        self.button_left_line.setEnabled(False)
        self.button_add_polygon.setEnabled(False)
        
    def f_button_add_polygon(self):
        
        if self.list_polygons:
            if not self.list_polygons[-1].is_full:
                return None
        new_polygon = PointsStore(5)
        self.list_polygons.append(new_polygon)
        self.panel_rgb.canvas.add_element_to_store(new_polygon)
        self.button_add_polygon.set_pressed(True)
        self.button_left_line.setEnabled(False)
        self.button_right_line.setEnabled(False)
        
        
        
#TEST
################################################################################
if __name__=='__main__':
    stream_handler = ThreadToStream()
    stream_class = ImageGenerator()
    stream_handler.add_stream(stream_class)
    stream_handler.start()
    stream_handler.update_availables()
    stream_handler.set_stream(stream_class.name)
    app = QApplication(sys.argv)
    window = PanelSetupMill(stream_handler)
    window.show()
    sys.exit(app.exec())