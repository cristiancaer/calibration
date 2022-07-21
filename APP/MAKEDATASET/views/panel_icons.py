from PyQt5.QtWidgets import QWidget, QGridLayout, QApplication, QSizePolicy, QSpacerItem
import sys
sys.path.append('./')
from APP.MAKEDATASET.views.basic.label_for_image import LabelForImage
from APP.models.basic_config import CC_ICON_PATH


class PanelIcons(QWidget):
    def __init__(self, parent=None):
        """
        Panel to show icons 
        """
        super().__init__(parent=parent)
        self.init_gui()

    def init_gui(self):
        """
        Visualization 
        """

        layout = QGridLayout()
        # add horizontal spacer
        horizontal_spacer = QSpacerItem(10, 10, QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout.addItem(horizontal_spacer)
        # add vertical spacer
        vertical_spacer = QSpacerItem(10, 10, QSizePolicy.Fixed, QSizePolicy.Expanding)
        layout.addItem(vertical_spacer)
        cc_icon = self.get_icon(CC_ICON_PATH)
        layout.addWidget(cc_icon)
        self.setLayout(layout)

    def get_icon(self, path_name: str) ->LabelForImage:
        """
        usefull to make a label that will conteint an image specify by path name
        Args:
            path_name (str): path and name to the image/icon.jpg

        Returns:
            LabelForImage: label widget with the image
        """
        icon = LabelForImage()
        icon.update_img_from_path(path_name)
        icon.setScaledContents(True)
        icon.setMaximumSize(200, 200)

        return icon


#TEST
################################################################################
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PanelIcons()
    window.show()
    sys.exit(app.exec_())
