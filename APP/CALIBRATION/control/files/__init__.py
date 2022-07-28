from glob import glob
from typing import List, Set
import numpy as np
import cv2
import sys
sys.path.append('./')
from APP.models.basic_config import TEST_IMG_PATH


def get_prefix_from_name(name: str) -> str:
    """get prefix, example rgb_1.png -> rgb

    Args:
        name (str): must have the format prefix_index.png

    Returns:
        str: prefix
    """
    name_split = name.split('_')
    return name_split[0]

def detect_prefixes(path: str) -> Set[str]:
    path_names = glob(f'{path}/*.png')
    prefixes = list(set([get_prefix_from_name(pathname[len(path):]) for pathname in path_names]))
    possible_rgb = []
    possible_depth = []
    for prefix in prefixes:
            path_names = glob(f'{path}/{prefix}_*.png')
            test_img = cv2.imread(path_names[0], cv2.IMREAD_UNCHANGED)
            if not isinstance(test_img, np.ndarray):
                continue
            if test_img.dtype == np.uint16:
                possible_depth.append(prefix)
            else:
                possible_rgb.append(prefix)
    
    rgb_prefix = None
    depth_prefix = None
    if possible_rgb:
        rgb_prefix = possible_rgb[0]
        
    if possible_depth:
        depth_prefix = possible_depth[0]
    return rgb_prefix, depth_prefix

def get_list_index(path: str, prefix: str):
    """the images in the directory must have the following format prefix_index.png. example rgb_1.png
    """
    path_names = glob(f'{path}/{prefix}_*.png')
    list_index = [get_index(pathname[len(path):]) for pathname in path_names]
    return list_index

def get_index(name: str) -> int:
    """ name=prefix_index.png
        splitted_name = ['prefix','_index.png']
        index = index
    """
    splitted_name = name.split('_')
    index = splitted_name[1][:-4]
    return int(index)
#TEST
################################################################################
if __name__=='__main__':
    print(detect_prefixes(TEST_IMG_PATH))