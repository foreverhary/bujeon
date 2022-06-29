from PySide2.QtCore import Signal

from process_package.models.ConfigModel import ConfigModel
from process_package.resource.color import LIGHT_SKY_BLUE, RED, BACK_GROUND_COLOR, WHITE
from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, STR_OK, STR_NFC1, \
    NUMERAL, STR_WRITE_DONE, STR_AIR_LEAK, STR_NFC
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import set_config_value, get_config_value


class AirLeakModel(ConfigModel):
    nfc_changed = Signal(str)

    result_changed = Signal(str)
    result_background_color_changed = Signal(str)
    unit_input_changed = Signal(int, str)
    unit_color_changed = Signal(int)
    unit_blink_changed = Signal(int)
    units_clean = Signal()

    status_changed = Signal(str)
    status_color_changed = Signal(str)

    def __init__(self):
        super(AirLeakModel, self).__init__()
        self.units = []
        self.result = ''
        self.data_matrix = ''
        self.name = STR_AIR_LEAK
        self.baudrate = 9600
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1)

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value
        set_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, value)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)
        if not value:
            self.result_background_color = BACK_GROUND_COLOR
        else:
            self.units = []
            self.units_clean.emit()
            self.result_background_color = LIGHT_SKY_BLUE if value == STR_OK else RED
            self.status = "TAG FIRST JIG"

    @property
    def result_background_color(self):
        return self._result_background_color

    @result_background_color.setter
    def result_background_color(self, value):
        self._result_background_color = value
        self.result_background_color_changed.emit(value)

    @property
    def unit_input(self):
        return self._unit_input

    @unit_input.setter
    def unit_input(self, value):
        self._unit_input = value
        self.unit_input_changed.emit(len(self.units), value)
        self.units.append(value)
        if len(self.units) < 4:
            self.status = f"TAG {NUMERAL[len(self.units) + 1]} JIG"
        else:
            self.units = []
            self.result = ''
            self.status = STR_WRITE_DONE

    @property
    def unit_color(self):
        return self._unit_color

    @unit_color.setter
    def unit_color(self, value):
        self._unit_color = value
        self.unit_color_changed.emit(value)

    @property
    def unit_blink(self):
        return self._unit_blink

    @unit_blink.setter
    def unit_blink(self, value):
        self._unit_blink = value
        self.unit_blink_changed.emit(value)

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
    def nfc(self):
        return self._nfc

    @nfc.setter
    def nfc(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break
