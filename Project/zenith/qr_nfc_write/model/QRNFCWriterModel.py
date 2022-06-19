from PySide2.QtCore import QObject, Signal

from process_package.resource.color import LIGHT_SKY_BLUE, RED, WHITE
from process_package.resource.string import STR_PREVIOUS_PROCESS_OK, STR_NFC1, STR_TAG_NFC_JIG, STR_DONE
from process_package.tools.CommonFunction import logger


class QRNFCWriterModel(QObject):
    nfc_connection_changed = Signal(str)
    previous_process_changed = Signal(str)
    previous_process_color_changed = Signal(str)
    data_matrix_changed = Signal(str)
    data_matrix_background_changed = Signal(str)
    status_changed = Signal(str)
    status_color_changed = Signal(str)
    nfc_changed = Signal(str)

    def __init__(self):
        super(QRNFCWriterModel, self).__init__()
        self.data_matrix = ''

    @property
    def nfc_connection(self):
        return self._nfc_connection

    @nfc_connection.setter
    def nfc_connection(self, value):
        self.nfc_connection_changed.emit(LIGHT_SKY_BLUE if value else RED)

    @property
    def previous_process(self):
        return self._previous_process

    @previous_process.setter
    def previous_process(self, value):
        self.previous_process_color = LIGHT_SKY_BLUE if value == STR_PREVIOUS_PROCESS_OK else RED
        self._previous_process = value
        self.previous_process_changed.emit(value)

    @property
    def previous_process_color(self):
        return self._previous_process_color

    @previous_process_color.setter
    def previous_process_color(self, value):
        self._previous_process_color = value
        self.previous_process_color_changed.emit(value)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(self._data_matrix)
        if value:
            self.status = STR_TAG_NFC_JIG

    @property
    def data_matrix_background(self):
        return self._data_matrix_background

    @data_matrix_background.setter
    def data_matrix_background(self, value):
        self._data_matrix_background = value
        self.data_matrix_background_changed.emit(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.status_changed.emit(value)

        self.status_color = LIGHT_SKY_BLUE if STR_DONE in value else WHITE

    @property
    def status_color(self):
        return self._status_color

    @status_color.setter
    def status_color(self, value):
        self._status_color = value
        self.status_color_changed.emit(value)

    @property
    def nfc(self):
        return self._nfc

    @nfc.setter
    def nfc(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if nfc == STR_NFC1:
                self._nfc = port
                self.nfc_changed.emit(port)
                break
