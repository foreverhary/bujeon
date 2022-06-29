from PySide2.QtCore import QObject, Signal

from process_package.resource.color import LIGHT_SKY_BLUE, WHITE
from process_package.resource.string import STR_NFC1, STR_TAG_NFC_JIG, STR_DONE, STR_READY, STR_INSERT_ORDER_NUMBER, \
    STR_NFC
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import set_order_number, get_order_number


class QRNFCWriterModel(QObject):
    nfc_changed = Signal(str)
    order_changed = Signal(str)
    data_matrix_changed = Signal(str)
    data_matrix_background_changed = Signal(str)
    status_changed = Signal(str)
    status_color_changed = Signal(str)

    def __init__(self):
        super(QRNFCWriterModel, self).__init__()
        self.data_matrix = ''

    @property
    def order_number(self):
        return self._order

    @order_number.setter
    def order_number(self, value):
        self.status = STR_READY if value else STR_INSERT_ORDER_NUMBER
        self._order = value
        self.order_changed.emit(value)
        set_order_number(value)

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
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break

    def begin(self):
        self.order_number = get_order_number()
