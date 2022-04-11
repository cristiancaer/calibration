## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.

from typing import Tuple
import numpy as np
import pyrealsense2 as rs
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.control.stream_source import Stream
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition
from APP.MAKEDATASET.views import depth2color
from APP.MAKEDATASET.models import IMAGE_SHAPE

class Intel455(Stream):
    name = 'intel455'
    depth_units = '100um'
    def __init__(self) -> None:
        """
        get object to handle an stream from  the  Intel 455 camera
        """
        # Initialize the  device
        self.pipeline = None
        self.setup_done = False
        self.set_shape(IMAGE_SHAPE)
        
    def set_shape(self, shape: Tuple[int])-> None:
        """ setup image shape

        Args:
            shape (Tuple[int]): (heigh, width) of image
        """
        if len(shape) == 2:
            self.shape = shape
        else:
            self.shape = IMAGE_SHAPE
            
    def setup(self) -> None:
        """
        init config to make a connection with the Intel 455 camera
        """
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        
        # print(device)
        # config
        depth_sensor = device.first_depth_sensor()
        depth_sensor.set_option(rs.option.enable_auto_exposure,1)
        
        config.enable_stream(rs.stream.depth, self.shape[1], self.shape[0], rs.format.z16, 30)
        config.enable_stream(rs.stream.color,self.shape[1], self.shape[0], rs.format.bgr8, 30)

        # Start streaming
        try:
            self.pipeline.start(config)
            self.setup_done = True
        except Exception:
            self.setup_done = False
            print('no intel device was found')


    def get_stream_data(self) -> DataFromAcquisition:
        """ 
        to get object that have the image-pair

        returns:
            DataFromAcquisition: DataObject that store an rgb and a depth image and the acquisition  time
        """
        
        try:
            # Wait for a coherent pair of frames: depth and color
            frames = self.pipeline.wait_for_frames()
            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            # Convert images to numpy arrays
            rgb = np.asanyarray(depth_frame.get_data())
            depth = np.asanyarray(color_frame.get_data())
            self.is_working = True
            data = DataFromAcquisition(rgb,depth)
        except:
            self.close()
            data= None
        finally:
            return data

    def close(self):
        """ close stream and drivers"""
        if self.setup_done:
            try:
                self.pipeline.stop()
                self.setup_done = False
                self.is_working = False
            except Exception:
                print('devise disconnected')
