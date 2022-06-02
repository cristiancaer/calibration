import sys
sys.path.append('./')
from APP.MAKEDATASET.models import  RGB_PREFIX, DEPTH_PREFIX, TEST_IMG_PATH
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition
from APP.MAKEDATASET.control.stream_source import Stream
from typing import List, Tuple
import glob
import cv2



class ImageGenerator(Stream):
    name = 'Test'

    def __init__(self, path: str= TEST_IMG_PATH , rgb_prefix: str= RGB_PREFIX, depth_prefix: str= DEPTH_PREFIX) -> None:
        """
            used to open from a directory a rgb-depth image pair. 
            to re-pair  the pair RGB-DEPTH image. the images must have the same index.
            this class is going to charge only the name of the image pair and read the image when is needed

        Args:
            path: path to the directory where image are stored.
            rgb_prefix: specify rgb image type. the name image must have the format: rgb-prefix_index.png. E.g RGB_1.png.
            depth_prefix: specify depth image type. the name image must have the format: depth-prefix_index.png. E.g depth_1.png.

        """
        self.message = ""  # to comunacate if something is not going well
        self.change_source(path, rgb_prefix, depth_prefix)
        self.name_pairs: List[Tuple[str]] = []    
        
    def setup(self):
        names_RGB = self.get_image_names(self.path, self.rgb_prefix)
        names_depth = self.get_image_names(self.path, self.depth_prefix)
        self.name_pairs.clear()
        if len(names_RGB) == len(names_depth):
            self.name_pairs = list(zip(names_RGB, names_depth))
        else:
            self.message = f'there are {len(names_RGB)} rgb and {len(names_depth)} depth images. which is not allow'
            print(self.message)
        self.index_img = 0
        self.setup_done = True

    def get_image_names(self, path: str, prefix: str) -> list:
        """
        Get and sort all images according  a prefix.
        to get and sort the images, sorting is made by a number/index in name-image, the name img must have  an index preceded by '_'.
        the image name must have the follow format. 
        
        type_index examples: 
        RGB_1.png,RGB_2.png, depth_3.png, where RGB and depth are possible prefix types, and the number is the index.

        Args:
            path: path to directory.
            prefix (str): specify the type of image.

        Returns:
            list: list with all the image that have the prefix required in their name.
        """
        names = glob.glob('{}{}*.png'.format(path, prefix))
        print(f'image number of {prefix}: {len(names)}')
        if not names:
            self.message = 'Warning: There are not test images!. Check if test image folder exist'
            print(self.message)
        buffer_names = {}
        #sort names
        for name in names:
            name_without_path = name[name.rfind('/')+1:]  # remove path from name: path/to_img/rgb_1.png -->rgb_1.png
            name_without_format_img = name_without_path[:-4]  # remove .png from name, RGB_1.png --> RGB_1
            index = int(name_without_format_img.split('_')[1])  # after split: [[rgb],[1]]
            buffer_names.update({index: name})
        sorted_names = sorted(buffer_names.items())  # this is ordered by its keys and  it  has the key and the value stored,
        sorted_names = [name for index, name in sorted_names]  # stract only the values/names
        return sorted_names

    def get_stream_data(self) -> DataFromAcquisition:
        """ 
        to get object that have the image-pair

        returns:
            DataFromAcquisition: DataObject that store an rgb and a depth image and the acquisition  time
        """
        try:
            rgb_name, depth_name = self.name_pairs[self.index_img]
            rgb = cv2.imread(rgb_name)
            depth = cv2.imread(depth_name, cv2.IMREAD_UNCHANGED)
            self.update_index()
            self.is_working = True
            return DataFromAcquisition(rgb, depth)
        except:
            self.close()
            return None

    def update_index(self):
        """ update the index_img to read 
        """
        self.index_img += 1
        if self.index_img == len(self.name_pairs):
            self.index_img = 0

    def change_source(self, path: str, rgb_prefix: str, depth_prefix: str) -> None:
        """
        change the source where the images are read

        Args:
            path: path to the directory where image are stored.
            rgb_prefix: specify rgb image type. the name image must have the format: prefix_index.png. E.g RGB_1.png.
            depth_prefix: specify depth image type. the name image must have the format: prefix_index.png. E.g depth_1.png.

        """
        self.path = path
        self.rgb_prefix = rgb_prefix
        self.depth_prefix = depth_prefix
    
    def close(self) -> None:
        self.is_working = False
        # self.name_pairs.clear()

#TEST
################################################################################
def run():
    from APP.MAKEDATASET.control.stream_source.thread_stream import test_stream
    test_stream(ImageGenerator)
if __name__ == '__main__':
    run()
