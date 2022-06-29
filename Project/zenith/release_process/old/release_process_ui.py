import sys

from PySide2.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QApplication

from process_package.component.CustomComponent import Label, style_sheet_setting, LabelTimerClean

RELEASE_FIXED_WIDTH = 700
RELEASE_FIXED_DM_HEIGHT = 100
RELEASE_FIXED_DM_FONT_SIZE = 70

RELEASE_FIXED_RESULT_HEIGHT = 400
RELEASE_FIXED_RESULT_FONT_SIZE = 60

RELEASE_FIXED_STATUS_FONT_SIZE = 35


class CustomLabel(Label):
    def __init__(self, width=300, height=200, font_size=30, is_clean=False, clean_time=2000):
        super(CustomLabel, self).__init__(font_size=font_size, is_clean=False, clean_time=2000)
        self.setMinimumSize(width, height)


class ReleaseProcessUI(QWidget):
    def __init__(self):
        super(ReleaseProcessUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(dm_groupbox := QGroupBox('DM'))
        dm_groupbox.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm_input_label := LabelTimerClean(
            font_size=RELEASE_FIXED_DM_FONT_SIZE,
            is_clean=True,
            clean_time=2000
        ))
        dm_input_label.setMinimumSize(RELEASE_FIXED_WIDTH,
                                      RELEASE_FIXED_DM_HEIGHT)
        layout.addWidget(result_groupbox := QGroupBox('RESULT'))
        result_groupbox.setLayout(result_layout := QVBoxLayout())
        result_layout.addWidget(result_input_label := LabelTimerClean(
            font_size=RELEASE_FIXED_RESULT_FONT_SIZE,
            is_clean=True,
            clean_time=1500))
        result_input_label.setMinimumSize(RELEASE_FIXED_WIDTH,
                                          RELEASE_FIXED_RESULT_HEIGHT)
        layout.addWidget(status_groupbox := QGroupBox('STATUS'))
        status_groupbox.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status_label := Label(font_size=RELEASE_FIXED_STATUS_FONT_SIZE))
        status_label.setMinimumSize(RELEASE_FIXED_WIDTH, RELEASE_FIXED_DM_HEIGHT)
        # status_layout.addWidget(status_label := CustomLabel(RELEASE_FIXED_WIDTH,
        #                                                     RELEASE_FIXED_DM_HEIGHT,
        #                                                     RELEASE_FIXED_STATUS_FONT_SIZE))
        self.dm_input_label = dm_input_label
        self.result_input_label = result_input_label
        self.status_label = status_label


app = QApplication([])
style_sheet_setting(app)
ex = ReleaseProcessUI()
ex.show()
sys.exit(app.exec_())