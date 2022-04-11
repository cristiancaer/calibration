from PyQt5.QtWidgets import QPushButton, QWidget, QStyle, QApplication, QHBoxLayout
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic import LabelFont

class BasicButton(QPushButton):
    def __init__(self, name: str, icon_atr: str = None):
        super().__init__()
        self.name = name
        self.icon_atr = icon_atr
        self.init_gui()

    def init_gui(self):
        self.setText(self.name)
        if self.icon_atr:
            pixmap = getattr(QStyle, self.icon_atr)
            icon = self.style().standardIcon(pixmap)
            self.setIcon(icon)
            self.setFont(LabelFont())


class NextButton(BasicButton):
    def __init__(self, parent: QWidget = None):
        super().__init__('Next', 'SP_ArrowForward')
        self.setParent(parent)


class BackButton(BasicButton):
    def __init__(self, parent: QWidget = None):
        super().__init__('Back', 'SP_ArrowLeft')
        self.setParent(parent)

class BackNextButtons(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        self.next = NextButton()
        self.back = BackButton()
        layout.addWidget(self.back)
        layout.addWidget(self.next)
        
        
# TEST
##


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = BackNextButtons()
    window.show()
    sys.exit(app.exec_())
