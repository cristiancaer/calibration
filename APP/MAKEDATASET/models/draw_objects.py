import numpy as np
from typing import Tuple, List


class PointsStore:
    def __init__(self, n: int) -> None:
        """ class to store  n number of points. the points will be like point = [x, y]

        it has a function to store a point at a time.

        is_full will be True when all positions have been used
        Args:
            n (int): number of max points to store
        """
        self.points_number = n
        self.clear()

    def clear(self):
        """erase all points stored return the object to its initial status and 
        """
        self.points = np.zeros((self.points_number, 2), dtype=int)
        self.last_index = 0
        self.is_full = False

    def add_point(self, x: int, y: int):
        if not self.is_full:
            self.points[self.last_index] = np.array([x, y], dtype=int)
            self.last_index += 1

        self.is_full = self.last_index == self.points_number


class Line(PointsStore):
    def __init__(self) -> None:
        super().__init__(2)

    def get_angle(self) -> float:
        """get angle with respect to x-axis

        Returns:
            float: angle in degrees
        """
        # point = [x,y]
        delta = self.points[1] -self.points[0]
        delta = delta.astype(float)
        if delta[0] == 0:
            delta[0] = 1E-9
        
        angle = np.arctan(delta[1]/delta[0])# radians
        return angle*180/np.pi # degrees