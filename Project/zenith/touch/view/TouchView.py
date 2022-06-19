from PySide2.QtCore import Qt, Slot
from PySide2.QtWidgets import QVBoxLayout, QGroupBox

from process_package.Views.CustomComponent import Widget
from process_package.Views.CustomMixComponent import GroupLabel, HBoxComboButton
from process_package.controllers.OrderNumberDialog import OrderNumberDialog
from process_package.resource.color import RED, LIGHT_SKY_BLUE
from process_package.resource.size import TOUCH_MACHINE_MINIMUM_WIDTH, TOUCH_DATA_MATRIX_FONT_SIZE, \
    TOUCH_MACHINE_RESULT_FONT_SIZE, TOUCH_COMPORT_MAXIMUM_HEIGHT, TOUCH_ORDER_MAXIMUM_HEIGHT, \
    TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT, TOUCH_STATUS_MAXIMUM_HEIGHT
from process_package.resource.string import STR_ORDER_NUMBER, STR_DATA_MATRIX, STR_MACHINE_RESULT, STR_STATUS, \
    STR_MACHINE_COMPORT, STR_TOUCH_PROCESS, STR_TOUCH, STR_NG


class TouchView(Widget):
    def __init__(self, *args):
        super(TouchView, self).__init__(*args)
        self._model, self._control = args

        # ui
        layout = QVBoxLayout(self)
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := HBoxComboButton(STR_TOUCH))

        layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine := GroupLabel(title=STR_MACHINE_RESULT, font_size=TOUCH_MACHINE_RESULT_FONT_SIZE))
        layout.addWidget(status := GroupLabel(title=STR_STATUS, blink_time=100))

        comport_box.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        status.setMaximumHeight(TOUCH_STATUS_MAXIMUM_HEIGHT)
        machine.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)

        self.comport = comport
        self.order = order.label
        self.data_matrix = data_matrix.label
        self.machine = machine.label
        self.status = status.label

        self.setWindowTitle(STR_TOUCH_PROCESS)

        # connect widgets to controller
        self.comport.comport.currentIndexChanged.connect(self._control.change_comport)
        self.comport.button.clicked.connect(self._control.comport_clicked)

        # listen for model event signals
        self._model.comport_changed.connect(self.comport.comport.setCurrentText)
        self._model.comport_open_changed.connect(self.comport.serial_connection)
        self._model.available_comport_changed.connect(self.comport.fill_combobox)

        self._model.order_number_changed.connect(self.order.setText)
        self._model.data_matrix_changed.connect(self.change_data_matrix)
        self._model.machine_result_changed.connect(self.change_machine_result)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

    @Slot(str)
    def change_data_matrix(self, value):
        if value:
            self.machine.clean()
            self.data_matrix.setText(value)

    @Slot(str)
    def change_machine_result(self, value):
        self.data_matrix.clean()
        self.machine.setText(value)
        self.machine.set_background_color((LIGHT_SKY_BLUE, RED)[value == STR_NG])
