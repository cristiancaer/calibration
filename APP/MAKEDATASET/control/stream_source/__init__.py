import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition

class Stream:
    name: str = None
    is_working: bool = False  # to inform that the stream has not crashed
    mesage: str = ''  # any usefull information
    setup_done: bool = False  # to know if the basic-configuration was made.

    def get_name(self) -> str:
        """

        Returns:
            str: name of the stream: camara-name,test,...
        """
        return self.name

    def get_stream_data(self) -> DataFromAcquisition:
        """
        to get an object that have the image-pair(rgb,depth)

        Returns:
            DataFromAcquisition: object with an rgb-image,depth-image and the acquisition datatime
        """
        pass

    def stop(self) -> None:
        """
        to release the resources. Have in main that this must be executed when the camara connection crash or when is need to manually close the connection.
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
        to release the resources. Have in main that this must be executed when the camara connection crash or when is need to manually close the connection.
        """
        pass
