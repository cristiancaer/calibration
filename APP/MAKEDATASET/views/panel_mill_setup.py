from PyQt5.QtWidgets import  QApplication, QGroupBox, QHBoxLayout
import cv2
import sys
sys.path.append('./')
from APP.MAKEDATASET.models.data_objects import DataFromAcquisition
from APP.MAKEDATASET.views.draw_tools.draw_over_data_to_show import DrawDataToShow
from APP.MAKEDATASET.models import  TEST_IMG
from APP.MAKEDATASET.views.panel_rgbd_images import PanelRGBDImage
from APP.MAKEDATASET.views.basic.buttons import BackNextButtons, BasicButton
from APP.MAKEDATASET.views.basic import CustomLineEdit


class PanelMillSetup(PanelRGBDImage):
    def __init__(self, parent= None)->None:
        super().__init__(parent, draw_rgb=True)
    
    def init_gui(self):
        super().init_gui()
        group_tool_buttons = QGroupBox('Tools')
        group_tool_buttons.setMaximumHeight(90)
        tool_layout = QHBoxLayout(group_tool_buttons)
        self.button_screenshot = BasicButton(' Take ScreenShot')
        tool_layout.addWidget(self.button_screenshot)
        
        self.button_left_line = BasicButton('Add left line')
        tool_layout.addWidget(self.button_left_line)

        self.button_right_line = BasicButton('Add right line')
        tool_layout.addWidget(self.button_right_line)
        
        self.button_add_polygon = BasicButton('Add Polygon')
        self.button_add_polygon.setEnabled(False)
        tool_layout.addWidget(self.button_add_polygon)
        
        self.button_get_inclination = BasicButton('Get inclination info')
        self.button_get_inclination.setEnabled(False)
        tool_layout.addWidget(self.button_get_inclination)
        
        self.main_layout.addWidget(group_tool_buttons, 4, 0, 1 , 2)
        ################################################################################
        group_show_info = QGroupBox('Information')
        group_show_info.setMaximumHeight(150)
        info_layout = QHBoxLayout(group_show_info)
        
        self.label_left_angle = CustomLineEdit('Left angle')
        info_layout.addWidget(self.label_left_angle)
        
        self.label_right_angle = CustomLineEdit('Right angle')
        info_layout.addWidget(self.label_right_angle)
        
        self.main_layout.addWidget(group_show_info, 5, 0, 1, 2)
        ################################################################################
        self.back_next_buttons = BackNextButtons()
        self.back_next_buttons.setMaximumHeight(60)
        self.main_layout.addWidget(self.back_next_buttons, 6, 0, 1, 2)
        
#TEST
################################################################################
if __name__=='__main__':
    img_test = cv2.imread(TEST_IMG)
    data_to_show = DrawDataToShow(DataFromAcquisition(rgb=img_test, depth=img_test))
    app = QApplication(sys.argv)
    window = PanelMillSetup()
    window.set_dark_images()
    window.panel_visualization_range.set_units('100 um')
    window.update_rgbd(data_to_show)
    window.show()
    sys.exit(app.exec_())