from typing import Tuple
import numpy as np

class ThroughSquare:

    def __init__(self, top_point: Tuple[int], buttom_point: Tuple[int], width: int, threshold: float) -> None:
        """
            To check how much camera-axis (Y and X) are parallel to a flat surface
    
            To avoid X axis influence over Y axis, each column has its minimun value subtracted from it
            
            To avoid Y axis influence over X axis, each row has its minimun value subtracted from it
            
            With 2 points, top_point and bottom_point, will have in mind a square with a  given Width_line
            
            check axis X variation: given mean_lef and mean_right the mean value of the each vertcal line of the square, then x variation, delta_x = mean_lef - mean_right
            
            if |delta_x| > Threshold there will be an inclnation.   delta_x > 0 leftward inclination, delta_x< 0 rightward inclination
            
            check axis Y variation: the same as X but with the horizontal line of the square. delta_y = mean_top -mean_bottom
            
            if |delta_y| > Threshold there will be an inclnation.   delta_y > 0 topward inclination, delta_y< 0 bottomward inclination
            
            

        Args:
            top_point (Tuple[int]): left-top point of the cosidered square
            buttom_point (Tuple[int]): right-bottom point of the cosidered square
            width (int): square width line
            threshold (float): thread to consider where there are an inclination
        """
        self.top_point = top_point
        self.buttom_point = buttom_point
        self.width = width
        self.treshold = threshold
    
    def check(self, depth_image: np.ndarray):
        
        # avoid X axis influence over Y axis. normal_y,  each column has its minimun value subtracted from it
        normal_y = depth_image.copy()- depth_image.mean(axis=0)
        # avoid Y axis influence over X axis. normal_x,  each row has its minimun value subtracted from it
        normal_x = depth_image.copy()- depth_image.mean(axis=1)
        