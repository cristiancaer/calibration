import numpy as np
from typing import  Tuple, List
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataToShow, InclinationStatus, DataFromAcquisition, int_array


class DrawDataToShow(DataToShow):
    # colors in BGR
    SQUARE_COLOR = 	(128, 128, 128)# Blue
    ARROW_COLOR = (0, 0, 255)# Read
    PLUS_SIGN_COLOR = (0, 255, 0)# Green
    THICKNESS = 10 # In px
    TIP_LENGTH = 0.3
    ARROW_LENGTH = 0.7 # range min 0, max 1
    Len_CENTERED_LINES = 40
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    FONT_COLOR = (0, 255, 0)
    FONT_SCALE = 0.7
    FONT_LINE = cv2.LINE_AA
    FONT_THICKNESS = 2
    def get_mid_point(self)-> np.ndarray:
        """mid of the images

        Returns:
            np.array: [xc,yc]
        """
        u = self.WIDTH/2
        v = self.HEIGHT/2
        return int_array(u, v)
    
    def get_zip(self, in_rgb: bool= False, in_depth: bool= True)-> zip:
        return zip([in_rgb, in_depth], [self.rgb, self.depth])
    
    def draw_rectangle(self, top_point: List[int], bot_point: List[int], in_rgb: bool= False, in_depth: bool= True):
        """draw a rectangle, usefull to show a ROI

        Args:
            top_point (List[int]): [x, y]
            bot_point (List[int]): [x, y]
            in_rgb (bool, optional):  if True, draw in rgb. Defaults to False.
            in_depth (bool, optional): if True, draw in depth. Defaults to True.
        """
        for flat, img in self.get_zip(in_rgb, in_depth):
            if flat:
                if bot_point[0] <0 :
                    bot_point[0] = self.WIDTH + bot_point[0]
                if bot_point[1] <0 :
                    bot_point[1] = self.HEIGHT + bot_point[1]
                cv2.rectangle(img, top_point, bot_point, self.SQUARE_COLOR, self.THICKNESS) 
    
    def _draw_plus_sign(self, img: np.ndarray, center_point: Tuple[int], line_length: int):
        # vertical line
        init_point = center_point - (0, line_length)
        end_point = center_point + (0, line_length)
        img = cv2.line(img, init_point, end_point, self.PLUS_SIGN_COLOR, self.THICKNESS)
        # horizontal line
        init_point = center_point - (line_length, 0)
        end_point = center_point + (line_length, 0)
        img = cv2.line(img, init_point, end_point, self.PLUS_SIGN_COLOR, self.THICKNESS)
        return img
    
    def _draw_centered_lines(self, img: np.ndarray, vertical: bool, horizontal: bool):
        center_point = self.get_mid_point()
        if vertical:
        # vertical line
            init_point = center_point - (0, self.Len_CENTERED_LINES)
            end_point = center_point + (0, self.Len_CENTERED_LINES)
            img = cv2.line(img, init_point, end_point, self.PLUS_SIGN_COLOR, self.THICKNESS)
        if horizontal:
        # horizontal line
            init_point = center_point - (self.Len_CENTERED_LINES, 0)
            end_point = center_point + (self.Len_CENTERED_LINES, 0)
            img = cv2.line(img, init_point, end_point, self.PLUS_SIGN_COLOR, self.THICKNESS)
        return img
    
    def draw_is_parallel(self, in_vertical: bool, in_horizontal: bool, in_rgb: bool= False, in_depth: bool= True):
        for flat, img in self.get_zip(in_rgb, in_depth):
            if flat:
                self._draw_centered_lines(img, in_vertical, in_horizontal)
    
    def draw_vertical_row(self, topward: bool = True):
        len_arrow = self.ARROW_LENGTH*self.HEIGHT/2
        if  topward:
            len_arrow = - len_arrow
        init_point = self.get_mid_point()
        end_point = init_point +int_array(0, len_arrow)
    
        cv2.arrowedLine(self.depth, init_point, end_point,self.ARROW_COLOR, self.THICKNESS, tipLength = self.TIP_LENGTH) 
    
    def draw_horizontal_row(self, leftward: bool= True):
        len_arrow = self.ARROW_LENGTH*self.WIDTH/2
        if  leftward:
            len_arrow = - len_arrow
        init_point = self.get_mid_point()
        end_point = init_point + int_array(len_arrow, 0)
        cv2.arrowedLine(self.depth,init_point, end_point, self.ARROW_COLOR, self.THICKNESS, tipLength = self.TIP_LENGTH)
    
    def add_text(self,img: np.ndarray, text: str, origin_point: Tuple[int]):
        cv2.putText(img, text, origin_point, self.FONT, self.FONT_SCALE, self.FONT_COLOR, self.FONT_THICKNESS, self.FONT_LINE)
        
    def draw_parallel_information(self, vertical_variation: InclinationStatus, horizontal_variation : InclinationStatus):
        if not horizontal_variation.is_parallel:
            self.draw_horizontal_row(horizontal_variation.is_positive)
        
        if not vertical_variation.is_parallel:
            self.draw_vertical_row(vertical_variation.is_positive)
            
        
        self.draw_is_parallel(vertical_variation.is_parallel, horizontal_variation.is_parallel)
        
        text = f'eX: {int(horizontal_variation.value)} ; eY: {int(vertical_variation.value)}'
        origin = (40,40)
        self.add_text(self.rgb, text, origin)
    
#TEST
################################################################################

if __name__=='__main__':
    from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
    from PyQt5.QtWidgets import QApplication
    img_test = np.zeros( (400, 400, 3))
    depth =  np.arange(0, 320000, 2 , dtype= int).reshape(400, 400)
    data_to_show = DrawDataToShow(DataFromAcquisition(rgb=img_test, depth=depth))
    thr = 2
    y_var = InclinationStatus(thr, -80) #  top inclination
    x_var = InclinationStatus(thr, -8)# right inclination
    data_to_show.draw_parallel_information(y_var, x_var)
    data_to_show.draw_rectangle(top_point=[10, 50], bot_point=[-200, 200])
    data_to_show.draw_is_parallel(in_vertical=True, in_horizontal=True)
    app = QApplication(sys.argv)
    window = PanelRGBDImage()
    window.panel_visualization_range.set_units('100 um')
    window.update_rgbd(data_to_show)
    window.show()
    sys.exit(app.exec_())
