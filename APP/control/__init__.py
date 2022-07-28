import numpy as np
import cv2
import sys
sys.path.append('./')
from APP.models.basic_config import ZMAX, ZMIN


def depth2color(depth_img: np.ndarray, zmin: int = ZMIN, zmax: int = ZMAX) -> np.ndarray:
    """to convert a one-chanel-depth image in a  3-chanel-color image to have a better visualization
    Args:
        depth_img (np.ndarray): one-chanel depth image
        zmin (int, optional): minimun  value o the z image used in normalization.
        zmax (int, optional): maximun value of the z image used in normalization
    Returns:
        np.ndarray: 3-chanel-color image
    """
    img = depth2uint8(depth_img, zmin, zmax)
    img = cv2.applyColorMap(img, cv2.COLORMAP_JET)
    return img

def depth2uint8(depth_img, zmin =ZMIN, zmax=ZMAX):
    """ transform uint16 depth image to uint8 one chanel image"""
    img = depth_img.astype(float)
    if len(depth_img.shape) > 2:
        img = img[:, :, 0]
    img = img.astype(float)
    img = 255*(img-zmin)/(zmax-zmin)
    img[img>255] = 255
    img[img<0] = 0
    img = img.astype(np.uint8)
    return img