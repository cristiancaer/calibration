## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 Intel Corporation. All Rights Reserved.
from time import sleep
from typing import Tuple
import numpy as np
import pyrealsense2 as rs
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.control.stream_source import Stream
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition
from APP.MAKEDATASET.models import IMAGE_SHAPE
import traceback
from time import time

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
        try:
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
            depth_sensor.set_option(rs.option.depth_units,0.0001)
            depth_sensor.set_option(rs.option.emitter_enabled, 1)
            depth_sensor.set_option(rs.option.laser_power, 350)
            
            #config to align rgb-d
            align_to = rs.stream.depth
            self.aligner = rs.align(align_to)
            
            config.enable_stream(rs.stream.depth, self.shape[1], self.shape[0], rs.format.z16, 30)
            # config.enable_stream(rs.stream.infrared, 1, self.shape[1], self.shape[0], rs.format.y8, 30)
            config.enable_stream(rs.stream.color,self.shape[1], self.shape[0], rs.format.bgr8, 30)

            # Start streaming

            self.pipeline.start(config)
            self.config = config
            self.setup_done = True
            sleep(1)
            self.is_working = True
            
        except Exception:
            self.setup_done = False
            print('no intel device was found')
            print(traceback.format_exc())

    def get_stream_data(self) -> DataFromAcquisition:
        """ 
        to get object that have the image-pair

        returns:
            DataFromAcquisition: DataObject that store an rgb and a depth image and the acquisition  time
        """
        try:
            data = None
            if self.is_working:
                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()
                aligned_frames = self.aligner.process(frames)
                depth_frame = aligned_frames.get_depth_frame()
                color_frame = aligned_frames.get_color_frame()
                # color_frame = frames.get_infrared_frame()
                # Convert images to numpy arrays
                depth = np.asanyarray(depth_frame.get_data()).copy()
                rgb = np.asanyarray(color_frame.get_data()).copy()
                # rgb = cv2.merge((rgb,rgb,rgb))
                self.is_working = True
                fps = self.get_fps()
                data = DataFromAcquisition(rgb,depth, fps)
                
        except:
            data = None
            self.close()
            print(traceback.print_exc())
        finally:
            return data

    def close(self):
        """ close stream and drivers"""
        if self.setup_done:
            try:
                self.setup_done = False
                self.is_working = False
                sleep(0.1)
                self.config.disable_all_streams()
                sleep(0.1)
                self.pipeline.stop()
                del self.pipeline
                print(f'{self.name}  closed')
            except Exception:
                print('devise disconnected')
    

#TEST
################################################################################

if __name__=='__main__':
    from APP.MAKEDATASET.control.stream_source.stream_handler import test_stream
    test_stream(Intel455)