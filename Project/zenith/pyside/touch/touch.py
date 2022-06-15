import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout, QGroupBox

from packages.component.CustomComponent import HBoxSerial, GroupLabel, style_sheet_setting, Widget
from packages.config.config import get_config_value
from packages.serial.MachineSerial import SerialMachine
from packages.variable.size import TOUCH_MACHINE_RESULT_FONT_SIZE, TOUCH_DATA_MATRIX_FONT_SIZE, \
    TOUCH_COMPORT_MAXIMUM_HEIGHT, \
    TOUCH_ORDER_MAXIMUM_HEIGHT, TOUCH_STATUS_MAXIMUM_HEIGHT, TOUCH_MACHINE_MINIMUM_WIDTH, \
    TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT
from packages.variable.string import MACHINE_COMPORT, ORDER_NUMBER, DATA_MATRIX, MACHINE_RESULT, STATUS, TOUCH, \
    CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1
from packages.variable.variables import logger, BAUDRATE_115200


class Touch(Widget):
    def __init__(self):
        super(Touch, self).__init__()

        # component
        self.status = None
        self.machine_result = None
        self.data_matrix = None
        self.order_number = None
        self.comport = None

        self.setup_ui()

        self.setup_program()

        self.show()

    def setup_program(self):
        self.comport.setup_serial(
            get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1),
            baudrate=BAUDRATE_115200,
            serial_name=TOUCH
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(comport_group := QGroupBox(MACHINE_COMPORT))
        comport_group.setLayout(comport := HBoxSerial())

        layout.addWidget(order_number := GroupLabel(title=ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=DATA_MATRIX, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine_result := GroupLabel(title=MACHINE_RESULT, font_size=TOUCH_MACHINE_RESULT_FONT_SIZE))
        layout.addWidget(status := GroupLabel(title=STATUS))

        comport_group.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order_number.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        status.setMaximumHeight(TOUCH_STATUS_MAXIMUM_HEIGHT)
        machine_result.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)

        self.comport = comport
        self.order_number = order_number
        self.data_matrix = data_matrix
        self.machine_result = machine_result
        self.status = status

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            print("Right")
        if e.buttons() & Qt.MidButton:
            print("middle")


if __name__ == '__main__':
    logger.info("start touch process")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = Touch()
    sys.exit(app.exec())
