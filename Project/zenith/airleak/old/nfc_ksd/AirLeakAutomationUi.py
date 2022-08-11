import serial.tools.list_ports
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QWidget

from process_package.check_string import check_dm
from process_package.component.CustomComponent import Button, Label, ComboBox
from process_package.old.SerialMachine import SerialMachine
from process_package.old.defined_serial_port import ports, get_serial_available_list
from process_package.resource.color import LIGHT_SKY_BLUE, RED, BLUE
from process_package.resource.string import STR_OK, COMPORT_SECTION, MACHINE_COMPORT_1
from process_package.tools.Config import get_config_value, set_config_value

SLOT_MINIMUM_WIDTH = 300
AIR_LEAK_NFC_COUNT = 4


class AirLeakSlot(QGroupBox):
    def __init__(self, slot):
        super(AirLeakSlot, self).__init__()
        self.slot = slot
        self.setTitle(f"SLOT {self.slot + 1}")
        self.create_component()

    @property
    def dm(self):
        return self._dm

    @dm.setter
    def dm(self, dm):
        if isinstance(dm, str):
            self._dm = check_dm(dm)
            self.dm_label.setText(dm)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, result):
        if isinstance(result, str):
            self._result = result
            self.result_label.setText(result)
            if result == STR_OK:
                self.result_label.set_color(LIGHT_SKY_BLUE)
            else:
                self.result_label.set_color(RED)

    def create_component(self):
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(dm_label := Label())
        layout.addWidget(result_label := Label())

        self.result_label = result_label
        self.result_label.setMinimumWidth(SLOT_MINIMUM_WIDTH)
        self.dm_label = dm_label


class AirLeakAutomationUi(QWidget):
    def __init__(self, parent=None):
        super(AirLeakAutomationUi, self).__init__(parent)
        self.setLayout(layout := QVBoxLayout())
        layout.addLayout(comport_layout := QHBoxLayout())
        comport_layout.addWidget(machine_button := Button('MACHINE'))
        comport_layout.addWidget(machine_comport := ComboBox())

        layout.addLayout(unit_grid := QGridLayout())
        self.slots = []
        for index in range(AIR_LEAK_NFC_COUNT):
            unit_grid.addWidget(slot := AirLeakSlot(index), index // 4, index % 4)
            self.slots.append(slot)

        layout.addWidget(status_group := QGroupBox('STATUS'))
        status_group.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status_label := Label())

        # machine comport
        self.machine_port_connect_button = machine_button
        self.machine_comport = machine_comport
        self.machine_comport.addItems(ports)
        self.machine_comport.setMinimumWidth(200)

        # status
        self.status_label = status_label
        self.status_label.setMinimumWidth(300)

        self.serial_machine = SerialMachine(baudrate=38400, serial_name='ksd_air_leak')
        self.machine_port_connect_button.clicked.connect(self.connect_machine_button)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)

    def fill_available_ports(self):
        serial_ports = [s.device for s in serial.tools.list_ports.comports()]
        self.machine_comport.clear()
        self.machine_comport.addItems(get_serial_available_list())

    def connect_machine_button(self, not_key=None):
        if not_key:
            button = self.machine_port_connect_button
            self.machine_comport.setCurrentText(
                get_config_value(COMPORT_SECTION, MACHINE_COMPORT_1)
            )
        else:
            button = self.sender()

        if self.serial_machine.connect_serial(self.machine_comport.currentText()):
            set_config_value(COMPORT_SECTION, MACHINE_COMPORT_1, self.serial_machine.port)
            self.serial_machine.start_machine_read()
        self.check_serial_connection()

    def check_serial_connection(self):
        if self.serial_machine.is_open:
            self.machine_port_connect_button.set_background_color(BLUE)
            self.machine_comport.setDisabled(True)
        else:
            self.machine_port_connect_button.set_background_color(RED)
            self.machine_comport.setEnabled(True)
