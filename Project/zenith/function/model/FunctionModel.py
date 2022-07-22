from PySide2.QtCore import Signal

from function.model.NFCModel import NFCModel
from process_package.models.BasicModel import BasicModel
from process_package.resource.color import LIGHT_SKY_BLUE, RED, WHITE, GREEN, YELLOW
from process_package.resource.string import STR_NFC1, \
    STR_WRITE_DONE, STR_NFCIN, STR_NFC2, STR_SPL, STR_THD, STR_IMP, STR_MIC_FRF, STR_RUB_BUZ, STR_HOHD, \
    STR_POLARITY, B_GRADE_MAX, STR_NG, A_GRADE_MAX, STR_B, C_GRADE_MAX, STR_A, C_GRADE_MIN, STR_C
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_audio_bus


class FunctionModel(BasicModel):
    comport_changed = Signal(str)
    comport_open_changed = Signal(bool)
    available_comport_changed = Signal(list)

    previous_changed = Signal(str)
    previous_color_changed = Signal(str)

    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

    nfc_input_changed = Signal(str)
    nfc_color_changed = Signal(str)

    status_changed = Signal(str)
    status_color_changed = Signal(str)

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
        self.nfc_in = NFCModel()
        self.nfc1 = NFCModel()
        self.nfc2 = NFCModel()
        self.result = ''
        self.error_code_result = {}

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value
        self.previous_changed.emit(value)
        self.previous_color_changed.emit(LIGHT_SKY_BLUE)

    @property
    def grade(self):
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
        return self._grade_color

    @grade_color.setter
    def grade_color(self, value):
        self._grade_color = value
        self.grade_color_changed.emit(value)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.status_changed.emit(value)
        self.status_color = LIGHT_SKY_BLUE if STR_WRITE_DONE in value else WHITE

    @property
    def status_color(self):
        return self._status_color

    @status_color.setter
    def status_color(self, value):
        self._status_color = value
        self.status_color_changed.emit(value)

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
                self.nfc_in.nfc_changed.emit(port)
            if nfc == STR_NFC1:
                self.nfc1.nfc_changed.emit(port)
            if nfc == STR_NFC2:
                self.nfc2.nfc_changed.emit(port)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}

    def begin_config_read(self):
        self.init_result()
