from typing import Dict
import numpy as np
class ImgTypeNames:
    rgb = 'RGB'
    depth = 'Depth'
    process = 'Process'
    undistorted = 'Undistorted Image'
    
class ImgTypes:
    def __init__(self, rgb:np.ndarray=None, depth:np.ndarray=None, process:np.ndarray=None, undistorted:np.ndarray=None)->None:
        self.data:Dict[str, np.ndarray] = {}
        if rgb is not None:
            self.data.update({ImgTypeNames.rgb: rgb})
        
        if depth is not None:
            self.data.update({ImgTypeNames.depth: depth})
        
        if process is not None:
            self.data.update({ImgTypeNames.process: process})
        
        if undistorted is not None:
            self.data.update({ImgTypeNames.undistorted: undistorted})
        
class ImgData:
    def __init__(self, index: int , images:ImgTypes)->None:
        self.index = index
        self.images = images.data
        
    def update_img(self, img_name: str, img: np.ndarray) -> None:
        self.images.update({img_name: img})