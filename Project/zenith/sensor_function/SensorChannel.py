import socket

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QGroupBox, QVBoxLayout

from process_package.component.NFCComponent import NFCComponent
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.Views.CustomComponent import Button, ComboBox, Label, Widget, get_time, LabelTimerClean, LabelNFC
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.string import STR_RESULT, STR_CON_OS, STR_POGO_OS, STR_LED, STR_HALL_IC, STR_VBAT_ID, \
    STR_C_TEST, STR_BATTERY, STR_PROX_TEST, STR_MIC, STR_PCM, STR_SEN, CONFIG_FILE_NAME, COMPORT_SECTION, \
    MACHINE_COMPORT_1, MACHINE_COMPORT_2, STR_DATA_MATRIX, PROCESS_NAMES, STR_SENSOR, STR_OK, STR_NG
from process_package.tools.CommonFunction import write_beep
from process_package.tools.Config import get_config_value, set_config_value
from process_package.tools.mssql_connect import MSSQL


class SensorChannel(QGroupBox):
    def __init__(self, channel):
        super(SensorChannel, self).__init__()
        self._model = SensorChannelModel(channel)
        self._control = SensorChannelControl(self._model)

        # UI
        self.setTitle(f"Channel {channel}")
        layout = QVBoxLayout(self)
        layout.addLayout(comport := SerialComboHBoxLayout(self._model, button_text='CONN'))
        layout.addWidget(Label('DM'))
        layout.addWidget(data_matrix := LabelNFC())
        layout.addWidget(Label(STR_RESULT))
        layout.addWidget(result := Label())
        layout.addWidget(nfc := NFCComponent(f"NFC{channel}"))

        # size & font size
        result.setFixedHeight(350)
        result.set_font_size(100)

        # assign
        self.comport = comport
        self.data_matrix = data_matrix
        self.result = result
        self.nfc = nfc

        # view connect control
        self.comport.comport_save.connect(self._control.comport_save)
        self.comport.serial_output_data.connect(self._control.input_serial_data)
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # control connect view
        self._control.nfc_write.connect(nfc.write)

        # model connect view
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_clean.connect(self.data_matrix.clean)
        self._model.data_matrix_color_changed.connect(self.data_matrix.set_background_color)
        self._model.result_changed.connect(self.result.setText)
        self._model.result_clean.connect(self.result.clean)
        self._model.result_color_changed.connect(self.result.set_background_color)

    def set_port(self, value):
        self.nfc.set_port(value)


class SensorChannelControl(QObject):
    nfc_write = Signal(str)
    def __init__(self, model):
        super(SensorChannelControl, self).__init__()
        self._model = model

        self._mssql = MSSQL(STR_SEN)

        self.delay_write_count = 0
        self.data_matrix = ''
        self.process_name = STR_SEN

    @Slot(str)
    def comport_save(self, comport):
        self._model.comport = comport

    @Slot(str)
    def input_serial_data(self, value):
        value = value.upper()
        split_list = value.split(',')
        if len(split_list) < 2:
            return

        self._model.init_result()
        split_list = split_list[1:-1]
        for item, key in zip(split_list, self._model.error_code_result):
            self._model.error_code_result[key] = item == STR_OK
        if False in self._model.error_code_result.values():
            self._model.result = STR_NG
        else:
            self._model.result = STR_OK
        self._model.data_matrix = ''

    @Slot(dict)
    def receive_nfc_data(self, value):
        self._model.data_matrix_color = LIGHT_SKY_BLUE

        if not self._model.result:
            return

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if self.data_matrix != data_matrix or self._model.result != value.get(STR_SEN):
            self.data_matrix = data_matrix
            msg = data_matrix
            for name in PROCESS_NAMES:
                if name == self.process_name:
                    msg += f",{name}:{self._model.result}"
                    break
                if result := value.get(name):
                    msg += f",{name}:{result}"
            self.nfc_write.emit(msg)
            self.delay_write_count = 3
        else:
            write_beep()
            self.sql_update()
            self._model.result = ''
            self._model.data_matrix = data_matrix

    def sql_update(self):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       self.data_matrix,
                                       get_time(),
                                       self._model.result,
                                       STR_SENSOR,
                                       self._model.get_error_code(),
                                       socket.gethostbyname(socket.gethostname()))

    def begin(self):
        self._mssql.timer_for_db_connect()


class SensorChannelModel(QObject):
    data_matrix_changed = Signal(str)
    data_matrix_clean = Signal()
    data_matrix_color_changed = Signal(str)
    result_changed = Signal(str)
    result_clean = Signal()
    result_color_changed = Signal(str)
    error_code = {
        STR_CON_OS: 1,
        STR_POGO_OS: 2,
        STR_LED: 3,
        STR_HALL_IC: 10,
        STR_VBAT_ID: 4,
        STR_C_TEST: 5,
        STR_BATTERY: 6,
        STR_PROX_TEST: 8,
        STR_MIC: 7,
        STR_PCM: 9,
    }

    def __init__(self, channel):
        super(SensorChannelModel, self).__init__()
        self.name = STR_SEN
        self.baudrate = 9600
        self.channel = MACHINE_COMPORT_1 if channel == 1 else MACHINE_COMPORT_2
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, self.channel)
        self.error_code_result = {}

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value
        set_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, self.channel, value)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        if value:
            self.data_matrix_changed.emit(value)
        else:
            self.data_matrix_clean.emit()

    @property
    def data_matrix_color(self):
        return self._data_matrix_color

    @data_matrix_color.setter
    def data_matrix_color(self, value):
        self._data_matrix_color = value
        self.data_matrix_color_changed.emit(value)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)
        if not value:
            self.result_clean.emit()
            return
        if value == STR_OK:
            self.result_color_changed.emit(LIGHT_SKY_BLUE)
        else:
            self.result_color_changed.emit(RED)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}

    def begin(self):
        self.init_result()
