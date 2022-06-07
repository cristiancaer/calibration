from typing import List, Tuple
import numpy as np 
from sklearn import linear_model
from APP.MAKEDATASET.models.draw_objects import PointsStore
from APP.MAKEDATASET.models.data_objects import InclinationStatus
import cv2


class ThroughPlane:
    def __init__(self, threshold:float = 20)->None:
        self.threshold = threshold
    
    def get_u_v(self, shape: Tuple[int]):
        v,u=np.mgrid[0:shape[0], 0:shape[1]]
        u = u.reshape(-1)
        v = v.reshape(-1)
        return u, v
        
    def get_model(self, depth_img: np.ndarray, mask:np.ndarray) -> linear_model._base.LinearRegression:
        shape = depth_img.shape
        mask_row = mask.reshape(-1)
        index = np.where(mask_row == 1)
        z_row = depth_img.copy().reshape(-1)
        z_row = z_row[index]

        # make coords uv. 
        u, v = self.get_u_v(shape)
        u_mask = u[index]
        v_mask = v[index]
        # eliminate the zero values
        index = np.where(z_row!=0)
        z_row = z_row[index]
        u_mask = u_mask[index]
        v_mask = v_mask[index]
        uvMask=np.array((u_mask,v_mask)).transpose()

        # model
        # put the data as column data shape = (N,2)
        model = linear_model.LinearRegression()
        model.fit(uvMask, z_row)
        return  model 
           
    def get_mask(self, shape: Tuple[int], list_points:List[PointsStore]) -> np.ndarray:
        mask = np.zeros(shape, dtype=np.uint8)
        for point_store in list_points:
            mask=cv2.fillPoly(mask, [point_store.points], 1)
        return mask
    
    def get_surface_img(self, model: linear_model._base.LinearRegression, shape: Tuple[int]) -> np.ndarray:
        u, v = self.get_u_v(shape)
        uvModel = np.array((u, v)).transpose()
        row_surface = model.predict(uvModel)
        img = row_surface.reshape(shape[0],shape[1])
        return img       
    
    def check(self, depth_img: np.ndarray, list_points:List[PointsStore]) -> Tuple[any] : 
        shape = depth_img.shape[:2]
        mask = self.get_mask(shape, list_points)
        model = self.get_model(depth_img, mask)
        x_variation = model.coef_[0]*shape[1]
        y_variation = -model.coef_[1]*shape[0]# (-) sign. this is because, top side was take as reference, but v-row grow negative towards top
        x_inclination = InclinationStatus(self.threshold, x_variation)
        y_inclination = InclinationStatus(self.threshold, y_variation)
        depth_model_img = self.get_surface_img(model, shape)
        return  y_inclination, x_inclination, depth_model_img
