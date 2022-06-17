from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtSerialPort import QSerialPort

from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.controllers.OrderNumberDialog import OrderNumberDialog
from process_package.tools.SerialPort import SerialPort
from process_package.resource.string import STR_TOUCH


class TouchControl(QObject):
    serial_is_open = Signal(bool)

    def __init__(self, model):
        super(TouchControl, self).__init__()
        self._model = model

        self.serial = SerialPort(STR_TOUCH)
        self.keyboard_listener = LineReadKeyboard()

        # controller event connect
        self.serial.line_out_signal.connect(self.input_serial_data)
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

    @Slot(int)
    def change_comport(self, comport):
        self._model.comport = comport

    @Slot()
    def comport_clicked(self):
        self.serial.set_port_baudrate(self._model.comport, QSerialPort.Baud115200)
        self._model.comport_open = self.serial.close() if self.serial.isOpen() else self.serial.open()

    @Slot()
    def order_close(self):
        print("ok")
        self._model.get_order_number()

    def input_keyboard_line(self, value):
        self._model.data_matrix = value

    def input_serial_data(self, value):
        self._model.machine_result = value

    def begin(self):
        self.comport_clicked()

    def open_order_number_dialog(self):
        order = OrderNumberDialog()
        order.close_signal.connect(self.order_close)

    def open_mssql_dialog(self):
        MSSqlDialog()
