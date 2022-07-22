from PyQt5.QtWidgets import QPushButton, QWidget, QStyle, QApplication, QVBoxLayout, QHBoxLayout
import sys
sys.path.append('./')
from APP.views.basic import CustomLabel,LabelFont


class BasicButton(QPushButton):
    IS_PRESSED_COLOR = 'green'
    DEFAULT_COLOR = 'lightgray'
    def __init__(self, name: str, icon_atr: str = None):
        super().__init__()
        self.name = name
        self.icon_atr = icon_atr
        self.status = False
        self.init_gui()
        

    def init_gui(self):
        self.setText(self.name)
        if self.icon_atr:
            pixmap = getattr(QStyle, self.icon_atr)
            icon = self.style().standardIcon(pixmap)
            self.setIcon(icon)
        self.setStyleSheet("QPushButton::pressed"
                            "{"
                            "background-color : green;"
                            "}")
        self.setFont(LabelFont())
        
    def set_pressed(self, flat = False):
        self.status = flat
            
        if self.status:
            color = self.IS_PRESSED_COLOR
        else: 
            color = self.DEFAULT_COLOR
        self.setStyleSheet("background-color : {}".format(color))


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


class ButtonAndLabel(QWidget):
    def __init__(self,name_button: str , icon_atr: str= None, parent: QWidget= None):
        super().__init__(parent=parent)
        self.button = BasicButton(name_button, icon_atr)
        self.label = CustomLabel(center=True)
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        layout.addWidget(self.label)
        
    def set_text(self, text: str):
        self.label.setText(text)

class ButtonGetDir(ButtonAndLabel):
    def __init__(self, parent: QWidget= None):
        super().__init__('Open','SP_DirOpenIcon')
    
    
# TEST
##


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = BasicButton('test')
    
    window.show()
    sys.exit(app.exec_())
