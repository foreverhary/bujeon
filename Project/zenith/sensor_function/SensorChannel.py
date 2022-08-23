import socket

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QGroupBox, QVBoxLayout

from process_package.component.CustomComponent import Label, get_time, LabelNFC
from process_package.component.NFCComponent import NFCComponent
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.models.BasicModel import BasicModel
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.string import STR_RESULT, STR_CON_OS, STR_POGO_OS, STR_LED, STR_HALL_IC, STR_VBAT_ID, \
    STR_C_TEST, STR_BATTERY, STR_PROX_TEST, STR_MIC, STR_PCM, STR_SEN, MACHINE_COMPORT_1, MACHINE_COMPORT_2, \
    STR_DATA_MATRIX, STR_SENSOR, STR_OK, STR_NG, STR_PROCESS_RESULTS
from process_package.tools.CommonFunction import write_beep, is_result_in_nfc, get_write_result_in_nfc
from process_package.tools.mssql_connect import MSSQL

RESULT_HEIGHT = 350
RESULT_FONT_SUZE = 100


class SensorChannel(QGroupBox):
    def __init__(self, channel):
        super(SensorChannel, self).__init__()
        self._model = SensorChannelModel()
        self._control = SensorChannelControl(self._model)

        # UI
        self.setTitle(f"Channel {channel}")
        layout = QVBoxLayout(self)
        layout.addLayout(comport := SerialComboHBoxLayout(
                button_text='CONN',
                port_cfg=MACHINE_COMPORT_1 if channel == 1 else MACHINE_COMPORT_2))
        layout.addWidget(Label('DM'))
        layout.addWidget(data_matrix := LabelNFC())
        layout.addWidget(Label(STR_RESULT))
        layout.addWidget(result := Label())
        layout.addWidget(nfc := NFCComponent(f"NFC{channel}"))

        # size & font size
        result.setFixedHeight(RESULT_HEIGHT)
        result.set_font_size(RESULT_FONT_SUZE)

        comport.set_baudrate(9600)

        # assign
        self.comport = comport
        self.data_matrix = data_matrix
        self.result = result
        self.nfc = nfc

        # view connect control
        self.comport.serial_output_data.connect(self._control.input_serial_data)
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # control connect view
        self._control.nfc_write.connect(nfc.write)
        self._control.nfc_write_bytes.connect(nfc.write)

        # model connect view
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_background_color_changed.connect(self.data_matrix.set_background_color)
        self._model.machine_result_changed.connect(self.result.setText)

    def exclude_nfc_ports(self, value):
        self.comport.exclude_nfc_ports(value)

    def set_port(self, value):
        self.nfc.set_port(value)

    def begin(self):
        self.comport.begin()


class SensorChannelControl(QObject):
    nfc_write = Signal(str)
    nfc_write_bytes = Signal(bytes)

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
        if value[:2] not in ['L,', 'R,']:
            return
        # split_list = value.split(',')
        split_list = [item for item in value.split(',') if item]
        if len(split_list) < 2:
            return

        for item in split_list[1:]:
            if item not in [STR_OK, STR_NG]:
                return

        self._model.init_result()
        split_list = split_list[1:-1]
        for item, key in zip(split_list, self._model.error_code_result):
            self._model.error_code_result[key] = item == STR_OK
        if False in self._model.error_code_result.values():
            self._model.machine_result = STR_NG
        else:
            self._model.machine_result = STR_OK
        self._model.data_matrix = ''

    @Slot(dict)
    def receive_nfc_data(self, value):
        self._model.data_matrix_background_color = LIGHT_SKY_BLUE

        if not self._model.machine_result:
            return

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        machine_result_bit = 1 if self._model.machine_result == STR_OK else 0

        if not (results_byte := value.get(STR_PROCESS_RESULTS)) \
                or self.data_matrix != data_matrix \
                or not is_result_in_nfc(self, results_byte, machine_result_bit):
            self.data_matrix = data_matrix
            msg = data_matrix.encode() + b','
            msg += get_write_result_in_nfc(self, results_byte, machine_result_bit)
            self.nfc_write_bytes.emit(msg)
            self.delay_write_count = 2
        else:
            write_beep()
            self.sql_update()
            self._model.machine_result = ''
            self._model.data_matrix = data_matrix

    def sql_update(self):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       self.data_matrix,
                                       get_time(),
                                       self._model.machine_result,
                                       STR_SENSOR,
                                       self._model.get_error_code(),
                                       socket.gethostbyname(socket.gethostname()))


class SensorChannelModel(BasicModel):
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

    def __init__(self):
        super(SensorChannelModel, self).__init__()
        self.init_result()

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}

    def begin(self):
        self.init_result()
