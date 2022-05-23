from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from process_package.PyQtCustomComponent import Label
from process_package.defined_variable_function import QR_DM_MINIMUM_WIDTH_SIZE, QR_DM_TEXT_SIZE, \
    QR_PREVIOUS_PROCESS_TEXT_SIZE, QR_STATUS_TEXT_SIZE, PREVIOUS_PROCESS, DATA_MATRIX, STATUS


class QRNFCWriterUI(QWidget):
    """
    등록 공정 UI
    """

    def __init__(self):
        super(QRNFCWriterUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(preprocess_box := QGroupBox(PREVIOUS_PROCESS))
        preprocess_box.setLayout(preprocess_layout := QVBoxLayout())
        preprocess_layout.addWidget(preprocess := Label())

        layout.addWidget(dm_box := QGroupBox(DATA_MATRIX))
        dm_box.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm := Label())

        layout.addWidget(status_box := QGroupBox(STATUS))
        status_box.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status := Label())

        self.preprocess_label = preprocess
        self.dm_label = dm
        self.status_label = status
        self.preprocess_label.set_font_size(size=QR_PREVIOUS_PROCESS_TEXT_SIZE)
        self.dm_label.setMinimumWidth(QR_DM_MINIMUM_WIDTH_SIZE)
        self.dm_label.set_font_size(size=QR_DM_TEXT_SIZE)
        self.status_label.set_font_size(size=QR_STATUS_TEXT_SIZE)

        self.setWindowTitle('DM Registration')

        self.setLayout(layout)
