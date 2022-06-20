from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtSerialPort import QSerialPort

from process_package.Views.CustomComponent import get_time
from process_package.check_string import check_dm
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.controllers.OrderNumberDialog import OrderNumberDialog
from process_package.resource.string import STR_TOUCH, STR_OK, STR_NG
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.SerialPort import SerialPort
from process_package.tools.mssql_connect import MSSQL


class TouchControl(QObject):
    serial_is_open = Signal(bool)

    def __init__(self, model):
        super(TouchControl, self).__init__()
        self._model = model

        self.keyboard_listener = LineReadKeyboard()
        self._mssql = MSSQL(STR_TOUCH)

        # controller event connect
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

    @Slot(str)
    def comport_save(self, comport):
        self._model.comport = comport

    def input_keyboard_line(self, value):
        if self._model.data_matrix == value:
            return
        if not (data_matrix := check_dm(value)):
            return

        if self._model.data_matrix:
            self._model.data_matrix_waiting = data_matrix
        else:
            self._model.data_matrix = data_matrix
        if data_matrix and self._model.order_number:
            self._mssql.start_query_thread(self._mssql.insert_pprh,
                                           get_time(),
                                           self._model.order_number,
                                           data_matrix)

    def input_serial_data(self, value):
        if "TEST RESULT" in value and self._model.data_matrix:
            self._model.machine_result = STR_OK if STR_OK in value else STR_NG
            if self._model.order_number:
                self._mssql.start_query_thread(self._mssql.insert_pprd,
                                               get_time(),
                                               self._model.data_matrix,
                                               self._model.machine_result)

    def begin(self):
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        OrderNumberDialog(self._model)

    def mid_clicked(self):
        MSSqlDialog()
