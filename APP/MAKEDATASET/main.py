from PyQt5.QtWidgets import QMainWindow, QWidget
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.integration import Integration
from APP.MAKEDATASET.control.stream_source.intel_455 import Intel455
from APP.MAKEDATASET.control.stream_source.orbbec import Orbbec
from APP.MAKEDATASET.control.stream_source.thread_stream import ThreadToStream



class MainWindow(QMainWindow):
    def __init__(self, window_name = '', parent: QWidget=None):
        super().__init__(parent)
        self.window_name = window_name
        self.init_gui()
        
    def init_gui(self):
        self.setWindowTitle(self.window_name)
        self.panels = Integration(self)
        self.centralWidget(self.panels)
        self.showMaximized()
        
    def setup(self):
        self.stream_handler = ThreadToStream()
        self.stream_handler.add_stream(Intel455())
        self.stream_handler.add_stream(Orbbec())
        