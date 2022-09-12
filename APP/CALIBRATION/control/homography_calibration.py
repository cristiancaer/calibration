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
from APP.CALIBRATION.control.detect_pattern.circle_pattern import CirclePoints
from APP.control.utils import norm, get_img_from_fig


class HomographyCalibration():
    def __init__(self,  path_config:str, name_config:str)->None:
        stored_data = SectionsSaveHandler().open(path_config, name_config)
        self.rgb_section = UvSectionRgb(stored_data)
        self.homography_section = None
        self.depth_section = UvSectionDepth(stored_data)
        self.z_section = ZSection(stored_data)
        self.segmenter = None
        self.shape = None
    def get_rgb_and_depth_points(self, img_data: ImgData) -> List:
        img_data = self.preprocess(img_data)
        rgb = img_data.images.get(ImgTypeNames.rgb)
        rgb_ret, rgb_points = self.segmenter.get_center_circle_points(rgb)
        depth = img_data.images.get(ImgTypeNames.depth)
        depth_ret, depth_points = self.segmenter.get_center_circle_points(depth, is_depth=True)
        final_detection = rgb_ret, depth_ret
        return final_detection, rgb_points, depth_points
    
    def make_calibration(self, names_handler: NamesHandler, nrow: int, ncolumn: int) -> HomographySection:
        self.segmenter = CirclePoints(nrow, ncolumn)
        homography_totalizer = 0
        for img_data in names_handler.get_img_data_list():
            ret, rgb_points, depth_points = self.get_rgb_and_depth_points(img_data)
            if ret:
                homography,ret=cv2.findHomography(rgb_points, depth_points)# source reference, final reference: rgb -> depth    
                homography_totalizer += homography
                
        final_homography = homography_totalizer / names_handler.image_number
        homography_section = HomographySection()
        homography_section.update(mtx=final_homography)
        return homography_section
    
    def get_error(self, names_handler: NamesHandler, n_row: int, n_column: int, homography_section: HomographySection=None):
        self.segmenter = CirclePoints(n_row, n_column)
        self.homography_section = homography_section
        error = []
        for img_data in names_handler.get_img_data_list():
            ret, rgb_points, depth_points = self.get_rgb_and_depth_points(img_data)
            if ret:
                img_error = cv2.norm(depth_points,rgb_points, cv2.NORM_L2)/len(depth_points)
                error.append(img_error)
        mean_error = np.array(error).mean()
        return mean_error

    def preprocess(self, img_data:ImgData) -> ImgData:
        if (ImgTypeNames.rgb in img_data.images) and (ImgTypeNames.depth in img_data.images):
            rgb = img_data.images.get(ImgTypeNames.rgb)
            rgb = self.rgb_section.undistort(rgb)
            if self.homography_section is not None:
                rgb = self.homography_section.rgb2depth(rgb)
            img_data.update_img(ImgTypeNames.rgb, rgb)
            
            depth = img_data.images.get(ImgTypeNames.depth)
            depth = self.z_section.undistort(depth)
            depth = self.depth_section.undistort(depth)
            img_data.update_img(ImgTypeNames.depth, depth)
            return img_data

#TEST
################################################################################
if __name__=='__main__':
    from APP.models.basic_config import TEST_IMG_HOMOGRAPHY_PATH, RGB_PREFIX, DEPTH_PREFIX, CONFIG_PATH, CONFIG_NAME
    from APP.CALIBRATION.control.app_panels.img_media import ImageMedia
    from APP.CALIBRATION.models.data_objects import ImgData
    from APP.views.basic import yes_no_message_box, ok_message_box
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import QCoreApplication
    
    app = QApplication(sys.argv)
    names_handler = NamesHandler(TEST_IMG_HOMOGRAPHY_PATH, rgb_prefix=RGB_PREFIX, depth_prefix=DEPTH_PREFIX)
    homography_calibration = HomographyCalibration(CONFIG_PATH, CONFIG_NAME)
    # pixel error before calibration
    
    error = homography_calibration.get_error(names_handler, n_row=9, n_column=6)
    ok_message_box(f'mean error before calibration: \n  {error}')
    