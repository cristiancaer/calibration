from typing import Tuple, List
import sys
import cv2
import numpy as np
sys.path.append('./')
from APP.MAKEDATASET.models.draw_objects import Line

class VerticalSegments:
    def __init__(self, line: Line, img_shape: Tuple[int, int], line_thickness: int = 10):
        """convert a vertical line in two segments ( upper and lower) separated by its mid-point


        Args:
            line (Line): this has the extreme points of a vertical line
            img_shape (Tuple[int, int]): this used to draw the line over a dark image( with shape dimensions), and with this image know all the points that belongs to the line
            line_thickness (int): value in pixels, by default the line will be draw  with a width of 10 px
        """
        points = np.sort(line.points, axis=1)  # sort using y_axis. points_shape = (2, 2). each point = [x, y]
        self.init_point = tuple(points[0])
        self.end_point = tuple(points[1])
        self.angle = line.get_angle()
        self.mind_point = tuple(np.int0(points.mean(axis=1)))
        self.img_shape = img_shape
        self.line_thickness = line_thickness

        self.upper_index = self._get_segment_index(self.init_point, self.mind_point)  # list of all points of the upper segment
        self.lower_index = self._get_segment_index(self.mind_point, self.end_point)  # list of all points of the lower segment

    def _get_segment_index(self, inti_point: List[int, int], end_point: List[int, int]) -> np.ndarray:
        black_img = np.zeros((self.img_shape[:2]))
        segment_mask = cv2.line(black_img, inti_point, end_point, (1, 0, 0), self.line_thickness)
        return np.where(segment_mask == 1)
    
