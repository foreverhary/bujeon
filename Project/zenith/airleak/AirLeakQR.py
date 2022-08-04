import socket
import sys

from PySide2.QtCore import Signal
from PySide2.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.check_string import check_dm
from process_package.component.CustomComponent import style_sheet_setting, Widget, Label, get_time, window_center
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.number import AIR_LEAK_UNIT_COUNT
from process_package.resource.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, COMPORT_FIXED_HEIGHT, \
    AIR_LEAK_RESULT_FONT_SIZE
from process_package.resource.string import STR_MACHINE_COMPORT, STR_RESET, STR_CHANGE, STR_UNIT, STR_RESULT, \
    STR_ORDER_NUMBER, STR_OK, STR_NG, STR_AIR
from process_package.tools.Config import get_order_number
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL

AIR_LEAK_VERSION = 'v1.30'


class AirLeakQR(QApplication):
    def __init__(self, sys_argv):
        super(AirLeakQR, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._view = AirLeakQRView()
        self._view.order.setText(get_order_number())
        self._view.comport.set_available_ports(get_serial_available_list())
        self._view.comport.begin()
        self._view.setWindowTitle(f"Air Leak {AIR_LEAK_VERSION}")
        self._view.show()
        window_center(self._view)

        self.update_db = UpdateDB()


class AirLeakQRView(Widget):
    def __init__(self):
        super(AirLeakQRView, self).__init__()

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(option_layout := QHBoxLayout())
        option_layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        option_layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        comport_box.setLayout(comport := SerialComboHBoxLayout())
        comport.serial_output_data.connect(self.receive_serial_data)
        layout.addLayout(channel_layout := QHBoxLayout())
        channel_layout.addWidget(left_air_leak := AirLeakChannel("LEFT"))
        channel_layout.addWidget(right_air_leak := AirLeakChannel("RIGHT"))

        order.setFixedHeight(COMPORT_FIXED_HEIGHT)
        comport_box.setFixedHeight(COMPORT_FIXED_HEIGHT)
        left_air_leak.qr_enable.emit(True)
        right_air_leak.qr_enable.emit(False)

        self.order = order
        self.comport = comport
        self.left_air_leak = left_air_leak
        self.right_air_leak = right_air_leak

        self.keyboard_listener = LineReadKeyboard()
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

        self.left_qr_enable = True

    def receive_serial_data(self, value):
        if self.left_qr_enable:
            self.right_air_leak.receive_serial.emit(value)
        else:
            self.left_air_leak.receive_serial.emit(value)

    def input_keyboard_line(self, value):
        if STR_CHANGE in value:
            self.left_qr_enable = False if self.left_qr_enable else True
            self.left_air_leak.qr_enable.emit(self.left_qr_enable)
            self.right_air_leak.qr_enable.emit(not self.left_qr_enable)
            return

        if self.left_qr_enable:
            self.left_air_leak.receive_keyboard.emit(value)
        else:
            self.right_air_leak.receive_keyboard.emit(value)

    def contextMenuEvent(self, e):

        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == order_action:
            OrderNumberDialog(self.order)
        elif action == db_action:
            MSSqlDialog()


class AirLeakChannel(QGroupBox):
    qr_enable = Signal(bool)
    receive_serial = Signal(str)
    receive_keyboard = Signal(str)

    def __init__(self, channel):
        super(AirLeakChannel, self).__init__()

        # UI
        self.setTitle(channel)
        layout = QGridLayout(self)
        layout.addWidget(unit_label := Label(STR_UNIT), 0, 0)
        layout.addWidget(result_label := Label(STR_RESULT), 0, 1)
        self.units = [Label(font_size=AIR_LEAK_UNIT_FONT_SIZE) for _ in range(AIR_LEAK_UNIT_COUNT)]
        for index, unit in enumerate(self.units):
            layout.addWidget(unit, index + 1, 0)
        layout.addWidget(result := Label(font_size=AIR_LEAK_RESULT_FONT_SIZE), 1, 1, AIR_LEAK_UNIT_COUNT + 1, 1)

        unit_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
        result_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)

        self.unit_label = unit_label
        self.result_label = result_label
        self.result = result

        self.qr_enable.connect(self.received_change)
        self.receive_serial.connect(self.received_serial)
        self.receive_keyboard.connect(self.received_keyboard)

        self._mssql = MSSQL(STR_AIR)

    def received_change(self, value):
        if value:
            self.unit_label.set_background_color(LIGHT_SKY_BLUE)
            self.result_label.set_background_color()
        else:
            self.unit_label.set_background_color()
            self.result_label.set_background_color(LIGHT_SKY_BLUE)

    def received_serial(self, value):
        self.result.setText(STR_OK if STR_OK in value else STR_NG)
        self._mssql.start_query_thread(
            self._mssql.insert_pprd_with_data_matrixs,
            [unit.text() for unit in self.units if unit.text()],
            get_time(),
            self.result.text(),
            STR_AIR,
            '',
            socket.gethostbyname(socket.gethostname())
        )
        self.clean_units()

    def received_keyboard(self, value):
        if STR_RESET in value:
            self.clean_units()
            return

        if data_matrix := check_dm(value):
            for unit in self.units:
                if unit.text() == data_matrix:
                    break
                if not unit.text():
                    unit.setText(data_matrix)
                    self._mssql.start_query_thread(
                        self._mssql.insert_pprh,
                        data_matrix,
                        get_order_number(),
                        get_time()
                    )
                    break

    def clean_units(self):
        for unit in self.units:
            unit.clean()


if __name__ == '__main__':
    app = AirLeakQR(sys.argv)
    sys.exit(app.exec_())
