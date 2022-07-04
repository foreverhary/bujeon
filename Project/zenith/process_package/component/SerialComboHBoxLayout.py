from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QHBoxLayout, QComboBox

from process_package.component.CustomComponent import Button
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.color import BLUE, RED
from process_package.tools.SerialPort import SerialPort


class SerialComboHBoxLayout(QHBoxLayout):
    comport_save = Signal(str)
    serial_output_data = Signal(str)

    def nfc_ports(self, value):
        available_ports = get_serial_available_list()
        for port in value:
            available_ports.remove(port)
        self._model.available_comport = available_ports

    def set_available_ports(self, value):
        self._model.available_comport = value

    def begin(self):
        self._model.begin()
        self._control.comport_clicked()

    def __init__(self, parent_model, button_text='CONNECT'):
        super(SerialComboHBoxLayout, self).__init__()
        self._model = SerialComboHBoxLayoutModel(parent_model)
        self._control = SerialComboHBoxLayoutControl(self._model)

        # UI
        self.addWidget(comport := QComboBox())
        self.addWidget(button := Button(button_text))

        self.comport = comport
        self.button = button

        # serial data out
        self._control.serial_output_data.connect(self.serial_output_data.emit)
        self._control.serial_connection.connect(self.serial_connection)

        # connect widgets to controller
        self.comport.currentIndexChanged.connect(self._control.change_comport)
        self.button.clicked.connect(self._control.comport_clicked)

        # listen for model event signals
        self._model.comport_save.connect(self.comport_save.emit)

        self._model.comport_index_changed.connect(self.comport.setCurrentIndex)
        self._model.comport_connection_changed.connect(self.serial_connection)
        self._model.available_comport_changed.connect(self.fill_combobox)

        # listen for out of class event signals

    @Slot(list)
    def fill_combobox(self, rows):
        self.comport.clear()
        self.comport.addItems(rows)

    @Slot(bool)
    def serial_connection(self, connection):
        self.button.set_background_color(BLUE if connection else RED)
        self.comport.setEnabled(not connection)


class SerialComboHBoxLayoutControl(QObject):
    serial_output_data = Signal(str)
    serial_connection = Signal(bool)

    def __init__(self, model):
        super(SerialComboHBoxLayoutControl, self).__init__()
        self._model = model

        self.serial = SerialPort()
        self.serial.line_out_signal.connect(self.serial_output_data.emit)
        self.serial.serial_connection_signal.connect(self.serial_connection.emit)

    @Slot(int)
    def change_comport(self, comport_index):
        self._model.comport_index = comport_index

    @Slot()
    def comport_clicked(self):
        self.serial.set_port_baudrate(self._model.available_comport[self._model.comport_index], self._model.baudrate)
        self._model.comport_connection = self.serial.connect_toggle()


class SerialComboHBoxLayoutModel(QObject):
    comport_index_changed = Signal(int)
    comport_connection_changed = Signal(bool)
    comport_save = Signal(str)
    available_comport_changed = Signal(list)

    def __init__(self, parent_model):
        super(SerialComboHBoxLayoutModel, self).__init__()
        self.name = parent_model.name
        self.baudrate = parent_model.baudrate
        self.comport = parent_model.comport

    @property
    def comport_index(self):
        return self._comport_index

    @comport_index.setter
    def comport_index(self, value):
        self._comport_index = value
        self.comport_index_changed.emit(value)
        self.comport = self.available_comport[value]

    @property
    def comport_connection(self):
        return self._comport_connection

    @comport_connection.setter
    def comport_connection(self, value):
        self._comport_connection = bool(value)
        self.comport_connection_changed.emit(self._comport_connection)
        if self._comport_connection:
            self.comport_save.emit(self.available_comport[self._comport_index])
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
        backup_comport = self.comport
        self.available_comport_changed.emit(ports)
        if backup_comport and backup_comport in ports:
            self.comport_index = ports.index(backup_comport)

    def begin(self):
        if self.comport:
            self.comport_index = self.available_comport.index(self.comport)
