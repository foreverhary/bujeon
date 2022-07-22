from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.component.CustomComponent import Widget
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.string import STR_ORDER_NUMBER, STR_DATA_MATRIX, STR_MACHINE_RESULT, STR_MACHINE_COMPORT, \
    STR_DATA_MATRIX_WAITING

# size
TOUCH_COMPORT_MAXIMUM_HEIGHT = 68
TOUCH_ORDER_MAXIMUM_HEIGHT = 72
TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT = 90
TOUCH_MACHINE_MINIMUM_WIDTH = 500
TOUCH_STATUS_MAXIMUM_HEIGHT = 72
TOUCH_DATA_MATRIX_FONT_SIZE = 50
TOUCH_MACHINE_RESULT_FONT_SIZE = 120


class TouchView(Widget):
    def __init__(self, *args):
        super(TouchView, self).__init__()
        self._model, self._control = args

        # ui
        layout = QVBoxLayout(self)
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := SerialComboHBoxLayout())

        layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX,
                                                   font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(data_matrix_waiting := GroupLabel(title=STR_DATA_MATRIX_WAITING,
                                                           font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine := GroupLabel(title=STR_MACHINE_RESULT,
                                               font_size=TOUCH_MACHINE_RESULT_FONT_SIZE,
                                               is_clean=True,
                                               clean_time=4000))

        # shape size
        comport_box.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        data_matrix_waiting.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        machine.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)

        # assign
        self.order = order.label
        self.data_matrix = data_matrix.label
        self.data_matrix_waiting = data_matrix_waiting.label
        self.machine = machine.label

        # init variable
        comport.set_available_ports(get_serial_available_list())
        comport.set_baudrate(115200)
        comport.begin()

        # connect widgets to controller
        comport.serial_output_data.connect(self._control.receive_serial_data)

        # listen for model event signals
        self._model.order_number_changed.connect(self.order.setText)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_waiting_changed.connect(self.data_matrix_waiting.setText)
        self._model.machine_result_changed.connect(self.machine.setText)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == order_action:
            OrderNumberDialog(self._model)
        elif action == db_action:
            MSSqlDialog()
