
from PyQt5.QtWidgets import QWidget, QLineEdit, QHBoxLayout, QApplication, QSizePolicy, QGroupBox, QSpacerItem
from PyQt5.QtCore import Qt
import sys
sys.path.append('./')
from app.views.pyqt.basic import LabelFont

class PanelOneMeasure(QWidget):
    def __init__(self, measure_name: str) -> None:
        """
        panel to show the name and the value of only one measure

        Args:
            measure_name (str): name of measure
        """
        super().__init__()
        self.name = measure_name
        self.setup_gui()

    def setup_gui(self):
        self.box = QGroupBox(self.name, font=LabelFont())
        layout = QHBoxLayout(self.box)
        self.line_edit = QLineEdit()
        self.line_edit.setMinimumWidth(200)
        layout.addWidget(self.line_edit)
        horizontal_spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addItem(horizontal_spacer)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.box)
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


#TEST
################################################################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PanelOneMeasure('measure1')
    window.show()
    sys.exit(app.exec_())
