from PyQt5.QtWidgets import QWidget, QStackedWidget, QGridLayout
from typing import List

class StackWidget(QWidget):
    def __init__(self, parent: QWidget= None):
        """panel that  consider all  available panels like pages. the page change is through  back and next buttons

        Args:
            parent (QWidget, optional): _description_. Defaults to None.
        """
        super().__init__(parent=parent)
        self.list_panels: List[QWidget] = []
        self.last_index = [0]
        layout = QGridLayout(self)
        self.stack = QStackedWidget ()
        layout.addWidget(self.stack)
        self.init_gui()
    
    def init_gui(self):
        for panel in self.list_panels:
            if hasattr(panel,'back_next_buttons'):
                panel.back_next_buttons.back.clicked.connect(self.go_to_panel)
   
    def add_panel(self, panel: QWidget):
        self.list_panels.append(panel)
        self.stack.addWidget(panel)
    
    def go_to_panel(self, panel: QWidget = None):
        """ if no args: all panel that have a back button will conduce to the last_index stored """
        if panel:
            self.update_panels_context()
            index = self.list_panels.index(panel)
            self.last_index.append(index)
        else:
            if self.last_index:
                self.last_index.pop()
                index = self.last_index[-1]
            else:
                index = 0
        self.stack.setCurrentIndex(index)
        
        
    def update_panels_context(self):
        self.dataset_type = self.panel_dataset_type.get_selected()