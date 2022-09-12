from typing import List
import numpy as np
import cv2
import sys
import random
from scipy import optimize
import matplotlib.pyplot as plt
sys.path.append('./')
from APP.models.basic_config import ZMAX, ZMIN
from APP.CALIBRATION.models.data_objects import ImgData, ImgTypeNames
from APP.CALIBRATION.control.files.names_handler import NamesHandler
from APP.CALIBRATION.control.calibration_sections.sections_handler import SectionsSaveHandler
from APP.CALIBRATION.control.calibration_sections import UvSectionRgb, UvSectionDepth, HomographySection, AreaSection, ZSection
from APP.CALIBRATION.control.detect_pattern.circle_detector import get_circle_detector
from APP.control.utils import norm, get_img_from_fig


class AreaCalibration:
    def __init__(self,  path_config:str, name_config:str)->None:
        stored_data = SectionsSaveHandler().open(path_config, name_config)
        self.rgb_section = UvSectionRgb(stored_data)
        self.depth_section = UvSectionDepth(stored_data)
        self.z_section = ZSection(stored_data)
        self.homgraphy_section = HomographySection(stored_data)
        self.segmenter = get_circle_detector()
        self.set_units_factor('m')
        self.shape = None
            
    def preprocess(self, img_data:ImgData) -> ImgData:
        if (ImgTypeNames.rgb in img_data.images) and (ImgTypeNames.depth in img_data.images):
            rgb = img_data.images.get(ImgTypeNames.rgb)
            rgb = self.rgb_section.undistort(rgb)
            rgb = self.homgraphy_section.rgb2depth(rgb)
            img_data.update_img(ImgTypeNames.rgb, rgb)
            
            depth = img_data.images.get(ImgTypeNames.depth)
            depth = self.z_section.undistort(depth)
            depth = self.depth_section.undistort(depth)
            img_data.update_img(ImgTypeNames.depth, depth)
            
            return img_data
            
        
    def set_units_factor(self,units: str) -> None:
        factor_conversion={'m':1/10000, #100um to meters
                             'cm':1/100,#100um to cm
                             'mm':1/10#100um to mm
                            }
        self.units_factor = factor_conversion.get(units)
    
    def set_min_max_values(self, z_min: float, z_max: float) -> None:
        self.z_min = z_min
        self.z_max = z_max
    
    def get_img_area(self, rgb_img: np.ndarray, radius: float) -> float:
        if self.shape != rgb_img.shape[:2]:
            self.shape = rgb_img.shape[:2]
        mascara=np.zeros((self.shape[0],self.shape[1]),dtype=np.uint8)
        key_points = self.segmenter.detect(rgb_img)
        for p in key_points:
            x,y=p.pt
            mascara=cv2.circle(mascara, (int(x),int(y)), radius=int(p.size/(2)), color=(1), thickness=-1)

        total_area=np.pi*(radius**2)*len(key_points)
        return mascara,total_area
    
    def get_data(self, names_handler: NamesHandler, radius: float, z_min: float=ZMIN, z_max: float=ZMAX) -> List[list]:
        self.set_min_max_values(z_min, z_max)
        list_areas = []
        list_depth_points = []
        list_means = []
        for img_data in names_handler.get_img_data_list():
            img_data = self.preprocess(img_data)
            rgb = img_data.images.get(ImgTypeNames.rgb)
            mask, total_area = self.get_img_area(rgb, radius)
            if total_area:
                index = np.where(mask == 1)
                depth = img_data.images.get(ImgTypeNames.depth)[index]
                depth_mean = depth.mean()
                if  self.z_min <= depth_mean <=self.z_max:
                    norm_depth = norm(depth.copy(), self.z_min, self.z_max).reshape(-1, 1)
                    # shuffle depth points
                    random_index = random.sample(range(norm_depth.shape[0]), int(norm_depth.shape[0]))
                    norm_depth = norm_depth[random_index]
                    # add noise
                    norm_depth = self.add_noise(norm_depth, 1)
                    total_area = self.add_noise(total_area, 1)[0]
                    list_depth_points.append(norm_depth)
                    list_areas.append(total_area)
                    list_means.append(depth_mean)
            else:
                print('circles no detected')
        return list_depth_points, list_areas, list_means
    
    def get_area_coeffs(self,list_depth_points: List[np.ndarray], list_areas: list[float]) -> List:
        init_coeffs = [0.12511402,  0.06029463, -0.00160806]#self.get_init_coeffs()
        def optimizer(init_coeffs: List[float]) -> List[float]:
            return list_areas - self.area_model(list_depth_points, init_coeffs)
        
        new_coeffs, _ = optimize.leastsq(optimizer, init_coeffs,maxfev=500*(len(list_depth_points)+1))
        return new_coeffs

    def make_calibration(self, names_handler: NamesHandler, radius: float, radius_units:'str'= 'm', z_min: float=ZMIN, z_max: float=ZMAX ) -> AreaSection:
        self.set_units_factor(radius_units)
        list_depth_points, list_areas, list_means = self.get_data(names_handler,radius, z_min, z_max)
        coeffs = self.get_area_coeffs(list_depth_points, list_areas)
        area_section = AreaSection()
        area_section.update(coeffs, z_min, z_max, self.units_factor)
        return area_section
        
    
    def area_model(self, list_depth_points: np.ndarray, coeffs: list) -> float:
        list_total_areas = np.array([(coeffs[0]*array**2+coeffs[1]*array+coeffs[2]).sum() for array in list_depth_points])
        return list_total_areas

    def add_noise(self,array: np.ndarray, percentage: float):
        """

        Args:
            array (np.ndarray): numpy array
            percentage (float): 0-100 value
        """
        percentage = percentage/100
        if np.array(array).shape==():
            array = array+np.random.normal(0,array*percentage,1)
        else:
            shape=array.shape
            array = np.array(array)
            
            noise= np.random.normal(0, array.mean()*percentage, len(array))
            noise = noise.reshape(shape)

            array = array+noise
        return array
    
    def get_init_coeffs(self):
        if self.depth_section.optimized_intrin is not None:
            fx = self.depth_section.optimized_intrin[0, 0]
            fy = self.depth_section.optimized_intrin[1,1]
            area_constant = fx*fy
            
            init_coeffs = [1, 1/area_constant, 1]
            return init_coeffs
        if self.depth_section.mtx_intrin is not None:
            fx = self.depth_section.mtx_intrin[0, 0]
            fy = self.depth_section.mtx_intrin[1,1]
            area_constant = fx*fy
            
            init_coeffs = [0, 1/area_constant, 0]
        init_coeffs = [ 1, 1 , 1]
        return init_coeffs
    
         
    def get_error_area_graph(self, names_handler: NamesHandler, radius: float, area_section:AreaSection = None, z_min: float= 6000) -> np.ndarray:
        list_error = []
        list_depth = []
        for img_data in names_handler.get_img_data_list():
            img_data = self.preprocess(img_data)
            mask, total_area = self.get_img_area(img_data.images.get(ImgTypeNames.rgb), radius)
            
            index = np.where(mask==1)
            mask_depth = img_data.images.get(ImgTypeNames.depth)[index]
            depth_mean = mask_depth.mean()
            if z_min <= depth_mean:
                if area_section is None:
                    # mask_depth = norm(mask_depth, self.z_min, self.z_max)
                    fx = self.depth_section.mtx_intrin[0, 0]
                    fy = self.depth_section.mtx_intrin[1, 1]
                    area_constant = 1/(fx * fy)
                    mask_depth = self.units_factor*mask_depth
                    estimated_area = self.area_model([mask_depth], [area_constant, 0, 0])[0]# to use area model, the array mask_depth must be inside of a list, this was design for multiple images. coeffs to orbbec abstra
                else:
                    get_area = area_section.get_area_model()
                    estimated_area_row = get_area(mask_depth)# this was design to receive one image
                    estimated_area = estimated_area_row.sum()
                error = 100*(total_area-estimated_area)/total_area
                list_error.append(error)
                list_depth.append(depth_mean)
        fig, ax = plt.subplots()
        ax.plot(list_depth, list_error)
        ax.set_ylabel('error [%]')
        ax.set_xlabel('depth')
        plt.grid()
        img_graph = get_img_from_fig(fig)
        return img_graph

