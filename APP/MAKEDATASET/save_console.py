import sys
sys.path.append('./')
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455, Stream
from APP.MAKEDATASET.control.stream_source.orbbec import Orbbec
from APP.MAKEDATASET.control.stream_source.stream_handler import StreamHandler
from APP.MAKEDATASET.control.loop_event_manager import LoopEventManager
from APP.MAKEDATASET.control.save_pair_images import SaveHandler
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToSave
import os

class Save:
    def __init__(self, stream_class:Stream, path:str)->None:
        self.event_manager = LoopEventManager('event_manager')
        self.stream_handler = StreamHandler(self.event_manager)
        camera = stream_class()
        self.stream_handler.add_stream(camera, check_is_available=True)
        self.stream_handler.set_stream(camera.name)
        self.stream_handler.data_ready.connect(self.make_save)
        self.first_saved = None
        
        self.save_handler = SaveHandler(self.event_manager, path, datetime_index=True)
        self.save_handler.last_index.connect(self.console)
        self.fps = 0
    def make_save(self, data: DataFromAcquisition):
        data_to_save = DataToSave(data)
        self.save_handler.add_new(data_to_save)
        self.fps = data.fps
        
    def console(self, last_saved:str):
        if self.first_saved is None:
            self.first_saved = last_saved
        os.system('clear')
        print(f'fps: {self.fps: .2f}; buffer to save: {self.save_handler.queue.qsize()}')
        
        print('first saved')
        print(self.first_saved)
        print(f'last saved')
        print(last_saved)
    
    def start(self):
        self.event_manager.start()
    def close(self):
        self.stream_handler.close()
        self.save_handler.close()
        self.event_manager.stop()


#TEST
################################################################################
if __name__=='__main__':
    path = '/home/ingelec2/Desktop/flujoBagazo/codigo/app_calibration/test/'
    save = Save(Orbbec, path)
    save.start()
    while True:
        key = input()
        if key == 'q':
            save.close()
            break
        