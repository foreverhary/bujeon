import serial.tools.list_ports
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox

from process_package.PyQtCustomComponent import Label, Button
from process_package.defined_serial_port import get_serial_available_list


class TouchUI(QWidget):
    def __init__(self):
        super(TouchUI, self).__init__()

        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(comport_box := QGroupBox("MACHINE COMPORT"))
        comport_box.setLayout(comport_layout := QHBoxLayout())
        comport_layout.addWidget(comport_combobox := QComboBox())
        comport_layout.addWidget(comport_button := Button("CONNECT"))

        layout.addWidget(order_box := QGroupBox("ORDER NUMBER"))
        order_box.setLayout(order_layout := QVBoxLayout())
        order_layout.addWidget(order := Label(''))

        layout.addWidget(dm_box := QGroupBox("DATA MATRIX"))
        dm_box.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm := Label(''))

        layout.addWidget(machine_box := QGroupBox("MACHINE RESULT"))
        machine_box.setLayout(machine_layout := QVBoxLayout())
        machine_layout.addWidget(machine := Label(''))

        layout.addWidget(status_box := QGroupBox("STATUS"))
        status_box.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status := Label(''))

        self.comport_combobox = comport_combobox
        self.fill_available_ports()
        self.connect_button = comport_button
        self.order_label = order
        self.dm_label = dm
        self.machine_label = machine
        self.status_label = status
        self.dm_label.setMinimumWidth(500)
        self.dm_label.set_text_property(size=80)
        self.machine_label.set_text_property(size=120)

        self.setWindowTitle('Touch Process')

    def fill_available_ports(self):
        serial_ports = [s.device for s in serial.tools.list_ports.comports()]
        self.comport_combobox.clear()
        self.comport_combobox.addItems(get_serial_available_list(serial_ports))
