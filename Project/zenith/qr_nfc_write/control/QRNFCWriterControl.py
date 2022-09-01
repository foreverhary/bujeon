from PySide2.QtCore import QObject, Signal

from process_package.check_string import check_dm
from process_package.component.SearchDataMatrixLocal import SearchDataMatrixLocal
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.string import STR_DATA_MATRIX, STR_TOUCH, STR_AIR
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class QRNFCWriterControl(QObject):
    nfc_write = Signal(str)
    nfc_write_bytes = Signal(bytes)

    def __init__(self, model):
        super(QRNFCWriterControl, self).__init__()
        self._model = model

        self.keyboard_listener = LineReadKeyboard(self.input_keyboard_line)
        self._mssql = MSSQL(STR_TOUCH)
        self._mssql.data_matrix_with_air_touch_result_signal.connect(self.receive_previous_result)
        self.update_db = UpdateDB()

        self.keyboard_disabled = False
        self.delay_write_count = 0
        self.temp_data_matrix = ''

    def receive_nfc_data(self, value):
        if not value:
            return
        self._model.data_matrix_background = LIGHT_SKY_BLUE
        if self.delay_write_count:
            self.delay_write_count -= 1
            return
        if not self._model.data_matrix:
            return

        if self._model.data_matrix == value.get(STR_DATA_MATRIX):
            logger.debug("DONE!!!")
            write_beep()
            self._model.data_matrix = ''
        else:
            logger.debug("WRITE!!")
            self.nfc_write.emit(self._model.data_matrix)
            self.delay_write_count = 1

    def input_keyboard_line(self, value):
        if self.keyboard_disabled:
            return
        self.temp_data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''

        if not self.temp_data_matrix:
            return

        self._mssql.start_query_thread(
            self._mssql.select_pprd_with_data_matrix_and_air_touch,
            self.temp_data_matrix
        )

    def receive_previous_result(self, value):
        db_result_to_dict = {STR_DATA_MATRIX: self.temp_data_matrix}
        for fetch in value:
            if fetch[3] == 'AIR' and not db_result_to_dict.get(STR_AIR):
                db_result_to_dict[STR_AIR] = fetch[2]
            if fetch[3] == 'TOUCH' and not db_result_to_dict.get(STR_TOUCH):
                db_result_to_dict[STR_TOUCH] = fetch[2]
        self._model.previous_result = db_result_to_dict

    def mid_clicked(self):
        self.keyboard_disabled = True
        SearchDataMatrixLocal(self)
