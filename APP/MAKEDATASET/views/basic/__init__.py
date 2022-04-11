from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel,QWidget
from PyQt5.QtCore import Qt


class LabelFont(QFont):
    def __init__(self):
        super().__init__()
        self.setBold(True)
        self.setWeight(75)


class CustomLabel(QLabel):
    def __init__(self, text: str= '', parent: QWidget= None):
        super().__init__(parent=parent)
        self.setText(text)
        self.setAlignment(Qt.AlignCenter)
