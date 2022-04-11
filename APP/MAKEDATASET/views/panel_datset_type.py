from PyQt5.QtWidgets import QComboBox
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.card_template import CardTemplate
from APP.MAKEDATASET.models.data_objects import DATASET_TYPES

class PanelDatasetType(CardTemplate):
    def __init__(self):
        super().__init__(title='Make Dataset')
        self.selected_type: str = None
        
    def init_gui(self):
        super().init_gui()
        self.combobox_datasets = QComboBox()
        self.combobox_datasets
        self.combobox_datasets.addItems(DATASET_TYPES.as_list())
        self.set_central_widget(self.combobox_datasets)
        
    def get_selected(self)-> str:
        self.selected_type = self.combobox_datasets.currentText()
        return self.selected_type
    
    
#TEST


if __name__=='__main__':
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = PanelDatasetType()
    window.show()
    sys.exit(app.exec_())