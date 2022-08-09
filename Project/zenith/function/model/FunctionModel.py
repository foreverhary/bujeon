from PySide2.QtCore import Signal

from process_package.models.BasicModel import BasicModel
from process_package.resource.color import RED, WHITE, GREEN, YELLOW
from process_package.resource.string import STR_NFC1, \
    STR_NFCIN, STR_NFC2, STR_SPL, STR_THD, STR_IMP, STR_MIC_FRF, STR_RUB_BUZ, STR_HOHD, \
    STR_POLARITY, B_GRADE_MAX, STR_NG, A_GRADE_MAX, STR_B, C_GRADE_MAX, STR_A, C_GRADE_MIN, STR_C
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_audio_bus


class FunctionModel(BasicModel):
    nfc_in_change_port = Signal(str)
    nfc1_change_port = Signal(str)
    nfc2_change_port = Signal(str)
    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

    nfc_input_changed = Signal(str)
    nfc_color_changed = Signal(str)

    error_code = {
        STR_SPL: 1,
        STR_THD: 2,
        STR_IMP: 3,
        STR_MIC_FRF: 4,
        STR_RUB_BUZ: 5,
        STR_HOHD: 6,
        STR_POLARITY: 7,
    }

    def __init__(self):
        super(FunctionModel, self).__init__()
        self.init_result()

    @property
    def grade(self):
        if not hasattr(self, '_grade'):
            self._grade = ''
        return self._grade

    @grade.setter
    def grade(self, value):
        if isinstance(value, float):
            if float(get_config_audio_bus(B_GRADE_MAX)) < value:
                self._grade = STR_NG
            elif float(get_config_audio_bus(A_GRADE_MAX)) < value:
                self._grade = STR_B
                color = GREEN
            elif float(get_config_audio_bus(C_GRADE_MAX)) < value:
                self._grade = STR_A
                color = WHITE
            elif float(get_config_audio_bus(C_GRADE_MIN)) <= value:
                self._grade = STR_C
                color = YELLOW
            else:
                self._grade = STR_NG
            self.grade_changed.emit(f"{self._grade} : {value:.2f}")
            self.grade_color = color
        elif isinstance(value, str):
            self._grade = value
            self.grade_color = RED

    @property
    def grade_color(self):
        if not hasattr(self, '_grade_color'):
            self._grade_color = ''
        return self._grade_color

    @grade_color.setter
    def grade_color(self, value):
        self._grade_color = value
        self.grade_color_changed.emit(value)

    @property
    def result(self):
        if not hasattr(self, '_result'):
            self._result = ''
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @property
    def nfc_input(self):
        return self._nfc_input

    @nfc_input.setter
    def nfc_input(self, value):
        self._nfc_input = value
        self.nfc_input_changed.emit(value)

    @property
    def nfc_color(self):
        return self._nfc_color

    @nfc_color.setter
    def nfc_color(self, value):
        self._nfc_color = value
        self.nfc_color_changed.emit(value)

    @property
    def nfcs(self):
        return self._nfcs

    @nfcs.setter
    def nfcs(self, value):
        if not isinstance(value, dict):
            return
        self._nfcs = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if STR_NFCIN in nfc:
                self.nfc_in_change_port.emit(port)
            if nfc == STR_NFC1:
                self.nfc1_change_port.emit(port)
            if nfc == STR_NFC2:
                self.nfc2_change_port.emit(port)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}
