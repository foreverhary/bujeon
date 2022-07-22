from PySide2.QtCore import Signal, Slot
from PySide2.QtWidgets import QHBoxLayout, QComboBox

from process_package.component.CustomComponent import Button
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.color import BLUE, RED
from process_package.resource.string import MACHINE_COMPORT_1, COMPORT_SECTION
from process_package.tools.Config import get_config_value, set_config_value
from process_package.tools.SerialPort import SerialPort


class SerialComboHBoxLayout(QHBoxLayout):
    comport_save = Signal(str)
    serial_output_data = Signal(str)

    def exclude_nfc_ports(self, value):
        available_ports = get_serial_available_list()
        for port in value:
            available_ports.remove(port)
        self.available_comport = available_ports

    def set_available_ports(self, value):
        self.available_comport = value

    def set_baudrate(self, value):
        self.serial.set_baudrate(value)

    def set_comport(self, value):
        self.serial.set_port(value)

    def begin(self):
        if self.serial.port:
            self.comport_index = self.available_comport.index(self.serial.port)
        self.comport_clicked()

    def __init__(self, button_text='CONNECT', port_cfg=MACHINE_COMPORT_1):
        super(SerialComboHBoxLayout, self).__init__()

        self.port_cfg = port_cfg

        # UI
        self.addWidget(comport := QComboBox())
        self.addWidget(button := Button(button_text))

        self.comport = comport
        self.button = button

        # init variable
        self.serial = SerialPort()

        # serial data out
        self.serial.line_out_signal.connect(self.serial_output_data.emit)
        self.serial.serial_connection_signal.connect(self.serial_connection)

        # connect widgets to controller
        self.comport.currentIndexChanged.connect(self.change_comport)
        self.button.clicked.connect(self.comport_clicked)

    @Slot(list)
    def fill_combobox(self, rows):
        self.comport.clear()
        self.comport.addItems(rows)

    @Slot(bool)
    def serial_connection(self, connection):
        self.button.set_background_color(BLUE if connection else RED)
        self.comport.setEnabled(not connection)

    @Slot(int)
    def change_comport(self, comport_index):
        self.comport_index = comport_index

    @Slot()
    def comport_clicked(self):
        self.comport_connection = self.serial.connect_toggle()

    @property
    def comport_index(self):
        return self._comport_index

    @comport_index.setter
    def comport_index(self, value):
        self._comport_index = value
        self.comport.setCurrentIndex(value)
        self.serial.port = self.available_comport[value]

    @property
    def comport_connection(self):
        return self._comport_connection

    @comport_connection.setter
    def comport_connection(self, value):
        self._comport_connection = bool(value)
        self.serial_connection(self._comport_connection)
        if self._comport_connection:
            set_config_value(COMPORT_SECTION, self.port_cfg, self.available_comport[self._comport_index])
        else:
            self.available_comport = get_serial_available_list()

    @property
    def available_comport(self):
        return self._available_comport

    @available_comport.setter
    def available_comport(self, value):
        port_numbers = [int(port[3:]) for port in value]
        port_numbers.sort()
        ports = [f"COM{port}" for port in port_numbers]
        self._available_comport = ports
        self.fill_combobox(ports)
        port = get_config_value(COMPORT_SECTION, self.port_cfg)
        if port in ports:
            self.comport.setCurrentIndex(ports.index(port))
