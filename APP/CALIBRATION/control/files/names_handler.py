
import sys
from typing import List
import numpy as np
import cv2
sys.path.append('./')
from APP.CALIBRATION.control.files import get_list_index
from APP.CALIBRATION.models.data_objects import ImgData, ImgTypes
from APP.CALIBRATION.models.data_objects import ImgData


class NamesHandler():
    def __init__(self, path: str, rgb_prefix: str =None, depth_prefix: str=None)->None:
        self.path = path
        self.rgb_prefix = rgb_prefix
        self.depth_prefix = depth_prefix
        self.message = None
        self.list_index = []
        
        rgb_index = set(get_list_index(path, rgb_prefix))
        depth_index = set(get_list_index(path, depth_prefix))
        if rgb_index and depth_index:
            self.list_index = sorted(list(rgb_index.intersection(depth_index)))
        elif rgb_index:
            self.list_index = list(rgb_index)
            self.message = 'depth images no found'
        elif depth_index:
            self.list_index = list(depth_index)
            self.message = 'rgb images no found'
        else:
            self.message = 'images no found'
        self.actual_id = 0 #  actual_id(id in list) != index (prefix_index)
        
        self.read_completed = False # to indicate that all the image had been read
        if self.message:
            print(self.message)
        self.image_number = len(self.list_index)
        
    def delete_index(self, id: int):
        self.list_index.pop(id)
    
    def go_next_id(self) -> int:
        self.actual_id += 1
        if self.actual_id >= self.image_number-1:
            self.read_completed = True
            self.actual_id = 0
            
    def go_back_id(self) -> int:
        self.actual_id -= 1
        if self.actual_id < 0:
            self.actual_id = 0
            
    def _read_img(self,prefix: str) -> np.ndarray:
        img = None
        try:
            img = cv2.imread(f'{self.path}/{prefix}_{self.list_index[self.actual_id]}.png', cv2.IMREAD_UNCHANGED)
        except:
            pass
        return img
    
    def read_last_pair(self) -> ImgData:
        depth = None
        rgb = None
        if self.rgb_prefix:
            rgb = self._read_img(self.rgb_prefix)
        if self.depth_prefix:
            depth = self._read_img(self.depth_prefix)
        return ImgData(self.actual_id, ImgTypes(rgb=rgb, depth=depth))

    def get_next_data(self):
        data = self.read_last_pair()
        self.go_next_id()
        return data
    
    def get_back_data(self):
        data= self.read_last_pair()
        self.go_back_id()
        return data
    
    def reset_reading(self):
        self.actual_id = 0
        self.read_completed = False
    
    def get_list_imgs(self, prefix: str) -> List[np.ndarray]:
        list_img: List[np.ndarray] = []
        for data_image in self.get_img_data_list():
            img = data_image.images.get(prefix)
            if img is not None:
               list_img.append(img)
        return list_img
    
    def get_img_data_list(self) -> ImgData:
        self.reset_reading()
        while not self.read_completed:
            yield self.get_next_data()
#TEST
################################################################################

        
    