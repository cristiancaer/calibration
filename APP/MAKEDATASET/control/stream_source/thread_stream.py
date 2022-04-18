from typing import Dict, List
from unicodedata import name
from PyQt5.QtCore import QThread, pyqtSignal
from time import sleep
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToShow
from APP.MAKEDATASET.control.stream_source import Stream


class ThreadToStream(QThread):
    data_ready = pyqtSignal(DataFromAcquisition)
    def __init__(self)->None:
        """
        Thread to generate an stream from an Stream object
        when the data is ready the  data_ready(pyqtSingal) is emitted with a DataFromAcquisition Object
        """
        super().__init__()
        self.is_running = True# loop condition 
        self.stop = True# start with a stopped acquisition
        self.actual_stream: Stream = None
        self.possible_streams: List[Stream] = []
        self.available_streams: Dict[str, Stream] = {}
    
    def add_stream(self, stream: Stream):
        self.possible_streams.append(stream)
    
    def update_availables(self):
        for stream in self.possible_streams:
            if stream != self.actual_stream:
                stream.setup()
                if stream.setup_done:
                    stream.close()
                    self.available_streams.update({stream.name:stream})
                else:
                    if stream.name in self.available_streams:
                        self.available_streams.pop(stream.name)
     
    def set_stop(self, flat: bool= True):
        self.stop = flat
        
    def set_stream(self, stream_name: str= None):
        """ 
        Args:
            new_stream (Stream, optional): Stream Object where get the rgb-dept  pair image, if not args is given, it try to setup the last Stream given. Defaults to None.
        """
        
        self.stop = True
        sleep(0.1)
        if hasattr(self.actual_stream, 'close'):
            self.actual_stream.close()

        if not stream_name:
            # Try to reconnect the actual stream
            new_stream = self.actual_stream
        else:
            new_stream = self.available_streams.get(stream_name)

        if isinstance(new_stream, Stream):
            print(f'stream from : {new_stream.name}')
            new_stream.setup()
            self.actual_stream = new_stream
            sleep(0.1)
            if new_stream.setup_done:
                self.stop = False
            else:
                self.stop = True
                self.message = f'Stream with name ({new_stream.name}) cannot be configured'
                print(self.message)
            
    def run(self) -> None:
        while self.is_running:
            if not self.stop:
                if self.actual_stream:
                    data = self.actual_stream.get_stream_data()
                    if data:
                        self.data_ready.emit(data)
                    else:
                        self.stop = True
                        self.message = f' stream with name ({self.actual_stream.name}) is disconnected'
                        print(self.actual_stream)
    
    def close(self):
        self.stop = True
        self.is_running = False
    
    def get_available_stream_names(self)-> List[str]:
        self.update_availables()
        return list(self.available_streams.keys())

POSSIBLE_STREAM: Dict[str, Stream]= {}

#TEST
################################################################################


def test_stream( stream_class: Stream):
    from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
    from PyQt5.QtWidgets import QApplication, QWidget
    
    class TestWindow(PanelRGBDImage):
        def __init__(self,parent: QWidget= None)->None:
            super().__init__()
            
        def update(self,data: DataFromAcquisition):
            zmin, zmax = self.panel_visualization_range.get_range()
            data = DataToShow(data_acquisition=data, zmin=zmin, zmax=zmax)
            self.update_rgbd(data)
        
        
            
    app = QApplication(sys.argv)
    camara = stream_class()
    thread_stream = ThreadToStream()
    thread_stream.start()
    thread_stream.add_stream(camara)
    thread_stream.update_availables()
    thread_stream.set_stream(camara.name)
    window = TestWindow()
    window.show()
    thread_stream.data_ready.connect(window.update)
    window.button_reconnect_stream.clicked.connect(lambda:thread_stream.set_stream())
    sys.exit(app.exec_())