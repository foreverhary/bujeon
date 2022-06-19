import sys

from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QApplication

from process_package.Views.CustomComponent import Label, Widget, style_sheet_setting
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.color import WHITE
from process_package.resource.size import MATCHING_PREVIOUS_PROCESS_FONT_SIZE, MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT, \
    MATCHING_DATA_MATRIX_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, MATCHING_STATUS_FONT_SIZE, \
    MATCHING_STATUS_MAXIMUM_HEIGHT
from process_package.resource.string import STR_PREVIOUS_PROCESS, STR_DATA_MATRIX, STR_STATUS, STR_QR_MATCHING


class QRNFCWriterUI(Widget):
    """
    등록 공정 UI
    """

    def __init__(self):
        super(QRNFCWriterUI, self).__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(previous_process := GroupLabel(STR_PREVIOUS_PROCESS))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX))
        layout.addWidget(status := GroupLabel(STR_STATUS))

        previous_process.label.set_font_size(MATCHING_PREVIOUS_PROCESS_FONT_SIZE)
        previous_process.setMaximumHeight(MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT)
        data_matrix.label.set_font_size(MATCHING_DATA_MATRIX_FONT_SIZE)
        data_matrix.label.setMinimumWidth(MATCHING_DATA_MATRIX_MINIMUM_WIDTH)
        status.label.set_font_size(MATCHING_STATUS_FONT_SIZE)
        status.setMaximumHeight(MATCHING_STATUS_MAXIMUM_HEIGHT)

        self.previous_process = previous_process.label
        self.data_matrix = data_matrix.label
        self.status = status.label

        self.setWindowTitle(STR_QR_MATCHING)

        self.setLayout(layout)

    def status_progress(self, percent):
        print(percent)
        self.status.setText(f"NFC Searching : {percent}%")

    def status_update(self, msg, color=WHITE):
        self.status.setText(msg)
        self.status.set_color(color)

app = QApplication([])
style_sheet_setting(app)
ex = QRNFCWriterUI()
ex.show()
sys.exit(app.exec_())