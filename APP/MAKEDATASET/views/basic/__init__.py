from PyQt5.QtGui import QFont


class LabelFont(QFont):
    def __init__(self):
        super().__init__()
        self.setBold(True)
        self.setWeight(75)
