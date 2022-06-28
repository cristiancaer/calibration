from queue import Queue
import sys
import cv2
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToSave, SavedInfo
from APP.MAKEDATASET.control.loop_event_manager import LoopEventManager, SignalHandler


class SaveHandler():
    
    def __init__(self, event_manager:LoopEventManager, path: str = None, datetime_index: bool = False):
        """object to store rgb-d images. to save a new pair the object has the function add_new, the images must came in the DataToSave object
        
        when the new pair is stored, the object has the last_index(signalHandler) to Know the name of the last saved
        Args:
            event_manager (LoopEventManager): used to put a loop function, which will be in charge of the save the images, in a loop inside of a Thread
            path (str, optional): optional in constructor but required to save. Defaults to None.
            datetime_index (bool, optional): optional in constructor but required to save. if data_index = False the object will use a int as index_name of the image, if datetime_index = True, the object will use the hour as index_name Defaults to False.
        """
        super().__init__()
        self.SIZE_BUFFER = 200
        self.set_index_type(datetime_index)
        self.set_path(path)
        self.index = 0
        self.queue = Queue(self.SIZE_BUFFER)
        self.is_running = True
        self.FORMAT = '.png'
        self.saturation_times = 0
        self.saturated = False
        self.last_size_buffer = None
        self.saved_info = SignalHandler('last_saved_image_index', SavedInfo)
        event_manager.add_signal_handler(self.saved_info)
        event_manager.emit_function_only_once(self.loop_task, wrap_in_loop= True)
        
        
    def add_new(self, data_to_save: DataToSave):
        """ add new data to stor in disc"""
        self.queue.put(data_to_save)
        
    def set_path(self, path: str)-> None:
        self.path = path
        
    def set_index_type(self, datetime_index: bool):
        """_summary_

        Args:
        datetime_index (bool, optional): optional in constructor but required to save. if data_index = False the object will use a int as index_name of the image, if datetime_index = True, the object will use the hour as index_name Defaults to False.

        """
        self.use_datetime_index = datetime_index
        
    def _get_last_pair(self)-> DataToSave:
        if not self.is_running:
            return
        return self.queue.get()
    
    def loop_task(self):
        data_to_save = self._get_last_pair()
        if data_to_save is not None:
            if self.use_datetime_index:
                index = data_to_save.hour
            else:
                index = str(self.index )
                self.index+= 1
            for key, image in data_to_save.data.items():
                path_name = f'{self.path}/{key}_{index}{self.FORMAT}'
                ret = cv2.imwrite(path_name, image)
            
            size_buffer = self.queue.qsize()
            if (size_buffer > self.SIZE_BUFFER/2) and (not self.saturated):
                self.saturated = True
                self.saturation_times += 1
               
            elif(size_buffer < self.SIZE_BUFFER/2):
                self.saturated = False
            
            last_index = None
            if ret:
                last_index = index[11:-3] if self.use_datetime_index else index# only hours-minutes-milliseconds
            
            saved_info = SavedInfo(last_index, size_buffer,self.saturation_times)
            self.saved_info.emit(saved_info)

    def close(self):
        self.is_running = False
        self.queue.put(None)
        print('thread to save images closed')
        

#TEST
################################################################################

if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    from APP.MAKEDATASET.views.panel_to_save import PanelToSave
    import numpy as np
    
    event_manager = LoopEventManager('manager')
    event_manager.start()
    
    app = QApplication(sys.argv)
    path= 'test_folder'
    window = PanelToSave(path= path)
    
    save_handler = SaveHandler(event_manager,path, datetime_index=False)
    
    img = np.ones((480, 640, 3), dtype=np.uint16)
    data_to_save = DataToSave(DataFromAcquisition(img, 1000*img))
    n = 3
    for _ in range(n):
        save_handler.add_new(data_to_save)
    save_handler.last_index.connect(window.line_edit_last_saved.update_text)
    window.show()
    app.exec_()
    save_handler.close()
    event_manager.stop()
    sys.exit()
    