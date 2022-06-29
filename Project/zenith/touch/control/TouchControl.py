import socket

from PySide2.QtCore import QObject, Slot, Signal, QTimer

from process_package.component.CustomComponent import get_time
from process_package.check_string import check_dm
from process_package.resource.number import CHECK_DB_UPDATE_TIME
from process_package.resource.string import STR_TOUCH, STR_OK, STR_NG
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class TouchControl(QObject):
    serial_is_open = Signal(bool)

    def __init__(self, model):
        super(TouchControl, self).__init__()
        self._model = model

        self.keyboard_listener = LineReadKeyboard()
        self._mssql = MSSQL(STR_TOUCH)

        self.db_update_timer = QTimer(self)
        self.db_update_timer.start(CHECK_DB_UPDATE_TIME)
        self.db_update_timer.timeout.connect(self.update_db)

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
                                           data_matrix,
                                           self._model.order_number,
                                           get_time(),
                                           )

    def input_serial_data(self, value):
        if "TEST RESULT" in value and self._model.data_matrix:
            self._model.machine_result = STR_OK if STR_OK in value else STR_NG
            if self._model.order_number:
                self._mssql.start_query_thread(self._mssql.insert_pprd,
                                               self._model.data_matrix,
                                               get_time(),
                                               self._model.machine_result,
                                               STR_TOUCH,
                                               '',
                                               socket.gethostbyname(socket.gethostname()))

                self._model.data_matrix = self._model.data_matrix_waiting
                self._model.data_matrix_waiting = ''

    def update_db(self):
        UpdateDB()

    def begin(self):
        self._mssql.timer_for_db_connect()

    def mid_clicked(self):
        pass
