import sys
from time import time
from typing import Tuple
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition

class Stream:
    name: str = None
    is_working: bool = False  # to inform that the stream has not crashed
    message: str = ''  # any useful information
    setup_done: bool = False  # to know if the basic-configuration was made.
    depth_units: str = '' # to know the original units of the depth stream
    shape: Tuple[int] = ()# image shape
    last_time: float = 0# variable to calc fps. time of the last image ready
    
    def __eq__(self, __o: object) -> bool:
        if not hasattr(__o, 'name'):
            return False
        return self.name == __o.name
    
    def __ne__(self, __o: object)-> bool:
        return not self.__eq__(__o)
    
    def get_name(self) -> str:
        """

        Returns:
            str: name of the stream: camera-name,test,...
        """
        return self.name

    def get_stream_data(self) -> DataFromAcquisition:
        """
        to get an object that have the image-pair(rgb,depth)

        Returns:
            DataFromAcquisition: object with an rgb-image,depth-image and the acquisition datetime
        """
        pass

    def stop(self) -> None:
        """
        to release the resources. Have in main that this must be executed when the camera connection crash or when is need to manually close the connection.
        """
        pass

    def get_status(self) -> str:
        """to know if the object has  crashed

        Returns:
            bool: if it is true there are no problems with the connection.
        """
        return self.is_working

    def setup(self) -> None:
        """
        to setup the needed config to get the image-pair
        """
        pass

    def close(self) -> None:
        """
        to release the resources. Have in main that this must be executed when the camera connection crash or when is need to manually close the connection.
        """
        pass
    
    def get_fps(self) -> float:
        period = time()- self.last_time
        fps = 1/period
        self.last_time = time()
        return fps