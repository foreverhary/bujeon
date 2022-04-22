from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QWidget

from process_package.PyQtCustomComponent import Button, Label, ComboBox
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import AIR_LEAK_DM_UNIT_SIZE, AIR_LEAK_RESULT_SIZE, AIR_LEAK_UNIT_COUNT, \
    UNIT, RESULT, WRITE


class AirLeakUi(QWidget):
    def __init__(self, parent=None):
        super(AirLeakUi, self).__init__(parent)

        # comport
        self.nfc_in_connect_button = Button('NFC')
        self.nfc_in_comport = ComboBox()
        self.machine_connect_button = Button('MACHINE')
        self.machine_comport = ComboBox()
        self.nfc_out_connect_button = Button('NFC')
        self.nfc_out_comport = ComboBox()

        self.nfc_in_comport.addItems(ports)
        self.nfc_in_comport.setMinimumWidth(200)
        self.machine_comport.addItems(ports)
        self.machine_comport.setMinimumWidth(200)
        self.nfc_out_comport.addItems(ports)
        self.nfc_out_comport.setMinimumWidth(200)

        comport_layout = QHBoxLayout()
        comport_layout.addWidget(self.nfc_in_connect_button)
        comport_layout.addWidget(self.nfc_in_comport)
        comport_layout.addWidget(self.machine_connect_button)
        comport_layout.addWidget(self.machine_comport)
        comport_layout.addWidget(self.nfc_out_connect_button)
        comport_layout.addWidget(self.nfc_out_comport)

        # unit
        in_group = QGroupBox("IN")
        self.in_grid_layout = QGridLayout()
        unit_in_label = Label("UNIT")
        unit_in_label.setMinimumWidth(AIR_LEAK_DM_UNIT_SIZE)
        self.in_grid_layout.addWidget(unit_in_label)

        out_group = QGroupBox("OUT")
        self.out_grid_layout = QGridLayout()
        unit_out_label = Label(UNIT)
        unit_out_label.setMinimumWidth(AIR_LEAK_DM_UNIT_SIZE)
        result_label = Label(RESULT)
        result_label.setMinimumWidth(AIR_LEAK_RESULT_SIZE)
        write_label = Label(WRITE)
        write_label.setMinimumWidth(AIR_LEAK_RESULT_SIZE)
        self.out_grid_layout.addWidget(unit_out_label, 0, 0)
        self.out_grid_layout.addWidget(result_label, 0, 1)
        self.out_grid_layout.addWidget(write_label, 0, 2)

        self.unit_in_list = [Label() for _ in range(AIR_LEAK_UNIT_COUNT)]
        self.unit_out_list = [{UNIT: Label(), RESULT: Label(), WRITE: Label()} for _ in
                              range(AIR_LEAK_UNIT_COUNT)]

        for index, (in_item, out_item) in enumerate(zip(self.unit_in_list, self.unit_out_list)):
            self.in_grid_layout.addWidget(in_item, index + 1, 0)
            self.out_grid_layout.addWidget(out_item[UNIT], index + 1, 0)
            self.out_grid_layout.addWidget(out_item[RESULT], index + 1, 1)
            self.out_grid_layout.addWidget(out_item[WRITE], index + 1, 2)

        in_group = QGroupBox("IN")
        in_group.setLayout(self.in_grid_layout)
        out_group = QGroupBox("OUT")
        out_group.setLayout(self.out_grid_layout)

        unit_layout = QHBoxLayout()
        unit_layout.addWidget(in_group)
        unit_layout.addWidget(out_group)

        layout = QVBoxLayout()
        layout.addLayout(comport_layout)
        layout.addLayout(unit_layout)
        self.setLayout(layout)

    def input_dm(self, dm):
        pass

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)
