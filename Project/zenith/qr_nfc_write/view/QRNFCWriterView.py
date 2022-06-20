from PySide2.QtCore import Slot
from PySide2.QtWidgets import QVBoxLayout

from process_package.Views.CustomComponent import Widget
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.size import MATCHING_PREVIOUS_PROCESS_FONT_SIZE, MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT, \
    MATCHING_DATA_MATRIX_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, MATCHING_STATUS_FONT_SIZE, \
    MATCHING_STATUS_MAXIMUM_HEIGHT, NFC_FIXED_HEIGHT
from process_package.resource.string import STR_PREVIOUS_PROCESS, STR_DATA_MATRIX, STR_STATUS, STR_QR_MATCHING, STR_NFC1


class QRNFCWriterView(Widget):
    def __init__(self, *args):
        super(QRNFCWriterView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc1 := GroupLabel(STR_NFC1))
        layout.addWidget(previous_process := GroupLabel(STR_PREVIOUS_PROCESS))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, is_nfc=True))
        layout.addWidget(status := GroupLabel(STR_STATUS))

        nfc1.setFixedHeight(NFC_FIXED_HEIGHT)
        previous_process.label.set_font_size(MATCHING_PREVIOUS_PROCESS_FONT_SIZE)
        previous_process.setMaximumHeight(MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT)
        data_matrix.label.set_font_size(MATCHING_DATA_MATRIX_FONT_SIZE)
        data_matrix.label.setMinimumWidth(MATCHING_DATA_MATRIX_MINIMUM_WIDTH)
        status.label.set_font_size(MATCHING_STATUS_FONT_SIZE)
        status.setMaximumHeight(MATCHING_STATUS_MAXIMUM_HEIGHT)

        self.nfc1_connection = nfc1.label
        self.previous_process = previous_process.label
        self.data_matrix = data_matrix.label
        self.status = status.label

        self.setWindowTitle(STR_QR_MATCHING)

        # connect widgets to controller

        # listen for model event signals
        self._model.nfc_changed.connect(self._control.nfc.set_port)
        self._model.nfc_changed.connect(self.nfc1_connection.setText)
        self._model.nfc_connection_changed.connect(self.nfc1_connection.set_background_color)

        self._model.previous_process_changed.connect(self.previous_process.setText)
        self._model.previous_process_color_changed.connect(self.previous_process.set_color)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_background_changed.connect(self.data_matrix.set_background_color)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)
