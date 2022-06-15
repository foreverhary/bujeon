import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout

from packages.component.CustomComponent import style_sheet_setting, Widget, GroupLabel
from packages.variable.size import RELEASE_LABEL_MINIMUM_WIDTH, RELEASE_DATA_MATRIX_MINIMUM_HEIGHT, \
    RELEASE_RESULT_FIXED_HEIGHT, RELEASE_STATUS_FONT_SIZE
from packages.variable.string import DATA_MATRIX, RESULT, STATUS
from packages.variable.variables import logger


class ReleaseProcess(Widget):
    def __init__(self):
        super(ReleaseProcess, self).__init__()
        self.status = None
        self.result = None
        self.data_matrix = None
        self.setup_ui()
        self.showMaximized()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(data_matrix := GroupLabel(DATA_MATRIX))
        layout.addWidget(result := GroupLabel(RESULT))
        layout.addWidget(status := GroupLabel(STATUS))

        data_matrix.label.setMinimumSize(RELEASE_LABEL_MINIMUM_WIDTH,
                                         RELEASE_DATA_MATRIX_MINIMUM_HEIGHT)
        result.label.setMinimumHeight(RELEASE_RESULT_FIXED_HEIGHT)
        status.label.setMinimumHeight(RELEASE_DATA_MATRIX_MINIMUM_HEIGHT)
        status.label.set_font_size(RELEASE_STATUS_FONT_SIZE)
        
        self.data_matrix = data_matrix
        self.result = result
        self.status = status

if __name__ == '__main__':
    logger.info("sensor start")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = ReleaseProcess()
    sys.exit(app.exec())
