from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QVBoxLayout, QGroupBox

from process_package.Views.CustomComponent import Widget
from process_package.Views.CustomMixComponent import GroupLabel, HBoxComboButton
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.controllers.OrderNumberDialog import OrderNumberDialog
from process_package.resource.color import RED, LIGHT_SKY_BLUE
from process_package.resource.size import TOUCH_MACHINE_MINIMUM_WIDTH, TOUCH_DATA_MATRIX_FONT_SIZE, \
    TOUCH_MACHINE_RESULT_FONT_SIZE, TOUCH_COMPORT_MAXIMUM_HEIGHT, TOUCH_ORDER_MAXIMUM_HEIGHT, \
    TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT, TOUCH_STATUS_MAXIMUM_HEIGHT
from process_package.resource.string import STR_ORDER_NUMBER, STR_DATA_MATRIX, STR_MACHINE_RESULT, STR_STATUS, \
    STR_MACHINE_COMPORT, STR_TOUCH_PROCESS, STR_TOUCH, STR_NG, STR_DATA_MATRIX_WAITING


class TouchView(Widget):
    def __init__(self, *args):
        super(TouchView, self).__init__(*args)
        self._model, self._control = args

        # ui
        layout = QVBoxLayout(self)
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := SerialComboHBoxLayout(self._model))

        layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(data_matrix_waiting := GroupLabel(title=STR_DATA_MATRIX_WAITING, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine := GroupLabel(title=STR_MACHINE_RESULT,
                                               font_size=TOUCH_MACHINE_RESULT_FONT_SIZE,
                                               is_clean=True,
                                               clean_time=4000))
        layout.addWidget(status := GroupLabel(title=STR_STATUS, blink_time=100))

        comport_box.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        data_matrix_waiting.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        status.setMaximumHeight(TOUCH_STATUS_MAXIMUM_HEIGHT)
        machine.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)

        self.comport = comport
        self.order = order.label
        self.data_matrix = data_matrix.label
        self.data_matrix_waiting = data_matrix_waiting.label
        self.machine = machine.label
        self.status = status.label

        self.setWindowTitle(STR_TOUCH_PROCESS)

        # connect widgets to controller
        self.comport.comport_save.connect(self._control.comport_save)
        self.comport.serial_output_data.connect(self._control.input_serial_data)

        # listen for model event signals
        self._model.order_number_changed.connect(self.order.setText)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_waiting_changed.connect(self.data_matrix_waiting.setText)
        self._model.machine_result_changed.connect(self.change_machine_result)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

    @Slot(str)
    def change_machine_result(self, value):
        self.machine.setText(value)
        self.machine.set_background_color((LIGHT_SKY_BLUE, RED)[value == STR_NG])
