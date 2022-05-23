import serial.tools.list_ports
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox

from process_package.Config import get_config_value, set_config_value
from process_package.PyQtCustomComponent import Button, ComboBox, Label
from process_package.SerialMachine import SerialMachine
from process_package.defined_serial_port import ports, get_serial_available_list
from process_package.defined_variable_function import SENSOR_ATECH, COMPORT_SECTION, \
    CONFIG_FILE_NAME, CON_OS, POGO_OS, LED, VBAT_ID, C_TEST, BATTERY, MIC, PROX_TEST, PCM, Hall_IC, \
    SENSOR_RESULT_TEXT_SIZE, SENSOR_RESULT_HEIGHT_SIZE, PREVIOUS_PROCESS, PREVIOUS_PROCESS_TEXT_SIZE, BLUE, RED

NFC_IN_COUNT = 1
NFC_OUT_COUNT = 2
MACHINE_SERIAL_COUNT = 2


class SensorUI(QWidget):
    def __init__(self):
        super(SensorUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())

        # previous process
        layout.addLayout(previous_process_layout := QHBoxLayout())
        self.previous_process_label = []
        for _ in range(NFC_IN_COUNT):
            previous_process_layout.addWidget(previous_process_group := QGroupBox())
            previous_process_group.setTitle(PREVIOUS_PROCESS)
            previous_process_group.setLayout(group_layout := QVBoxLayout())
            self.previous_process_label.append(label := Label(''))
            group_layout.addWidget(label)
            label.set_font_size(size=PREVIOUS_PROCESS_TEXT_SIZE)

        # Frame
        layout.addLayout(frame_layout := QHBoxLayout())
        self.ch_frame = []
        for index in range(MACHINE_SERIAL_COUNT):
            self.ch_frame.append(ch_frame := SensorChannelLayout(index + 1))
            frame_layout.addWidget(ch_frame)

        # status
        self.status_label = Label()

        layout.addWidget(self.status_label)

        self.setWindowTitle('IR SENSOR v0.1')

        self.setMinimumWidth(640)


class CustomLabel(Label):
    def __init__(self, txt):
        super(CustomLabel, self).__init__(txt)
        # self.setFixedWidth(300)


class SensorChannelLayout(QGroupBox):
    error_number = {
        CON_OS: 1,
        POGO_OS: 2,
        LED: 3,
        Hall_IC: 10,
        VBAT_ID: 4,
        C_TEST: 5,
        BATTERY: 6,
        PROX_TEST: 8,
        MIC: 7,
        PCM: 9,
    }

    def __init__(self, channel):
        super(SensorChannelLayout, self).__init__()
        self.channel = channel

        self.setTitle(f'Channel {self.channel}')
        layout = QVBoxLayout()

        self.serialComboBox = ComboBox()
        self.serialComboBox.addItems(ports)
        self.connectButton = Button('CONN')

        layout.addLayout(comportLayout := QHBoxLayout())
        comportLayout.addWidget(self.connectButton)
        comportLayout.addWidget(self.serialComboBox)

        dm_label = CustomLabel("DM")
        self.dmInput = CustomLabel('')
        layout.addWidget(dm_label)
        layout.addWidget(self.dmInput)

        result_label = CustomLabel("RESULT")
        self.resultInput = CustomLabel('')
        self.resultInput.setFixedHeight(SENSOR_RESULT_HEIGHT_SIZE)
        self.resultInput.set_font_size(size=SENSOR_RESULT_TEXT_SIZE)

        layout.addWidget(result_label)
        layout.addWidget(self.resultInput)

        self.setLayout(layout)

        self.error_code = {name: True for name in self.error_number}

        self.serial_machine = SerialMachine(baudrate=9600, serial_name=f'{SENSOR_ATECH}{self.channel}')

        self.connectButton.clicked.connect(self.connect_machine_button)

    def fill_available_ports(self):
        serial_ports = [s.device for s in serial.tools.list_ports.comports()]
        self.serialComboBox.clear()
        self.serialComboBox.addItems(get_serial_available_list(serial_ports))

    def connect_machine_button(self, not_key=None):
        if not_key:
            button = self.connectButton
            self.serialComboBox.setCurrentText(
                get_config_value(
                    CONFIG_FILE_NAME,
                    COMPORT_SECTION,
                    f"machine_comport_{self.channel}"
                )
            )
        else:
            button = self.sender()

        if self.serial_machine.connect_serial(self.serialComboBox.currentText()):
            set_config_value(
                CONFIG_FILE_NAME,
                COMPORT_SECTION,
                f'machine_comport_{self.channel}',
                self.serial_machine.port
            )
            self.serial_machine.start_machine_read()
        self.check_serial_connection()

    def check_serial_connection(self):
        if self.serial_machine.is_open:
            self.connectButton.set_clicked(BLUE)
            self.serialComboBox.setDisabled(True)
        else:
            self.connectButton.set_clicked(RED)
            self.serialComboBox.setEnabled(True)


    def init_result_true(self):
        self.error_code = {key: True for key in self.error_number}

    def get_ecode(self):
        return ','.join([
            str(self.error_number[key]) for key, value in self.error_code.items() if not value
        ])
