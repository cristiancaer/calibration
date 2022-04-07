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
    def __init__(self, rgb: np.ndarray = None, depth: np.ndarray = None, hour: datetime = None):
        self.data: Dict[str, np.ndarray] = {}
        self.add_img(RGB_PREFIX, rgb)
        self.add_img(DEPTH_PREFIX, depth)
        self.hour = hour
        if not hour:
            self.hour = datetime.now()
        self.hour = self.hour.strftime(HOUR_FORMAT)

    def add_img(self, name: str, img: np.ndarray):
        if hasattr(img, 'shape'):
            self.data.update({name: img})


class DataToShow:
    def __init__(self, data_acquisition: DataFromAcquisition, **args: np.ndarray):
        self.set_range(ZMIN, ZMAX)
        self.data: Dict[str, np.ndarray] = {}
        self.add_img(RGB_PREFIX, data_acquisition.rgb)
        self.add_img(DEPTH_PREFIX, data_acquisition.depth)
        self.hour = data_acquisition.hour.strftime(HOUR_FORMAT)
        for image_name, img in args.items():
            self.add_img(image_name, img)

    def add_img(self, name: str, img: np.ndarray):
        if hasattr(img, 'shape'):
            if img.dtype == np.uint16:
                img = depth2color(img)
            self.data.update({name: img})

    def set_range(self, zmin: float, zmax: float):
        self.zmin = zmin
        self.zmax = zmax
