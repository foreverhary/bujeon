from PySide2.QtCore import QObject, Slot, QTimer
from PySide2.QtSerialPort import QSerialPort

from process_package.check_string import check_dm, check_nfc_uid
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.string import STR_NFC, STR_MATCHING, STR_TOUCH, STR_OK, STR_PREVIOUS_PROCESS_OK, \
    STR_PREVIOUS_PROCESS_NG, STR_DATA_MATRIX, STR_NFC1, STR_DISCONNECT, STR_RECONNECT
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.SearchNFC import SearchNFC
from process_package.tools.SerialPort import SerialPort
from process_package.tools.mssql_connect import MSSQL


class QRNFCWriterControl(QObject):
    def __init__(self, model):
        super(QRNFCWriterControl, self).__init__()
        self._model = model

        self.nfc = NFCSerialPort()
        self.keyboard_listener = LineReadKeyboard()
        self._mssql = MSSQL(STR_MATCHING)
        self._mssql.pre_process_result_signal.connect(self.previous_result)

        # controller event connect
        self.nfc.nfc_out_signal.connect(self.receive_nfc_data)
        self.nfc.connection_signal.connect(self.receive_nfc_connection)
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

        self.delay_write_count = 0

    @Slot(bool)
    def receive_nfc_connection(self, connection):
        self._model.nfc_connection = connection

    @Slot(dict)
    def receive_nfc_data(self, value):
        self._model.data_matrix_background = LIGHT_SKY_BLUE
        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not self._model.data_matrix:
            return

        if self._model.data_matrix and self._model.data_matrix == value.get(STR_DATA_MATRIX):
            logger.debug("DONE!!!")
            write_beep()
            self._model.previous_process = ''
            self._model.status = f"{self._model.data_matrix} is WRITTEN DONE"
            self._model.data_matrix = ''
        else:
            logger.debug("WRITE!!")
            self.nfc.write(self._model.data_matrix)
            self.delay_write_count = 2

    def input_keyboard_line(self, value):
        self._model.data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''

        if not self._model.data_matrix:
            return

        if self._mssql.con:
            self._mssql.start_query_thread(self._mssql.select_result_with_dm_keyword,
                                           self._model.data_matrix,
                                           STR_TOUCH)
        else:  # Fake
            self._model.previous_process = STR_PREVIOUS_PROCESS_OK

    def previous_result(self, value):
        if not value or value == STR_OK:
            self._model.previous_process = STR_PREVIOUS_PROCESS_OK
        else:
            self._model.previous_process = STR_PREVIOUS_PROCESS_NG

    def begin(self):
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        MSSqlDialog()

    def mid_clicked(self):
        pass
