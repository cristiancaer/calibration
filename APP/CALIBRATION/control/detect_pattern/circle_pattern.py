from curses import window
from typing import List
import cv2
import sys
import numpy as np
sys.path.append('./')
from APP.CALIBRATION.models.data_objects import ImgTypeNames
from APP.control import depth2uint8
from APP.CALIBRATION.control.detect_pattern.circle_detector import get_circle_detector


class CirclePoints:
    def __init__(self, nrow: int, ncolumn: int)->None:
        self.nrow = nrow
        self.ncolumn = ncolumn
        self.circle_detector = get_circle_detector()
    
    def improve_depth(self, depth_img: np.ndarray) -> np.ndarray:
        """remove the background (depth range filter). near pixels will be consider as the interest object, distant pixels will be consider as background
        """
        improved_img = depth_img.copy()
        improved_img = depth2uint8(improved_img)
        
        improved_img[np.where(improved_img==0)] = improved_img.max()# the missing pixels will join to background
    
        _, mask = cv2.threshold(improved_img,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        improved_img = depth_img.copy()*mask
    
        return improved_img
    
    def sort_centers(self, centers: np.ndarray):
        #group by rows
        centers = centers.reshape(self.nrow,self.ncolumn,2)
        dtype=[("x",float),("y",float)]
        #sort row points from left to right
        for i in range(self.nrow):
            for j in range(self.ncolumn):
                for k in range(j+1,self.ncolumn):
                    buffer = centers[i,j].copy()
                    if (buffer[0]-centers[i,k,0])>0:
                        centers[i,j]=centers[i,k]
                        centers[i,k]=buffer
                        
        #sort rows from top to bottom
        for i in range(self.nrow):
            for j in range(i+1, self.nrow):
                buffer = centers[i].copy()
                if (buffer[0,1]-centers[j,0,1])>0:
                    centers[i] = centers[j]
                    centers[j] = centers
        #return to the original shape
        centers = centers.reshape(self.nrow*self.ncolumn,1,2)
        return centers

    def get_points_between_circles(self,centers):   
        #find mid point between circles
        
        centers_row = centers.copy().reshape(self.nrow, self.ncolumn, 2)# centers sorted by row
        mid_centers=[]
        for row in range(self.nrow):
            for col in range(self.ncolumn-1):
                mid=(centers_row[row,col]+centers_row[row,col+1])/2
                mid_centers.append([mid])
        mid_centers=np.array(mid_centers)
        return mid_centers
    
    def get_center_circle_points(self, img: np.ndarray, is_depth: bool=False):
        if not is_depth:
            one_chanel_img = cv2.cvtColor(img.copy(),cv2.COLOR_BGR2GRAY)
        else:
            one_chanel_img = self.improve_depth(img)
        #find centers
        ret, centers = cv2.findCirclesGrid(one_chanel_img, (self.ncolumn,self.nrow), None, flags = cv2.CALIB_CB_ASYMMETRIC_GRID, blobDetector=self.circle_detector)
        if  ret:
            centers=self.sort_centers(centers)
    
        return ret,centers
    
    def get_object_points(self, diameter:float)-> np.ndarray:
        """_summary_

        Args:
            diameter (float): distance between mid circle points. 

        Returns:
            np.ndarray: shape[nrow*ncolumn,1,2]. has points like 0,0,0), (1,0,0), (2,0,0)...., (6,5,0), if nrow=6 and ncolumn=5
        """
        object_points = np.zeros((self.nf*self.nc,3), np.float32)# 3 is due to (x,y,z)
        object_points[:,:2] = np.mgrid[0:self.nc,0:self.nf].T.reshape(-1,2)# make a chessboard grid

        # make coord plane having in main the pattern measures and its asymmetric shape
        object_points=object_points.reshape(self.nf,self.nc,3)
        for i in range(self.nf):
            # distance between rows
          object_points[i,:,1]=self.d*object_points[i,:,1]
        #distance between the mid point of the circles at the same row
          if i%2==0:
            object_points[i,:,0]=self.d*2*object_points[i,:,0]
          else:# moved rows
            object_points[i,:,0]=self.d*2*object_points[i,:,0]+self.d
        object_points=object_points.reshape(self.nf*self.nc,3) 
        return object_points

    def draw_centers(self, img: np.ndarray, centers: np.ndarray) -> np.ndarray:
        return self._draw_points(img,centers)
    
    def draw_points_between_circles(self, img: np.ndarray, points_between_circles: np.ndarray) -> np.ndarray:
        return self._draw_points(img, points_between_circles, True)
        
    def _draw_points(self, img:np.ndarray, points:np.ndarray, are_points_between_circles=False) -> np.ndarray:
        ncolum = self.ncolumn
        if are_points_between_circles:
            ncolum -= 1 # A column is lost,  when we calc the points_between_circles
        img = cv2.drawChessboardCorners(img, (ncolum, self.nrow), points, True)
        return img
    
#TEST
################################################################################
if __name__=='__main__':
    from APP.CALIBRATION.control.app_panels.img_media import ImageMedia
    from APP.CALIBRATION.control.files.names_handler import NamesHandler
    from APP.models.basic_config import TEST_IMG_PATH
    from APP.CALIBRATION.models.data_objects import ImgData
    from PyQt5.QtWidgets import QApplication
    
    def f_process(img_data: ImgData):
        rgb = img_data.images.get(ImgTypeNames.rgb)
        
        if rgb is not None:
            ret, centers = detect_pattern.get_center_circle_points(rgb)
            if ret:
                rgb = detect_pattern.draw_centers(rgb, centers)
                img_data.images[ImgTypeNames.rgb] = rgb
            else:
                print('there was not circle detection')
        return img_data
    
    names_handler = NamesHandler(TEST_IMG_PATH, rgb_prefix='rgb')
    detect_pattern = CirclePoints(nrow= 9, ncolumn=6)
    app = QApplication(sys.argv)
    window = ImageMedia(names_handler, f_process, list_img_names=[ImgTypeNames.rgb])
    window.show()
    sys.exit(app.exec())