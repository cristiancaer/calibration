from time import  sleep
import numpy as np
from openni import _openni2 as c_api
from openni import openni2
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.control.stream_source import Stream
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition


class Orbbec(Stream):
    name = 'Orbbec'
    depth_units = '100um'
    def __init__(self) -> None:
        """
        get object to handle an stream from  the  orbbec camara
        """
        # Initialize the  device
        self.dev = None
        self.setup_done = False

    def setup(self) -> None:
        """
        init config to make a connection with the orbbec camara
        """
        openni2.initialize()
        # Start the depth stream
        try:
            self.dev = openni2.Device.open_any()
            self.depth_stream = self.dev.create_depth_stream()
            self.depth_stream.start()
            self.depth_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_DEPTH_100_UM, resolutionX=640, resolutionY=480, fps=30))
            self.rgb_stream = self.dev.create_color_stream()
            self.rgb_stream.set_video_mode(c_api.OniVideoMode(pixelFormat=c_api.OniPixelFormat.ONI_PIXEL_FORMAT_RGB888, resolutionX=640, resolutionY=480, fps=30))
            self.rgb_stream.start()
            self.setup_done = True
            self.TIME_TO_SLEEP = 1/1000
        except Exception:
            self.setup_done = False
            print('no orbbec device was found')

    def get_rgb(self) -> np.ndarray:
        """get rgb-frame from rgb stream

        Returns:
            np.ndarray: 3 chanel image. uint8 dataType
        """

        bgr = np.frombuffer(self.rgb_stream.read_frame().get_buffer_as_uint16(), dtype=np.uint8).reshape(480, 640, 3)
        sleep(self.TIME_TO_SLEEP)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        return rgb

            
    def get_depth(self) -> np.ndarray:
        """get depth-frame form depth-stream

        Returns:
            np.ndarray: 3 chanel image. uint16 dataType
        """
        depth = np.frombuffer(self.depth_stream.read_frame().get_buffer_as_uint16(), dtype=np.uint16)
        sleep(self.TIME_TO_SLEEP)
        depth.shape = (480, 640)
        # cv2.imshow("h",depth)
        depth = cv2.merge([depth, depth, depth])  # for some reason when the union/merge of the three chanel is not make the are information lost in the depth-image.
        return depth[:, :, 0]

    def get_stream_data(self) -> DataFromAcquisition:
        """ 
        to get object that have the image-pair

        returns:
            DataFromAcquisition: DataObject that store an rgb and a depth image and the acquisition  time
        """
        
        try:
            rgb = self.get_rgb()
            depth = self.get_depth()
            data = DataFromAcquisition(rgb=rgb, depth=depth)
            self.is_working = True
        except:
            self.close()
            data= None
        finally:
            return data

    def close(self):
        """ close stream and drivers"""
        if self.setup_done:
            try:
                openni2.unload()
                self.dev.close()
                self.setup_done = False
                self.is_working = False
            except Exception:
                print('devise disconnected')


#TEST
################################################################################
def run():
    from APP.MAKEDATASET.control.stream_source.thread_stream import test_stream
    test_stream(Orbbec)
if __name__ == '__main__':
    run()
