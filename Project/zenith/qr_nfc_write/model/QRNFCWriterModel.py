from PySide2.QtCore import Signal

from process_package.models.BasicModel import BasicModel
from process_package.resource.string import STR_NFC
from process_package.tools.CommonFunction import logger


class QRNFCWriterModel(BasicModel):
    nfc_changed = Signal(str)
    previous_result_changed = Signal(dict)
    status_changed = Signal(str)
    status_color_changed = Signal(str)

    def __init__(self):
        super(QRNFCWriterModel, self).__init__()

    @property
    def previous_result(self):
        return self._previous_result

    @previous_result.setter
    def previous_result(self, value):
        self._previous_result = value
        self.previous_result_changed.emit(value)

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
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break