#TEST
################################################################################
if __name__=='__main__':
    from APP.models.basic_config import TEST_IMG_AREA_PATH, RGB_PREFIX, DEPTH_PREFIX, CONFIG_PATH, CONFIG_NAME
    from APP.CALIBRATION.control.app_panels.img_media import ImageMedia
    from APP.CALIBRATION.models.data_objects import ImgData
    from APP.views.basic import yes_no_message_box, ok_message_box
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
    import matplotlib.pyplot as plt
    
    # calibration
    names_handler = NamesHandler(TEST_IMG_AREA_PATH, rgb_prefix=RGB_PREFIX, depth_prefix=DEPTH_PREFIX)
    calibration = AreaCalibration(CONFIG_PATH, CONFIG_NAME)
    def process_function(img_data:ImgData):
        rgb = img_data.images.get(ImgTypeNames.rgb)
        mask, total_area = calibration.get_img_area(rgb, 5/100)
        mask = 255*cv2.merge((mask, mask, mask))
        img_data.update_img(ImgTypeNames.process, mask)
        return img_data
    app = QApplication(sys.argv)
    window =  ImageMedia(names_handler, process_function, list_img_names=[ImgTypeNames.rgb,ImgTypeNames.process])
    window.show()
    app.exec()
    error_img = calibration.get_error_area_graph(names_handler, radius=5/100)
    ok_message_box('Area error before calibration')
    plt.imshow(error_img)
    plt.show()
    area_section = calibration.make_calibration(names_handler, radius=5/100, radius_units='m')
    print(area_section.as_dict())
    error_img = calibration.get_error_area_graph(names_handler, radius=5/100, area_section=area_section, z_min=9000)
    ok_message_box('Area error after calibration')
    plt.imshow(error_img)
    plt.show()
    save = yes_no_message_box('save data?')
    if save:
        area_section.save(CONFIG_PATH, CONFIG_NAME)
        ok_message_box(f'config saved in :\n {CONFIG_PATH}/{CONFIG_NAME}')
    sys.exit()
    