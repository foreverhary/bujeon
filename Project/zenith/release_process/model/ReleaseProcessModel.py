from PySide2.QtCore import QObject, Signal

from process_package.check_string import check_dm
from process_package.resource.color import LIGHT_SKY_BLUE, RED, BACK_GROUND_COLOR, WHITE, YELLOW, GREEN
from process_package.resource.size import RELEASE_RESULT_FONT_SIZE, RELEASE_GRADE_FONT_SIZE
from process_package.resource.string import STR_NFC, STR_A, STR_B, STR_C
from process_package.tools.CommonFunction import logger

grade_colors = {
    STR_A: WHITE,
    STR_B: YELLOW,
    STR_C: GREEN
}

class ReleaseProcessModel(QObject):
    nfc_changed = Signal(str)
    nfc_connection_changed = Signal(str)

    data_matrix_changed = Signal(str)

    result_changed = Signal(str)
    result_font_size_changed = Signal(int)
    result_font_color_changed = Signal(str)
    result_background_color_changed = Signal(str)

    status_changed = Signal(str)

    @property
    def nfc_connection(self):
        return self._nfc_connection

    @nfc_connection.setter
    def nfc_connection(self, value):
        self.nfc_connection_changed.emit(LIGHT_SKY_BLUE if value else RED)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''
        self.data_matrix_changed.emit(self._data_matrix)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        if value in [STR_A, STR_B, STR_C]:
            self.result_font_size = RELEASE_GRADE_FONT_SIZE
            self.result_background_color = BACK_GROUND_COLOR
            self.result_font_color = grade_colors[value]
        else:
            self.result_font_color = WHITE
            self.result_font_size = RELEASE_RESULT_FONT_SIZE
            self.result_background_color = RED
        self.result_changed.emit(value)

    @property
    def result_font_size(self):
        return self._result_font_size

    @result_font_size.setter
    def result_font_size(self, value):
        self._result_font_size = value
        self.result_font_size_changed.emit(value)

    @property
    def result_font_color(self):
        return self._result_font_color

    @result_font_color.setter
    def result_font_color(self, value):
        self._result_font_color = value
        self.result_font_color_changed.emit(value)

    @property
    def result_background_color(self):
        return self._result_background_color

    @result_background_color.setter
    def result_background_color(self, value):
        self._result_background_color = value
        self.result_background_color_changed.emit(value)

    @property
    def nfcs(self):
        return self._nfc

    @nfcs.setter
    def nfcs(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break
