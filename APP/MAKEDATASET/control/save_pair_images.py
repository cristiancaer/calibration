from PyQt5.QtCore import QThread, pyqtSignal
from queue import Queue
import sys
import cv2
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition, DataToSave


class ThreadToSave(QThread):
    last_index = pyqtSignal(str)
    
    def __init__(self, path: str, datatime_index: bool = False):
        super().__init__()
        self.use_datatime_index = datatime_index
        self.path = path
        self.index = 0
        self.queue = Queue(50)
        self.is_running = True
        self.FORTMAT = '.png'
        
    def add_new(self, data_to_save: DataToSave):
        self.queue.put(data_to_save)
        
    def get_last_pair(self)-> DataToSave:
        return self.queue.get()
    
    def run(self):
        while self.is_running:
            data_to_save = self.get_last_pair()
            if self.use_datatime_index:
                index = data_to_save.hour
            else:
                index = str(self.index )
                self.index+= 1
            for key, image in data_to_save.data.items():
                path_name = f'{self.path}/{key}_{index}{self.FORTMAT}'
                ret = cv2.imwrite(path_name, image)
            self.last_index.emit(index+self.FORTMAT)


#TEST
################################################################################

if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    from APP.MAKEDATASET.views.panel_to_save import PanelToSave
    import numpy as np
    app = QApplication(sys.argv)
    path= 'test_folder'
    window = PanelToSave(path= path)
    save_handler = ThreadToSave(path, datatime_index=False)
    img = np.ones((480, 640, 3), dtype=np.uint16)
    data_to_save = DataToSave(DataFromAcquisition(img, 1000*img))
    n = 3
    for _ in range(n):
        save_handler.add_new(data_to_save)
    save_handler.last_index.connect(window.line_edit_last_saved.update_text)
    window.show()
    save_handler.start()
    sys.exit(app.exec_())
    