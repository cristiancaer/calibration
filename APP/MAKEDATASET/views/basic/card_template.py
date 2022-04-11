from PyQt5.QtWidgets import QWidget, QApplication, QGridLayout, QSpacerItem, QSizePolicy, QLabel
from PyQt5.QtCore import Qt
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic import LabelFont
from APP.MAKEDATASET.views.basic.buttons import BackNextButtons

class CardTemplate(QWidget):
    def __init__(self, title: str, central_widget: QWidget= None, parent: QWidget= None):
        super().__init__(parent=parent)
        self.grid_layout = QGridLayout(self)
        self.centralwidget = central_widget
        self.title = title
        self.init_gui()
        
    def init_gui(self):
        # 4x5 GRID
        ##########
        # 1x2 element
        horizontal_spacer = QSpacerItem(100, 100, QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grid_layout.addItem(horizontal_spacer, 0, 0, 1, 2)
        title = QLabel(self.title)
        font = LabelFont()
        font.setPixelSize(50)
        title.setFont(font)
        title.setAlignment(Qt.AlignCenter)
        # 1x1 element
        self.grid_layout.addWidget(title, 0, 2, 1, 1)
        # 1x2 element
        self.grid_layout.addItem(horizontal_spacer, 0, 3, 1, 2)
        # 1x1 element  VARIABLE CENTRAL WIDGET
        if self.centralwidget:
            self.set_central_widget(self.centralwidget)
         # 1x1 element
        self.back_next_buttons = BackNextButtons()
        self.grid_layout.addWidget(self.back_next_buttons, 2, 2, 1, 1)
        # 1x1 element
        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding)
        # self.grid_layout.addItem(vertical_spacer, 3,0,1,1)
    def set_central_widget(self, widget: QWidget):
        self.centralwidget = widget
        self.grid_layout.addWidget(self.centralwidget, 1, 2, 1, 1)
        
        
#TEST

if __name__=='__main__':
    from PyQt5.QtWidgets import QPushButton
    app = QApplication(sys.argv)
    test_button = QPushButton('test select')
    window = CardTemplate('Make Dataset')
    window.set_central_widget(test_button)
    window.show()
    sys.exit(app.exec_())