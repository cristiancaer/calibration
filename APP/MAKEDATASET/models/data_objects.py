from genericpath import getsize
from textwrap import indent
from typing import Dict, List, Tuple
import numpy as np
import cv2
from datetime import datetime
import sys
sys.path.append('./')
from APP.MAKEDATASET.views import depth2color
from APP.MAKEDATASET.models import HOUR_FORMAT, RGB_PREFIX, DEPTH_PREFIX, ZMAX, ZMIN


class DataFromAcquisition:
    """ To store de data produce in acquisition 
    """

    def __init__(self, rgb: np.ndarray, depth: np.ndarray) -> None:
        self.rgb = rgb
        self.depth = depth
        self.hour = datetime.now()


class DataToSave:
    def __init__(self, data_acquisition: DataFromAcquisition, rgb: bool = True, depth: bool = True):
        self.data: Dict[str, np.ndarray] = {}
        if rgb:
            self.add_img(RGB_PREFIX, data_acquisition.rgb)
        if depth:
            self.add_img(DEPTH_PREFIX, data_acquisition.depth)
        self.hour = data_acquisition.hour.strftime(HOUR_FORMAT)

    def add_img(self, name: str, img: np.ndarray):
        if isinstance(img, np.ndarray):
            self.data.update({name: img})

class InclinationStatus:
    def __init__(self,threshold: float, inclination_value: float)->None:
        """
        used in parallel checking

        Args:
            thread (float): if |inclination_value|< Thread, we'll consider that the surface is parallel to the camera
            inclination_value (float): variation in the axis
        """
        self.is_parallel = np.absolute(inclination_value)< threshold
        self.value = inclination_value
        self.is_positive = inclination_value > 0

class DataToShow:
    def __init__(self, data_acquisition: DataFromAcquisition, zmin= ZMIN, zmax= ZMAX):
        """_summary_

        Args:
            data_acquisition (DataFromAcquisition): rgb-d original from stream
        
        """  
        self.rgb = data_acquisition.rgb
        self.depth = depth2color(data_acquisition.depth, zmin=zmin, zmax= zmax)
        self.HEIGHT, self.WIDTH = self.rgb.shape[:2]
        
    
class DatasetTypes:
    "titles of dataset types"
    Z_CALIBRATION = 'Z Calibration'
    UV_CALIBRATION = 'UV Calibration'
    AREA_CALIBRATION = 'Area Calibration'
    MILL= 'At Mill'
    def as_list(self)->List[str]:
        """
        Returns:
            List[str]: All dataset types in a list
        """
        return [self.Z_CALIBRATION,
                self.UV_CALIBRATION,
                self.AREA_CALIBRATION,
                self.MILL
               ]          
DATASET_TYPES = DatasetTypes()
