from PyQt5.QtWidgets import QFileDialog, QLabel
from PyQt5.QtCore import pyqtSlot,Qt
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.card_template import CardTemplate
from APP.MAKEDATASET.views.basic.buttons import ButtonGetDir



class PanelDatasetType(CardTemplate):
    def __init__(self):
        """
        a panel where the user will select a dir where the app will save the image
        """
        super().__init__(title='Select Path to save images')
        self.selected_type: str = None
        self.path: str = None
        
    def init_gui(self):
        super().init_gui()
        self.button_path = ButtonGetDir()
        self.button_path.button.clicked.connect(self.get_path)
        self.set_central_widget(self.button_path)

    @pyqtSlot()
    def get_path(self):
        self.path = QFileDialog.getExistingDirectory()
        self.button_path.set_text(self.path)
        print(self.path)
    
    
#TEST

if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PanelDatasetType()
    window.show()
    sys.exit(app.exec_())