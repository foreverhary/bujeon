from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox

from process_package.tools.Config import get_config_value, set_config_value
from process_package.component.CustomComponent import Button, Label, ComboBox, Widget
from process_package.old.SerialMachine import SerialMachine
from process_package.old.defined_serial_port import ports, get_serial_available_list
from process_package.old.defined_variable_function import AIR_LEAK_DM_UNIT_WIDTH_SIZE, AIR_LEAK_RESULT_SIZE, \
    AIR_LEAK_UNIT_COUNT, \
    UNIT, RESULT, AIR_LEAK_RESULT_FONT_SIZE, AIR_LEAK_DM_UNIT_FONT_SIZE, COMPORT_SECTION, \
    MACHINE_COMPORT_1, STR_AIR_LEAK, CONFIG_FILE_NAME, BLUE, RED, AIR_LEAK_DM_UNIT_HEIGHT_SIZE


class AirLeakUi(Widget):
    def __init__(self, parent=None):
        super(AirLeakUi, self).__init__()

        # comport
        self.machine_port_connect_button = Button('MACHINE')
        self.machine_comport = ComboBox()

        self.machine_comport.addItems(ports)
        self.machine_comport.setMinimumWidth(200)

        comport_layout = QHBoxLayout()
        comport_layout.addWidget(self.machine_port_connect_button)
        comport_layout.addWidget(self.machine_comport)

        # status
        self.status_label = Label()
        self.status_label.setMinimumWidth(AIR_LEAK_RESULT_SIZE)

        # unit
        self.out_grid_layout = QGridLayout()
        result_label = Label(RESULT)
        result_label.setMinimumWidth(AIR_LEAK_RESULT_SIZE)
        unit_out_label = Label(UNIT)
        unit_out_label.setMinimumWidth(AIR_LEAK_DM_UNIT_WIDTH_SIZE)
        self.out_grid_layout.addWidget(unit_out_label, 0, 1)
        self.out_grid_layout.addWidget(result_label, 0, 0)
        self.result_label = Label()
        self.result_label.setMinimumWidth(AIR_LEAK_DM_UNIT_WIDTH_SIZE)
        self.result_label.setMinimumSize(AIR_LEAK_DM_UNIT_WIDTH_SIZE, AIR_LEAK_DM_UNIT_HEIGHT_SIZE)
        self.result_label.set_font_size(size=AIR_LEAK_RESULT_FONT_SIZE)
        self.out_grid_layout.addWidget(self.result_label, 1, 0, 5, 1)

        self.unit_list = [Label() for _ in
                          range(AIR_LEAK_UNIT_COUNT)]
        for index, out_item in enumerate(self.unit_list):
            out_item.set_font_size(size=AIR_LEAK_DM_UNIT_FONT_SIZE)
            self.out_grid_layout.addWidget(out_item, index + 1, 1)

        out_group = QGroupBox("OUT")
        out_group.setLayout(self.out_grid_layout)

        unit_layout = QHBoxLayout()
        unit_layout.addWidget(out_group)

        layout = QVBoxLayout()
        layout.addLayout(comport_layout)

        layout.addLayout(unit_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

        self.serial_machine = SerialMachine(baudrate=9600, serial_name=STR_AIR_LEAK)
        self.machine_port_connect_button.clicked.connect(self.connect_machine_button)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)

    def fill_available_ports(self):
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
