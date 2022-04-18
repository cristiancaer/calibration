from typing import List
from PyQt5.QtWidgets import QComboBox, QWidget, QVBoxLayout, QPushButton
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.card_template import CardTemplate

class PanelSelectCamera(CardTemplate):
    name = 'select_camera'
    
    def __init__(self):
        """ Panel where the user will select the camera to get the rgb-d image pair
        """
        super().__init__(title='Select Camera')
        self.selected_type: str = None
        
    def init_gui(self):
        super().init_gui()
        # central widget
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        self.button_update_streams = QPushButton('Update Streams')
        layout.addWidget(self.button_update_streams)
        self.combobox_cameras = QComboBox()
        layout.addWidget(self.combobox_cameras)
        self.set_central_widget(central_widget)
        
    def get_selected(self)-> str:
        self.selected_type = self.combobox_cameras.currentText()
        return self.selected_type
    
    def update_available_streams(self, list_availables: List[str]):
        self.combobox_cameras.clear()
        self.combobox_cameras.addItems(list_availables)


#TEST
################################################################################

if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PanelSelectCamera()
    available_stream = ['test_camera1',
                        'test_camera2']
    window.button_update_streams.clicked.connect(lambda: window.update_available_streams(available_stream))
    window.show()
    sys.exit(app.exec_())