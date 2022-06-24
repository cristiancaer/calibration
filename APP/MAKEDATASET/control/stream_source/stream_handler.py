from asyncio import events
import traceback
import sys
from typing import Dict, List
from time import sleep
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
sys.path.append('./')
from APP.MAKEDATASET.control.loop_event_manager.futures_event_manager import FuturesLoopEventManager, SignalHandler
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToShow
from APP.MAKEDATASET.control.stream_source import Stream


class BasicStreamHandler:
    data_ready = None # signal which will be emitted when data from acquisition is ready
    def __init__(self)->None:
        """object to handler the source where the images rgb-d are acquired
        when the data is ready the  data_ready(SignalHandler) is emitted with a DataFromAcquisition Object
        """
        self.possible_streams: List[Stream]= []
        self.available_streams: Dict[str, Stream] = {}
        self.stop = True# start with acquisition stopped
        self.actual_stream = None
        
    def add_stream(self, stream: Stream, check_is_available: bool= False) -> None:
        """add a new possible stream
        """
        self.possible_streams.append(stream)
        if check_is_available:
            self.check_and_add_to_available_streams(stream)
        
    def get_available_stream_names(self) -> None:
        """ get the list of the source where the app can get images
        """
        self.update_available_streams()
        return list(self.available_streams.keys())

    def update_available_streams(self) -> None:
        for stream in self.possible_streams:
            if stream != self.actual_stream:
                self.check_and_add_to_available_streams(stream)

    def check_and_add_to_available_streams(self, stream:Stream):
        """ Try to setup the Stream if the setup is successful add the stream to the available streams
        """
        stream.setup()
        sleep(0.1)
        if stream.setup_done:
            print(stream.name, id(stream))
            stream.close()
            sleep(0.1)
            self.available_streams.update({stream.name:stream})
        else:
            if stream.name in self.available_streams:
                self.available_streams.pop(stream.name)
    
    def set_stream(self, stream_name: str= None) -> None:
        """ 
        Args:
            stream_name ('str', optional): Stream_name where to get the rgb-dept  pair image, if not args are given, it try to setup the last Stream given. Defaults to None.
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
                print('new stream id', stream_name, id(self.actual_stream))
            else:
                self.stop = True
                self.message = f'Stream with name ({new_stream.name}) cannot be configured'
                print(self.message)
    
    def close(self) -> None:
        self.stop = True
        sleep(1)
        if hasattr(self.actual_stream, 'close'):
            self.actual_stream.close()
        print('acquisition task closed')
    
    def acquisition_task(self) -> None:
        try:
             if not self.stop:
                if self.actual_stream:
                    data = self.actual_stream.get_stream_data()
                    if data:
                        self.data_ready.emit(data)
                    else:
                        self.stop = True
                        self.message = f' stream with name ({self.actual_stream.name}) is disconnected'
                        print(self.message)
        except:
            self.close()
            print(traceback.format_exc())

    def set_stop(self, flat: bool= True):
        self.stop = flat
    
    def disconnect_data_ready_slots(self):
        pass
    
class StreamHandler(BasicStreamHandler):
    def __init__(self, event_manager: FuturesLoopEventManager)->None:
        super().__init__()
        self.data_ready = SignalHandler('data_ready', DataFromAcquisition)
        event_manager.add_signal_handler(self.data_ready)
        event_manager.emit_function_only_once(self.acquisition_task, wrap_in_loop=True)
    
    def disconnect_data_ready_slots(self):
        self.data_ready.disconnect_all()
        
class QStreamHandler(QThread, BasicStreamHandler):
    data_ready = pyqtSignal(DataFromAcquisition)
    def __init__(self)->None:
        QThread.__init__(self)
        BasicStreamHandler.__init__(self)
        self.is_running = True
        
    def run(self) -> None:
        while self.is_running:
            self.acquisition_task()
        
    def closeTread(self) -> None:
        self.is_running = False
        super().close()
    
    def disconnect_data_ready_slots(self):
        self.data_ready.disconnect()
        
    
#TEST
################################################################################

def test_stream( stream_class: Stream):
    from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
    from PyQt5.QtWidgets import QApplication, QWidget
    from threading import Lock
    
    class TestWindow(PanelRGBDImage):
        update_acquisition = pyqtSignal(DataToShow)
        
        def __init__(self,parent: QWidget= None)->None:
            self.lock_visualization = Lock()
            super().__init__()
            self.update_acquisition.connect(self.update_rgbd)
        @pyqtSlot(DataFromAcquisition)     
        def update_images(self,data: DataFromAcquisition):
            with self.lock_visualization:
                zmin, zmax = self.panel_visualization_range.get_range()
                data = DataToShow(data_acquisition=data, zmin=zmin, zmax=zmax)
                self.update_acquisition.emit(data)
                
        
        def closeEvent(self, event) -> None:
            camera.close()
            stream_handler.close()
            event_manager.stop()
            return super().closeEvent(event)
        
       
    app = QApplication(sys.argv)
    event_manager = FuturesLoopEventManager('event manager')
    event_manager.start()
    camera = stream_class()
    stream_handler = StreamHandler(event_manager)
    stream_handler.add_stream(camera)
    stream_handler.update_available_streams()
    stream_handler.set_stream(camera.name)
    window = TestWindow()
    window.show()
    stream_handler.data_ready.connect(window.update_images)
    window.button_reconnect_stream.clicked.connect(lambda:stream_handler.set_stream())
    sys.exit(app.exec_())