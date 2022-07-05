from typing import Tuple
import numpy as np
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import InclinationStatus


class ThroughSquare:

    def __init__(self, top_point: Tuple[int], bottom_point: Tuple[int], line_width: int, threshold: float) -> None:
        """
            To check how much camera-axis (Y and X) are parallel to a flat surface
    
            To avoid X axis influence over Y axis, each column has its minimum value subtracted from it
            
            To avoid Y axis influence over X axis, each row has its minimum value subtracted from it
            
            With 2 points, top_point and bottom_point, will have in mind a square with a  given line_width_line
            
            check axis-X variation: given mean_lef and mean_right the mean value of the each vertical line of the square, then x variation, variation_x =   mean_right  -mean_lef
            
            if |variation_x| > Threshold there will be an inclination.   variation_x > 0 leftward inclination, variation_x< 0 rightward inclination
            
            check axis Y variation: the same as X but with the horizontal line of the square. variation_y = mean_top -mean_bottom
            
            if |variation_y| > Threshold there will be an inclination.   variation_y > 0 upward inclination, variation_y< 0 downward inclination
            
            EG.
            
            | 1 2 3 |
            
            | 4 5 6 |
            
            | 7 8 9 |
            
            use normal-Y to know Y variation. subtract the minimum value of each column
            
            | 0 0 0 |
            
            | 3 3 3 | -> variation = -3, ( mean of the top and bot lines(rows))
            
            | 6 6 6 |
            
            use normal-X to know X variation. Subtract the minimum value of each row
            
            | 0 1 2 |
            
            | 0 1 2 | -> variation = 1 ( mean of the lef and right lines(columns))
            
            | 0 1 2 |
            

        Args:
            top_point (Tuple[int]): left-top point of the considered square, array index reference. [row,column]
            bottom_point (Tuple[int]): right-bottom point of the considered square. [row, column]
            line_width (int): square width line
            threshold (float): thread to consider where there are an inclination
        """
        self.top_point = top_point
        self.bottom_point = bottom_point
        self.line_width = line_width
        self.threshold = threshold
    
    def check(self, depth_image: np.ndarray)-> Tuple[InclinationStatus]:
        """check if camera is parallel  to a flat surface
        the found variation is the total variation between the sides of the square. this is
        different from the delta variation, variation between columns of rows 

        Args:
            depth_image (np.ndarray): one chanel  depth image

        Returns:
            Tuple[InclinationStatus]: object to indicate inclination status.
        """
        # avoid X axis influence over Y axis. normal_y,  each column has its minimum value subtracted from it
        normal_y = depth_image.copy()- depth_image.min(axis=0)
        # avoid Y axis influence over X axis. normal_x,  each row has its minimum value subtracted from it
        normal_x = depth_image.copy()- depth_image.min(axis=1).reshape(-1, 1)# -  column vector
        # use vertical lines to get x variation
        left_vertical = normal_x[ : , self.top_point[1]:self.top_point[1]+self.line_width]
        # use - self.with to use the information inside of the square form through the top an bot points. 
        right_vertical = normal_x[ : , self.bottom_point[1]-self.line_width:self.bottom_point[1]]
        x_variation = right_vertical.mean() - left_vertical.mean()
        x_inclination = InclinationStatus(self.threshold, x_variation)
        # use horizontal lines to get y variation
        top_horizontal = normal_y[self.top_point[0]: self.top_point[0]+self.line_width]
        bot_horizontal = normal_y[self.bottom_point[0]-self.line_width: self.bottom_point[0]]
        y_variation = top_horizontal.mean()- bot_horizontal.mean()
        y_inclination = InclinationStatus( self.threshold, y_variation)
        return y_inclination, x_inclination
        

#TEST
################################################################################

if __name__=='__main__':
    from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
    from APP.MAKEDATASET.views.draw_tools.draw_over_data_to_show import DrawDataToShow
    from APP.MAKEDATASET.models.data_objects import DataFromAcquisition
    from PyQt5.QtWidgets import QApplication
    # images
    rgb = np.zeros( (400, 400, 3))
    depth = np.arange(0, 160000, 1, dtype=int).reshape(400,400)
    data_to_show = DrawDataToShow(DataFromAcquisition(rgb=rgb, depth=depth))
    # roi
    top_point = [50, 40]
    bot_point = [-15, -15]
    line_width = 15
    # thread consider in inclination
    thr = 200
    check_parallel = ThroughSquare(top_point, bot_point, line_width, thr)
    # show inclination status
    y_var, x_var = check_parallel.check(depth) #  top inclination
    print(y_var.value,x_var.value)
    data_to_show.draw_rectangle(top_point, bot_point)
    data_to_show.draw_parallel_information(y_var, x_var)
    app = QApplication(sys.argv)
    window = PanelRGBDImage()
    window.update_rgbd(data_to_show)
    window.show()
    sys.exit(app.exec_())
        