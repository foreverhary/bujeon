from PySide2.QtCore import QObject, Signal

from process_package.Views.CustomComponent import get_time
from process_package.check_string import check_dm
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.controllers.OrderNumberDialog import OrderNumberDialog
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.string import STR_OK, STR_DATA_MATRIX, STR_TOUCH
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.mssql_connect import MSSQL


class QRNFCWriterControl(QObject):
    nfc_write = Signal(str)

    def __init__(self, model):
        super(QRNFCWriterControl, self).__init__()
        self._model = model

        self.keyboard_listener = LineReadKeyboard()
        self._mssql = MSSQL(STR_TOUCH)

        # controller event connect
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

        self.delay_write_count = 0

    def receive_nfc_data(self, value):
        if not value:
            return
        logger.debug(value)
        self._model.data_matrix_background = LIGHT_SKY_BLUE
        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not self._model.data_matrix:
            return

        if self._model.data_matrix and self._model.data_matrix == value.get(STR_DATA_MATRIX):
            logger.debug("DONE!!!")
            write_beep()
            self._model.order_number = ''
            self._model.status = f"{self._model.data_matrix} is WRITTEN DONE"
            self._model.data_matrix = ''
        else:
            logger.debug("WRITE!!")
            self.nfc_write.emit(self._model.data_matrix)
            self.delay_write_count = 2

    def input_keyboard_line(self, value):
        self._model.data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''

        if not self._model.data_matrix:
            return

        if self._model.order_number:
            self._mssql.start_query_thread(self._mssql.insert_pprh,
                                           get_time(),
                                           self._model.order_number,
                                           self._model.data_matrix)
            self._mssql.start_query_thread(self._mssql.insert_pprd,
                                           get_time(),
                                           self._model.data_matrix,
                                           STR_OK)

    def begin(self):
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        OrderNumberDialog(self._model)

    @staticmethod
    def mid_clicked():
        MSSqlDialog()
