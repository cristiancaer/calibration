from typing import Dict
import sys

class AreaFields():
    DESCRIPTION = 'description'
    POLYNOMIAL = 'polynomial'
    ZMIN = 'zmin'
    ZMAX = 'zmax'
    UNITS = 'units'
    
class UvFields:
    MTX_INTRIN = 'mtx_intrin'
    OPTIMIZED_INTRIN = 'optimized_intrin'
    DISTORTION_COEFF = 'distortion_coeff'
    ROI = 'roi'
    ERROR = 'error'

class ZFields:
    DESCRIPTION = 'description'
    COEFF0 = 'coeff0'
    COEFF1 = 'coeff1'
    COEFF2 = 'coeff2'
    ZMIN = 'zmin'
    ZMAX = 'zmax'
    
class HomographyFields:
    MTX = 'mtx'
    ERROR = 'error'

class ImgRefFields:
    IMG = 'img'
    DEPTH_MEAN = 'depth_mean'
    

class DensityFields:
    DESCRIPTION = 'description'
    POLYNOMIAL = 'polynomial'

class CameraFields:
    NAME = 'name'
    DESCRIPTION = 'description'
    
class Cameras:
    ORBBEC = 'orbbec'
    INTEL = 'intel'



class Sections:
    CAMERA_INFO = 'camera_info'
    UV_RGB = 'uv_rgb'
    UV_DEPTH = 'uv_depth'
    Z_CAL = 'z_cal'
    AREA = 'area'
    HOMOGRAPHY = 'homography'
    IMG_REF = 'img_ref'
    DENSITY = 'density'