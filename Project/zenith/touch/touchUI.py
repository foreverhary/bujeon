import serial.tools.list_ports
from PySide2.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QComboBox

from process_package.Views.CustomComponent import Label, Button
from process_package.Views.CustomComponent import Widget
from process_package.Views.CustomMixComponent import GroupLabel, HBoxSerial
from process_package.defined_serial_port import get_serial_available_list
from process_package.defined_variable_function import TOUCH
from process_package.resource.size import TOUCH_MACHINE_MINIMUM_WIDTH, TOUCH_DATA_MATRIX_FONT_SIZE, \
    TOUCH_MACHINE_RESULT_FONT_SIZE, TOUCH_COMPORT_MAXIMUM_HEIGHT, TOUCH_ORDER_MAXIMUM_HEIGHT, \
    TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT, TOUCH_STATUS_MAXIMUM_HEIGHT
from process_package.resource.string import STR_ORDER_NUMBER, STR_DATA_MATRIX, STR_MACHINE_RESULT, STR_STATUS, \
    STR_MACHINE_COMPORT, STR_TOUCH_PROCESS


class TouchUI(Widget):
    def __init__(self):
        super(TouchUI, self).__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := HBoxSerial(TOUCH))

        layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine := GroupLabel(title=STR_MACHINE_RESULT, font_size=TOUCH_MACHINE_RESULT_FONT_SIZE))
        layout.addWidget(status := GroupLabel(STR_STATUS))

        comport_box.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        status.setMaximumHeight(TOUCH_STATUS_MAXIMUM_HEIGHT)
        machine.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)
        comport.serial_line_signal.connect(lambda x: print(x))

        self.comport = comport
        self.order = order.label
        self.data_matrix = data_matrix.label
        self.machine = machine.label
        self.status = status.label

        self.setWindowTitle(STR_TOUCH_PROCESS)
