from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel,QWidget, QGroupBox, QHBoxLayout, QLineEdit, QSizePolicy, QSpacerItem, QSpinBox
from PyQt5.QtCore import Qt


class LabelFont(QFont):
    def __init__(self):
        super().__init__()
        self.setBold(True)
        self.setWeight(75)


class CustomLabel(QLabel):
    def __init__(self, text: str= '', center: bool= False, parent: QWidget= None):
        super().__init__(parent=parent)
        self.setText(text)
        self.setFont(LabelFont())
        self.setMaximumHeight(30)
        if center:
            self.setAlignment(Qt.AlignCenter)


class CustomLineEdit(QWidget):
    def __init__(self, title: str) -> None:
        """
        panel to show the name and the value of only one measure

        Args:
            title (str): name of measure
        """
        super().__init__()
        self.name = title
        self.init_gui()

    def init_gui(self):
        self.box = QGroupBox(self.name, font=LabelFont())
        layout = QHBoxLayout(self.box)
        self.line_edit = QLineEdit()
        self.line_edit.setMaximumWidth(200)
        layout.addWidget(self.line_edit)
        horizontal_spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addItem(horizontal_spacer)
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.box)
        self.setLayout(main_layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    
    def update_title(self, title: str):
        self.box.setTitle(title)
        
    def update_text(self, text: str):
        self.line_edit.setText(text)
        

class CustomSpinBox(QWidget):
    
    def __init__(self, name: str, parent:QWidget= None)->None:
        """
        panel to show a title and modify a number value

        Args:
            title (str): name/title of the number value
        """
        super().__init__()
        self.STEP_SIZE = 500
        self.RANGE = (0,2**16-1)# due uint16
        self.name = name
        self.value: int = None
        self.init_gui()
        
    def init_gui(self):
        layout = QHBoxLayout(self)
        label_name = CustomLabel(self.name)
        label_name.setMaximumWidth(50)
        label_name.setMinimumWidth(0)
        layout.addWidget(label_name)
        self.spin_box = QSpinBox()
        self.spin_box.setSingleStep(self.STEP_SIZE)
        self.spin_box.setRange(*self.RANGE)
        layout.addWidget(self.spin_box)
    
    def set_value(self, value: int):
        self.spin_box.setValue(value)
    
    def get_value(self)-> int:
        return self.spin_box.value()
        
        