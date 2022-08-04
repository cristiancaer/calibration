from curses import window
from typing import List, Tuple
import cv2
import sys
import numpy as np
sys.path.append('./')
from APP.CALIBRATION.control.calibration_sections import UvSection
from APP.CALIBRATION.control.files.names_handler import NamesHandler
from APP.CALIBRATION.control.detect_pattern.circle_pattern import CirclePoints
from APP.CALIBRATION.models.data_objects import ImgTypeNames


class UvCalibration():
    """use to get uv calibration. this includes intrinsic matrix and distortion coefficients
    """

    def __init__(self, diameter: float, nrow: int, ncolumn: int) -> None:
        """use to get uv calibration. this includes intrinsic matrix and distortion coefficients

        Args:
            
            diameter (float): pattern circle diameter, it could be write in  any units [m, cm, dm, ..]
            nrow (int): pattern row number
            ncolumn (int): pattern column number
        """
        
        self.pattern_detector = CirclePoints(nrow, ncolumn)
        self.object_points = self.pattern_detector.get_object_points(diameter)
        self.img_shape = None
        
    def get_points(self,names_handler: NamesHandler, is_depth: bool) -> Tuple[List[np.ndarray]]:
        """ get points from all the images in names_handler
        Args:
            names_handler (NamesHandler): this allow to access to the images that are going to use in the calibration
            is_depth (bool): True if the calibration is for depth sensor, False if it is for rgb sensor

        Returns:
            Tuple[List[np.ndarray]]: 
        """
        names_handler.reset_reading()
        list_img_points = []
        list_object_points = []
        while not names_handler.read_completed:
            image_data = names_handler.get_next_data()
            
            if is_depth:
                img = image_data.images.get(ImgTypeNames.depth)
            else:
                img = image_data.images.get(ImgTypeNames.rgb)
                
            ret, img_points = self.pattern_detector.get_center_circle_points(img, is_depth)
            if ret:
                list_img_points.append(img_points)
                list_object_points.append(self.object_points)
        
        img_shape = img.shape
        if not list_img_points:
            print('there are no detections')
        
        return list_img_points, list_object_points, img_shape
    
    def make_calibration(self, names_handler: NamesHandler, is_depth: bool= False):
        list_img_points, list_obj_points, img_shape = self.get_points(names_handler, is_depth)
        img_shape = img_shape[:2]# only hight and width
        ret, mtx,dist, rotation_vectors, translation_vectors = cv2.calibrateCamera(list_obj_points, list_img_points, img_shape[::-1],None,None)## las dimensiones que recive son de ancho por alto, por eso hay que invertir gray.shape
        if not ret:
            return None, None
        
        mtx_opt, roi = cv2.getOptimalNewCameraMatrix(mtx, dist,img_shape[::-1],1)# the shape must be [width, height]
        list_error = self.get_projection_errors(list_img_points, list_obj_points, rotation_vectors, translation_vectors, mtx, dist )
        uv_section = UvSection()
        uv_section.update(mtx, mtx_opt, dist, roi, list_error.mean())
        return uv_section, list_error  
            
    def get_projection_errors(self, list_img_points, list_obj_points, rotation_vts, translation_vts, mtx, dist) -> np.ndarray: 
        list_error = []
        for i, object_points in enumerate(list_obj_points):
            obj2img_points,_ = cv2.projectPoints(object_points, rotation_vts[i], translation_vts[i], mtx, dist)
            error = cv2.norm(list_img_points[i], obj2img_points, cv2.NORM_L2)/len(obj2img_points)
            list_error.append(error)
        return np.array(list_error)

#TEST
################################################################################
if __name__=='__main__':
    from APP.models.basic_config import TEST_IMG_PATH, RGB_PREFIX, DEPTH_PREFIX
    from APP.CALIBRATION.control.app_panels.img_media import ImageMedia
    from APP.CALIBRATION.models.data_objects import ImgData
    from PyQt5.QtWidgets import QApplication
    
    # calibration
    names_handler = NamesHandler(TEST_IMG_PATH, rgb_prefix=RGB_PREFIX, depth_prefix=DEPTH_PREFIX)
    calibration = UvCalibration(diameter= 5, nrow=9, ncolumn=6)
    depth_uv_section, list_error = calibration.make_calibration(names_handler, is_depth=True)
    rgb_uv_section, list_error = calibration.make_calibration(names_handler, is_depth=False)
    
    
    # show results
    ## check if there the images. 
    # if there are more distortion, the  column or row number could be wrong
    # if there are information displacement, the pattern does not cover the range image. you will need take images from the zones where the pattern was not visualized 
    def show_data(uv_section: UvSection):
        for key, value in uv_section.as_dict().items():
            print(f'{key}: \n {value} \n')
    
    def undistort(img_data: ImgData, prefix, uv_section: UvSection):
        img = img_data.images.get(prefix)
        undistorted_img = uv_section.undistort(img)
        img_data.update_img(prefix, undistorted_img)
        return img_data
        
    def process_function(img_data: ImgData):
        if ImgTypeNames.rgb in img_data.images:
            img_data = undistort(img_data, ImgTypeNames.rgb, rgb_uv_section)
        
        if ImgTypeNames.depth in img_data.images:
            img_data = undistort(img_data, ImgTypeNames.depth, depth_uv_section)
           
        return img_data
    print('rgb calibration')
    show_data(rgb_uv_section)
    print('depth calibration')
    show_data(depth_uv_section)
    
    app = QApplication(sys.argv)
    window = ImageMedia(names_handler, process_function, [ImgTypeNames.rgb,ImgTypeNames.depth])
    window.show()
    sys.exit(app.exec())