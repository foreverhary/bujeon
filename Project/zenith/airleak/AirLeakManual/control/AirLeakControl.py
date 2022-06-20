from PySide2.QtCore import QObject, Slot, Signal

from process_package.Views.CustomComponent import get_time
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.string import STR_AIR_LEAK, STR_DATA_MATRIX, STR_AIR, STR_OK, STR_NG
from process_package.tools.CommonFunction import write_beep
from process_package.tools.mssql_connect import MSSQL


class AirLeakControl(QObject):
    nfc_write = Signal(str)

    def __init__(self, model):
        super(AirLeakControl, self).__init__()
        self._model = model

        self._mssql = MSSQL(STR_AIR_LEAK)

        # controller event connect

        self.delay_write_count = 0

    @Slot(str)
    def comport_save(self, comport):
        self._model.comport = comport

    @Slot(str)
    def input_serial_data(self, value):
        if value:
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
            self.nfc_write.emit(f"{self._model.data_matrix},{STR_AIR}:{self._model.result}")
            self.delay_write_count = 2
        else:
            write_beep()
            self._model.unit_input = self._model.data_matrix
            self._mssql.start_query_thread(self._mssql.insert_pprd,
                                           get_time(),
                                           self._model.data_matrix,
                                           self._model.result)
            self._model.data_matrix = ''

    def begin(self):
        self._mssql.timer_for_db_connect()

    @staticmethod
    def right_clicked():
        MSSqlDialog()

    def mid_clicked(self):
        pass
