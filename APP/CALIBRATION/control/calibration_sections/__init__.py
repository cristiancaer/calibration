import numpy as np
import cv2
import sys
sys.path.append('./')
from APP.CALIBRATION.models.calibration_sections import *


class UvSection(CalibrationSection):
    mtx_intrin = None
    optimized_intrin = None
    distortion_coeff = None
    roi = None
    error = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, prefix: str = None) -> None:
        """use to load/store the uv calibration data from a dict(json) variable.
        use the update() function when the data don't came from a dict

        Args:
            stored_data (Dict[str, Dict[str, any]], optional): the first level divide rgb and depth data, the second level has the fields of the uv calibration. Defaults to None.
            prefix (str, optional): rgb or depth prefix. Defaults to None.
        """
        if stored_data:
            self.set_from_dict(stored_data[prefix])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.mtx_intrin = dict_fields.get(UvFields.MTX_INTRIN)
        self.optimized_intrin = dict_fields.get(UvFields.OPTIMIZED_INTRIN)
        self.distortion_coeff = dict_fields.get(UvFields.DISTORTION_COEFF)
        self.roi = dict_fields.get(UvFields.ROI)
        self.error = dict_fields.get(UvFields.ERROR)
        
    def update(self, mtx_intrin: np.ndarray = None, optimized_intrin: np.ndarray= None, distortion_coeff: np.ndarray= None, roi: np.ndarray= None, error: float= None) -> None:
        if mtx_intrin is not None:
            self.mtx_intrin = mtx_intrin
        if optimized_intrin is not None:
            self.optimized_intrin = optimized_intrin
        if distortion_coeff is not None:
            self.distortion_coeff = distortion_coeff
        if roi is not None:
            self.roi = roi
        if error is not None:
            self.error = error

    def undistort(self, img: np.ndarray) -> np.ndarray:
        if  self.distortion_coeff is None:
            return img
        undistorted_img = cv2.undistort(
            img, self.mtx_intrin, self.distortion_coeff, None, self.optimized_intrin)
        return undistorted_img


class ZSection(CalibrationSection):
    description = None
    coeff0 = None
    coeff1 = None
    coeff2 = None
    zmin = None
    zmax = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.Z_CAL])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.description = dict_fields.get(ZFields.DESCRIPTION)
        self.coeff0 = dict_fields.get(ZFields.COEFF0)
        self.coeff1 = dict_fields.get(ZFields.COEFF1)
        self.coeff2 = dict_fields.get(ZFields.COEFF2)
        self.zmin = dict_fields.get(ZFields.ZMIN)
        self.zmax = dict_fields.get(ZFields.ZMAX)
    
    def update(self, description: str, coeff0: np.ndarray, coeff1: np.ndarray, coeff2: np.ndarray, zmin:float, zmax: float):
        if description is not None:
            self.description = description
        if coeff0 is not None:
            self.coeff0 = coeff0
        if coeff1 is not None:
            self.coeff1 = coeff1
        if coeff2 is not None:
            self.coeff2 = coeff2
        if zmin is not None:
            self.zmin = zmin
        if zmax is not None:
            self.zmax = zmax
            
    def normalization(self, depth_row: np.ndarray) -> np.ndarray:
        return (depth_row - self.zmin)/(self.zmax - self.zmin)

    def de_normalization(self, z_norm: np.ndarray) -> np.ndarray:
        return z_norm*(self.zmax - self.zmin) + self.zmin

    def undistort(self, depth_img: np.ndarray) -> np.ndarray:
        z_norm = depth_img.astype(float)
        z_undistorted = self.coeff0*z_norm**2 + self.coeff1*z_norm + self.coeff2
        z_denorm = self.de_normalization(z_undistorted)
        return z_denorm


class AreaSection(CalibrationSection):
    polynomial = None
    zmin = None
    zmax = None
    units = None
    description = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.AREA])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.polynomial = dict_fields.get(AreaFields.POLYNOMIAL)
        self.zmin = dict_fields.get(AreaFields.ZMIN)
        self.zmax = dict_fields.get(AreaFields.ZMAX)
        self.units = dict_fields.get(AreaFields.UNITS)
        self.description = dict_fields.get(AreaFields.DESCRIPTION)
        print('description', dict_fields.get(AreaFields.DESCRIPTION))
    
    def update(self, polynomial: np.ndarray, zmin: float, zmax: float, units: float, description: str):
        if polynomial is not None:    
            self.polynomial = polynomial
        if zmin is not None:
            self.zmin = zmin
        if zmax is not None:
            self.zmax = zmax
        if units is not None:
            self.units = units
        if description is not None:
            self.description = description 
    def normalization(self, depth_row: np.ndarray) -> np.ndarray:
        return (depth_row - self.zmin)/(self.zmax - self.zmin)

    def set_area_model(self):
        def get_area(depth_row: np.ndarray) -> np.ndarray:
            norm_row = self.normalization(depth_row.copy())
            area_row = np.polyval(self.polynomial, norm_row)
            return area_row
        return get_area

    def conversion_camera2area_units(self, depth_row: np.ndarray):
        return self.units*depth_row


class HomographySection(CalibrationSection):
    mtx = None
    error = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.HOMOGRAPHY])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.mtx = dict_fields.get(HomographyFields.MTX)
        self.error = dict_fields.get(HomographyFields.ERROR)
    
    def update(self, mtx: np.ndarray, error: float):
        if mtx is not None:
            self.mtx = mtx
        if error is not None:
            self.error = error

    def rgb2depth(self, rgb_img: np.ndarray) -> np.ndarray:
        img_to_depth = cv2.warpPerspective(
            rgb_img, self.mtx, (rgb_img.shape[1], rgb_img.shape[0]))
        return img_to_depth


class ImgRefSection(CalibrationSection):
    img = None
    depth_mean = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.IMG_REF])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.img = dict_fields.get(ImgRefFields.IMG)
        self.depth_mean = dict_fields.get(ImgRefFields.DEPTH_MEAN)

    def update(self, img: np.ndarray, depth_mean: float):
        if img is not None:
            self.img = img
        if depth_mean is not None:
            self.depth_mean = depth_mean

class DensitySection(CalibrationSection):
    description = None
    polynomial = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.DENSITY])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.description = dict_fields.get(DensityFields.DESCRIPTION)
        self.polynomial = dict_fields.get(DensityFields.POLYNOMIAL)

    def update(self, description: str, polynomial: np.ndarray):
        if description is not None:
            self.description = description
        if polynomial is not None:
            self.polynomial = polynomial
            
            
class CameraInfoSection(CalibrationSection):
    description = None
    name = None

    def __init__(self, stored_data: Dict[str, Dict[str, any]] = None, type: str = None) -> None:
        if stored_data:
            self.set_from_dict(stored_data[Sections.CAMERA_INFO])

    def set_from_dict(self, dict_fields: Dict[str, any]) -> None:
        self.description = dict_fields.get(CameraFields.DESCRIPTION)
        self.name = dict_fields.get(CameraFields.NAME)
    
    def update(self, description: str, name: str):
        if description is not None:
            self.description = description
        if name is not None:
            self.name = name
