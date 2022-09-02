import re
from typing import List, Tuple
import numpy as np
import cv2
import sys
from sklearn import linear_model
from concurrent import futures
import multiprocessing
sys.path.append('./')
from APP.CALIBRATION.control.calibration_sections import ZSection
from APP.CALIBRATION.control.files.names_handler import NamesHandler
from APP.control.utils import get_uv_coords, norm, recover
from APP.models.basic_config import CONFIG_NAME, CONFIG_PATH, DEPTH_PREFIX, TEST_IMG_Z_PATH, ZMIN, ZMAX
from APP.CALIBRATION.models.data_objects import ImgData, ImgTypeNames
from time import time


class ZCalibration:
    def __init__(self)->None:
        self.uv = None
        self.shape = []
        self.max_threads = 15
    
    def make_uv(self, shape):
        #get u,v coords 
        self.shape = shape
        u, v = get_uv_coords(shape)
        #reshape to(N,2)
        self.uv=np.array((u.reshape(-1),v.reshape(-1))).transpose()
            
    def get_best_plane(self, depth_img: np.ndarray) -> Tuple[np.ndarray]:
        if len(depth_img.shape)==3:
            depth_img = depth_img[:, :, 0]
        if self.shape != depth_img.shape:
            self.make_uv(depth_img.shape)
        
        if self.uv is None:
            self.make_uv(depth_img.shape)
        # create model
        depth_img = recover(depth_img)
        z = depth_img.copy().reshape(-1,1)
        model = linear_model.LinearRegression()   
        #train model
        model.fit(self.uv,z)

        #get best plane
        z_model = model.predict(self.uv)
        return z.reshape(-1), z_model.reshape(-1)
    
    def get_points(self, names_handler: NamesHandler) -> Tuple[np.ndarray]:
        names_handler.reset_reading()
        list_z = []
        list_model = []
        
        list_depth_imgs = names_handler.get_list_imgs(ImgTypeNames.depth)
        self.make_uv(list_depth_imgs[0].shape)
        if list_depth_imgs:
            with futures.ProcessPoolExecutor(max_workers= multiprocessing.cpu_count() - 1) as executor:
                futures_r = [executor.submit(self.get_best_plane, img) for img in list_depth_imgs]
                for i,future in enumerate(futures.as_completed(futures_r, timeout =300)):
                    print('image',i)
                    result = future.result()
                    list_z.append(result[0])
                    list_model.append(result[1])
        
        print(self.shape, self.uv.shape)
        return np.array(list_z), np.array(list_model)
    
    def train_model(self, z_data:np.ndarray, model_data: np.ndarray) -> linear_model._base.LinearRegression:
        z_data = z_data.reshape(-1,1)
        z_data = np.hstack([np.power(z_data,2), z_data])
        model_data = model_data.reshape(-1,1)
        model = linear_model.LinearRegression()
        model.fit(z_data, model_data)
        return model
    
    def get_pixel_models(self, list_z: np.ndarray, list_model: np.ndarray, zmin: float = ZMIN, zmax: float = ZMAX) -> List[linear_model._base.LinearRegression]:
        """get a model by each pixel

        Args:
            list_z (np.ndarray): shape(n_images, n_pixels)
            list_model (np.ndarray): shape(n_images, n_pixels) 
        """
        list_z = norm(list_z, zmin, zmax)
        list_model = norm(list_model, zmin, zmax)
        input = [[list_z[:, i], list_model[:, i]] for i in range(list_z.shape[1])]
        print('start train')
        init = time()
        list_models = []
        i = 0
        buffer_percentage = None
        for z, model in input:
            i+=1
            list_models.append(self.train_model(z,model))
            percentage = round(100*i/(len(input)),0)
            if percentage != buffer_percentage and percentage%2==0:
                buffer_percentage = percentage
                print(percentage, ' %')
        # list_pixel_models = [self.train_model(z, model) for z, model in input ]
        # list_pixel_models = []
        # with futures.ProcessPoolExecutor(max_workers= multiprocessing.cpu_count() - 1) as executor:
        #     future_results = [executor.submit(self.train_model, z, model) for z,model in input]
        #     for i,completed_result in enumerate(futures.as_completed(future_results)):
        #         n = int(1000*i / list_z.shape[1])
        #         print(i)
        #         model = completed_result.result()
        #         list_pixel_models.append(model)
        print('process time', time()-init)
        return list_models
    
    def coeff_from_models(self, list_pixel_models: List[linear_model._base.LinearRegression]) -> List[np.ndarray]:
        print(self.shape)
        coeff2 =  np.array([model.intercept_ for model in list_pixel_models]).reshape(self.shape[0], self.shape[1])
        coeff01 = np.array([model.coef_ for model in list_pixel_models])
        
        coeff0 = coeff01[:, :, 0].reshape(self.shape[0], self.shape[1])
        coeff1 = coeff01[:, :, 1].reshape(self.shape[0], self.shape[1])
        return coeff2, coeff1, coeff0
        
    def make_calibration(self, names_handler: NamesHandler, zmin: float= ZMIN, zmax: float = ZMAX) -> ZSection:
        list_z, list_model = self.get_points(names_handler)
        list_pixel_models = self.get_pixel_models(list_z, list_model, zmin, zmax)
        coeff2, coeff1, coeff0 = self.coeff_from_models(list_pixel_models)
        z_section = ZSection()
        z_section.update(coeff0, coeff1, coeff2, zmin, zmax)
        return z_section
    
#TEST
################################################################################
if __name__=='__main__':
    from APP.CALIBRATION.control.app_panels.img_media import ImageMedia
    from PyQt5.QtWidgets import QApplication
    from APP.control import depth2color
    from APP.control.utils import get_max_contrast_fig
    from APP.views.basic import yes_no_message_box, ok_message_box
    from PyQt5.QtCore import QCoreApplication
    
    app = QApplication(sys.argv)
    ok_message_box('this will take about 10 minutes')

    names_handler = NamesHandler(TEST_IMG_Z_PATH, depth_prefix=DEPTH_PREFIX)
    z_calibration = ZCalibration()
    z_section = z_calibration.make_calibration(names_handler)
    
    
    def process_function(image_data: ImgData) -> ImgData:
        window.show_skip_button()
        depth_img = image_data.images.get(ImgTypeNames.depth)
        if depth_img is not None:
            if len(depth_img.shape)==3:
                depth_img = depth_img[:, :, 0]
            depth_img = recover(depth_img)    
            undistorted_img = z_section.undistort(depth_img)
            std = depth_img.std()
            mean = depth_img.mean()
            min_value = mean - 2*std
            max_value = mean + 2*std
            
            undistorted_img = depth2color(undistorted_img, min_value, max_value)
            depth_img = depth2color(depth_img, min_value, max_value )
            image_data.update_img(ImgTypeNames.depth, depth_img)
            image_data.update_img(ImgTypeNames.process, undistorted_img)
        return image_data
    
    app = QApplication(sys.argv)
    window = ImageMedia(names_handler, process_function, list_img_names=[ImgTypeNames.depth, ImgTypeNames.process])
    window.button_skip.clicked.connnect(QCoreApplication.instance().quit)
    window.show()
    app.exec()
    status = yes_no_message_box('do you want to save the config data')
    if status:
        z_section.save(CONFIG_PATH, CONFIG_NAME)
        ok_message_box(f'config saved\n {CONFIG_PATH}/{CONFIG_NAME}')
    sys.exit()
    
    