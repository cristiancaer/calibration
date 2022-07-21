from APP.MAKEDATASET.views import depth2color
from APP.models.basic_config import HOUR_FORMAT, RGB_PREFIX, DEPTH_PREFIX, ZMAX, ZMIN
from typing import Dict, List, Any, Tuple
import numpy as np
from datetime import date, datetime
import sys
sys.path.append('./')


class DataFromAcquisition:
    """ To store de data produce in acquisition 
    """

    def __init__(self, rgb: np.ndarray, depth: np.ndarray, fps: float = None) -> None:
        self.rgb = rgb
        self.depth = depth
        self.hour = datetime.now()
        self.fps = fps 
    
    def copy(self):
        copy = DataFromAcquisition(self.rgb.copy(), self.depth.copy())
        copy.hour = self.hour
        return copy


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

class SavedInfo:
    def __init__(self, last_saved:str, buffer_size:int, saturation_times:int, first_saved=0)->None:
        self.last_saved = last_saved
        self.first_saved = str(first_saved)
        self.buffer_size = str(buffer_size)
        self.saturation_times = str(saturation_times)


class InclinationStatus:
    def __init__(self, threshold: float, inclination_value: float) -> None:
        """
        used in parallel checking

        Args:
            thread (float): if |inclination_value|< Thread, we'll consider that the surface is parallel to the camera
            inclination_value (float): variation in the axis
        """
        self.is_parallel = np.absolute(inclination_value) < threshold
        self.value = inclination_value
        self.is_positive = inclination_value > 0


class DataToShow:
    def __init__(self, data_acquisition: DataFromAcquisition, zmin=ZMIN, zmax=ZMAX):
        """_summary_

        Args:
            data_acquisition (DataFromAcquisition): rgb-d original from stream

        """
        self.rgb = data_acquisition.rgb.copy()
        self.depth = depth2color(data_acquisition.depth.copy(), zmin=zmin, zmax=zmax)
        self.fps = data_acquisition.fps
        self.HEIGHT, self.WIDTH = self.rgb.shape[:2]


class DatasetTypes:
    "titles of dataset types"
    Z_CALIBRATION = 'Z Calibration'
    UV_CALIBRATION = 'UV Calibration'
    AREA_CALIBRATION = 'Area Calibration'
    MILL = 'At Mill'

    def as_list(self) -> List[str]:
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


def int_array(*args: Any) -> np.ndarray:
    """make an array of int numbers 

    Args:
        number_list (Any[int,float]): list of int or float numbers, it cannot be a list object

    Returns:
        np.ndarray: array of int numbers and shape = -1
    """
    buffer: List[Any[int, float]] = []
    for value in args:
        if not isinstance(value, list):
            buffer.append(value)
    return np.array(buffer, dtype=int)

class EventData:
    "to temporary store the info used in event_loop_manager"

    def __init__(self, name: str, data_to_work: any) -> None:
        self.name = name
        self.data_to_work = data_to_work