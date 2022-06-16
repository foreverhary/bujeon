import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout

from packages.views.CustomComponent import Widget, style_sheet_setting, GroupLabel
from packages.resources.size import MATCHING_PREVIOUS_PROCESS_FONT_SIZE, MATCHING_DATA_MATRIX_FONT_SIZE, \
    MATCHING_STATUS_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, MATCHING_STATUS_MAXIMUM_HEIGHT, \
    MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT
from packages.resources.string import PREVIOUS_PROCESS, DATA_MATRIX, STATUS


class QRNFCWriter(Widget):
    def __init__(self):
        super(QRNFCWriter, self).__init__()
        # component
        self.previous_process = None
        self.data_matrix = None
        self.status = None

        self.setup_ui()
        self.show()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(previous_process := GroupLabel(title=PREVIOUS_PROCESS))
        layout.addWidget(data_matrix := GroupLabel(title=DATA_MATRIX))
        layout.addWidget(status := GroupLabel(title=STATUS))

        previous_process.label.set_font_size(MATCHING_PREVIOUS_PROCESS_FONT_SIZE)
        previous_process.setMaximumHeight(MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT)
        data_matrix.label.set_font_size(MATCHING_DATA_MATRIX_FONT_SIZE)
        data_matrix.label.setMinimumWidth(MATCHING_DATA_MATRIX_MINIMUM_WIDTH)
        status.label.set_font_size(MATCHING_STATUS_FONT_SIZE)
        status.setMaximumHeight(MATCHING_STATUS_MAXIMUM_HEIGHT)

        self.previous_process = previous_process
        self.data_matrix = data_matrix
        self.status = status
        self.setWindowTitle("QR MATCHING")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = QRNFCWriter()
    sys.exit(app.exec())
