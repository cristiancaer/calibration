from typing import List, Tuple
import numpy as np
import sys
import cv2
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import seaborn as sb
import io
sys.path.append('./')
from APP.models.basic_config import ZMAX, ZMIN

def get_uv_coords(shape: np.ndarray) -> Tuple[np.ndarray]:
    """

    Args:
        shape (np.ndarray): [heigh, width]

    Returns:
        Tuple[np.ndarray]: [u,v]
    """
    v, u = np.mgrid[0:shape[1], 0:shape[0]]
    return u, v


def norm(array: np.ndarray, zmin: float = ZMIN, zmax: float = ZMAX) -> np.ndarray:
    norm_array = (array.astype(float)-zmin)/(zmax - zmin)
    return norm_array


def denorm(norm_array: np.ndarray, zmin: float = ZMIN, zmax: float = ZMAX) -> np.ndarray:
    array = norm_array*(zmax-zmin) + zmin
    return array


def recover(depth_img: np.ndarray) -> np.ndarray:
    mask = depth_img.copy()
    mask[mask < 3000] = 1
    mask[mask != 1] = 0
    mask = mask.astype(np.uint8)
    recovered_img = cv2.inpaint(depth_img.copy(), mask, 1, cv2.INPAINT_TELEA)
    return recovered_img

def get_img_from_fig(fig, dpi=180):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img

def get_max_contrast_fig(list_imgs: np.ndarray, ncol: int, nrow: int, list_titles: List[str]=None):
        if list_titles is None:
            list_titles = []
        nImg=len(list_imgs)
        nTitles=len(list_titles)
        if nTitles!=0 and nTitles!=nImg:
            print("numero de titulos incorrecto")
        fig, ax = plt.subplots(nrow,ncol,figsize=(20,7))
        img0=list_imgs[0]
        std=img0.std()
        vmin=img0.mean()-std
        vmax=img0.mean()+std
        for i,img in enumerate(list_imgs):
            heat_map = sb.heatmap(img,vmin=vmin,vmax=vmax,ax=ax[i],yticklabels=False,xticklabels=False)
            
            if nTitles>0 : 
                ax[i].set_title(list_titles[i],fontsize=20)
        plt.show()
        return fig