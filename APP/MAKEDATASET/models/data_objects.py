from typing import Dict
import numpy as np
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
        self.add_img(RGB_PREFIX, data_acquisition.rgb)
        self.add_img(DEPTH_PREFIX, data_acquisition.depth)
        self.hour = data_acquisition.hour.strftime(HOUR_FORMAT)

    def add_img(self, name: str, img: np.ndarray):
        if isinstance(img, np.ndarray):
            self.data.update({name: img})


class DataToShow:
    def __init__(self, data_acquisition: DataFromAcquisition, depth_mod: np.ndarray= None):
        """_summary_

        Args:
            data_acquisition (DataFromAcquisition): rgb-d original from stream
            depth_mod (np.ndarray, optional): a depth image that has been modify to show usefull information. it must be an 3-chanel numpy array with uint8 datatype.Defaults to None.
        """
        self.set_range(ZMIN, ZMAX)
        self.rgb = data_acquisition.rgb
        if isinstance(depth_mod, np.ndarray):
            self.depth = depth_mod
        else:
            self.depth = depth2color(data_acquisition.depth, zmin=self.zmin, zmax= self.zmax)

    def set_range(self, zmin: float, zmax: float):
        """
        to have a better visualization of a depth image.
        
        zmin y zmax allow to have a better visualization of values betwin this range

        Args:
        """
        self.zmin = zmin
        self.zmax = zmax
