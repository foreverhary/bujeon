from PySide2.QtCore import Signal
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox

from process_package.Views.CustomComponent import Label, Button
from process_package.controllers.SerialPort import SerialPort
from process_package.defined_serial_port import get_serial_available_list
from process_package.defined_variable_function import logger
from process_package.resource.color import BLUE, RED
from process_package.resource.size import DEFAULT_FONT_SIZE


class GroupLabel(QGroupBox):
    def __init__(self, title='', is_clean=False, font_size=DEFAULT_FONT_SIZE):
        super(GroupLabel, self).__init__()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(label := Label(is_clean=is_clean))

        self.label = label
        self.label.set_font_size(size=font_size)


class HBoxSerial(QHBoxLayout):
    serial_line_signal = Signal(str)

    def __init__(self, name, button_text='CONNECT'):
        super(HBoxSerial, self).__init__()
        self.serial = SerialPort(name)
        self.addWidget(comport := QComboBox())
        self.addWidget(button := Button(button_text))

        self.comport = comport
        self.button = button

        self.serial.line_out_signal.connect(self.serial_line_signal.emit)
        self.button.clicked.connect(self.clicked_button)

    def check_connect(self):
        if self.serial.isOpen():
            self.button.set_clicked(BLUE)
            self.comport.setDisabled(True)
        else:
            self.button.set_clicked(RED)
            self.comport.setEnabled(True)

    def setup_serial(self, port, baudrate=QSerialPort.Baud9600):
        self.fill_available_ports()
        self.comport.setCurrentText(port := port or self.comport.currentText())
        self.serial.set_port_baudrate(port, baudrate)
        if not self.serial.open():
            logger.warn(f"{self.serial.portName()} cannot connect!!")
        self.check_connect()

    def fill_available_ports(self):
        self.comport.clear()
        self.comport.addItems(get_serial_available_list())

    def toggle_serial(self):
        return self.serial.close() if self.serial.isOpen() else self.serial.open()

    def set_port(self):
        self.serial.port = self.comport.currentText() or None

    def clicked_button(self):
        self.set_port()
        if self.serial.connect_toggle():
            self.button.set_clicked(BLUE)
            self.comport.setDisabled(True)
        else:
            self.button.set_clicked(RED)
            self.comport.setEnabled(True)
