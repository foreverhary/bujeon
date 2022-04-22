import serial.tools.list_ports
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox

from process_package.Config import Config, get_config_value, set_config_value
from process_package.PyQtCustomComponent import Label, ComboBox, Button
from process_package.SerialMachine import SerialMachine
from process_package.defined_serial_port import ports, get_serial_available_list
from process_package.defined_variable_function import COMPORT_SECTION, SENSOR_CONFIG_FILENAME, SENSOR_ATECH


class CustomLabel(Label):
    def __init__(self, txt):
        super(CustomLabel, self).__init__(txt)
        self.setFixedWidth(300)


class SensorChannelLayout(QGroupBox):
    def __init__(self, parent, channel):
        super(SensorChannelLayout, self).__init__()
        self.config = Config('sensor.ini')
        self.parent = parent
        self.channel = channel

        self.setTitle(f'Channel {channel}')
        layout = QVBoxLayout()

        self.serialComboBox = ComboBox()
        self.serialComboBox.addItems(ports)
        self.connectButton = Button('Conn')
        comport_layout = QHBoxLayout()
        comport_layout.addWidget(self.connectButton)
        comport_layout.addWidget(self.serialComboBox)
        layout.addLayout(comport_layout)

        dm_label = CustomLabel(f"CH{channel} DM")
        self.dmInput = CustomLabel('')
        layout.addWidget(dm_label)
        layout.addWidget(self.dmInput)

        result_label = CustomLabel(f"CH{channel} RESULT")
        self.resultInput = CustomLabel('')
        self.resultInput.setFixedHeight(350)

        layout.addWidget(result_label)
        layout.addWidget(self.resultInput)

        self.setLayout(layout)

        self.serial_machine = SerialMachine(baudrate=9600, serial_name=SENSOR_ATECH)

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
                    SENSOR_CONFIG_FILENAME,
                    COMPORT_SECTION,
                    f"machine_comport_{self.channel}"
                )
            )
        else:
            button = self.sender()

        if self.serial_machine.connect_with_button_color(self.serialComboBox.currentText(), button):
            set_config_value(
                SENSOR_CONFIG_FILENAME,
                COMPORT_SECTION,
                f'machine_comport_{self.channel}',
                self.serial_machine.port
            )
