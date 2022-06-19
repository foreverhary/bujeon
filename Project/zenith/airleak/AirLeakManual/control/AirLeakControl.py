from PySide2.QtCore import QObject, Slot
from PySide2.QtSerialPort import QSerialPort

from process_package.Views.CustomComponent import get_time
from process_package.check_string import check_dm
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.string import STR_NFC, STR_TOUCH, STR_PREVIOUS_PROCESS_OK, \
    STR_AIR_LEAK, STR_DATA_MATRIX, STR_AIR, STR_OK, STR_NG
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.SerialPort import SerialPort
from process_package.tools.mssql_connect import MSSQL


class AirLeakControl(QObject):
    def __init__(self, model):
        super(AirLeakControl, self).__init__()
        self._model = model

        self.serial = SerialPort(STR_AIR_LEAK)
        self.nfc = NFCSerialPort(STR_NFC)
        self._mssql = MSSQL(STR_AIR_LEAK)

        # controller event connect
        self.serial.line_out_signal.connect(self.input_serial_data)
        self.nfc.nfc_out_signal.connect(self.receive_nfc_data)
        self.nfc.connection_signal.connect(self.receive_nfc_connection)

        self.delay_write_count = 0

    @Slot(int)
    def change_comport(self, comport):
        self._model.comport = comport

    @Slot()
    def comport_clicked(self):
        logger.debug(self._model.comport)
        self.serial.set_port_baudrate(self._model.comport, QSerialPort.Baud9600)
        self._model.comport_open = self.serial.close() if self.serial.isOpen() else self.serial.open()
        logger.debug(self._model.comport_open)

    @Slot(bool)
    def receive_nfc_connection(self, connection):
        self._model.nfc_connection = connection

    @Slot(str)
    def input_serial_data(self, value):
        self._model.result = STR_OK if STR_OK in value else STR_NG

    @Slot(dict)
    def receive_nfc_data(self, value):
        if not self._model.result:
            return

        if value.get(STR_DATA_MATRIX) in self._model.units:
            self._model.unit_blink = self._model.units.index(value[STR_DATA_MATRIX])
            return

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        self._model.unit_color = len(self._model.units)

        if self._model.data_matrix != value.get(STR_DATA_MATRIX) \
                or self._model.result != value.get(STR_AIR):
            self._model.data_matrix = value.get(STR_DATA_MATRIX)
            self.nfc.write(f"{self._model.data_matrix},{STR_AIR}:{self._model.result}")
            self.delay_write_count = 2
        else:
            write_beep()
            self._model.unit_input = self._model.data_matrix
            self._mssql.start_query_thread(self._mssql.insert_pprd,
                                           get_time(),
                                           self._model.data_matrix,
                                           self._model.result)
            self._model.data_matrix = ''

    def input_keyboard_line(self, value):
        self._model.data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''

        if self._mssql.con:
            self._mssql.start_query_thread(self._mssql.select_result_with_dm_keyword,
                                           self._model.data_matrix,
                                           STR_TOUCH)
        else:  # Fake
            self._model.previous_process = STR_PREVIOUS_PROCESS_OK

    def begin(self):
        self.comport_clicked()
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        MSSqlDialog()

    def mid_clicked(self):
        pass
