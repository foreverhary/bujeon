import socket
import sys
from threading import Timer

from PySide2.QtCore import Signal, QTimer
from PySide2.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.check_string import check_dm
from process_package.component.CustomComponent import style_sheet_setting, Widget, Label, get_time, window_center
from process_package.component.CustomMixComponent import GroupLabel, SerialComportGroupBox, NetworkStatusGroupLabel
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.number import AIR_LEAK_UNIT_COUNT
from process_package.resource.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, COMPORT_FIXED_HEIGHT, \
    AIR_LEAK_RESULT_FONT_SIZE
from process_package.resource.string import STR_MACHINE_COMPORT, STR_RESET, STR_CHANGE, STR_UNIT, STR_RESULT, \
    STR_ORDER_NUMBER, STR_OK, STR_NG, STR_AIR, STR_NETWORK, CHANNEL, AIR_LEAK_SECTION
from process_package.tools.Config import get_order_number, get_config_value, set_config_value
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL

AIR_LEAK_VERSION = 'v1.32'


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
        option_layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        option_layout.addWidget(network := NetworkStatusGroupLabel(title=STR_NETWORK))
        layout.addWidget(comport := SerialComportGroupBox(title=STR_MACHINE_COMPORT))
        comport.comport.serial_output_data.connect(self.receive_serial_data)
        layout.addLayout(channel_layout := QHBoxLayout())
        channel_layout.addWidget(left_air_leak := AirLeakChannel("CH 1"))
        channel_layout.addWidget(right_air_leak := AirLeakChannel("CH 2"))

        order.setFixedHeight(COMPORT_FIXED_HEIGHT)
        network.setFixedHeight(COMPORT_FIXED_HEIGHT)
        comport.setFixedHeight(COMPORT_FIXED_HEIGHT)
        left_air_leak.qr_enable.emit(True)
        right_air_leak.qr_enable.emit(False)

        self.order = order
        self.comport = comport.comport
        self.left_air_leak = left_air_leak
        self.right_air_leak = right_air_leak

        self.left_air_leak.dm_full.connect(self.receive_dm_full)
        self.right_air_leak.dm_full.connect(self.receive_dm_full)

        self.keyboard_listener = LineReadKeyboard()
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

        self.left_qr_enable = True
        self.channel_count = self.channel_count

    def receive_dm_full(self, value):
        if value:
            self.change_channel()

    def receive_serial_data(self, value):
        if self.channel_count == 2 and not self.left_qr_enable:
            self.right_air_leak.receive_serial.emit(value)
        else:
            self.left_air_leak.receive_serial.emit(value)

    def input_keyboard_line(self, value):
        if STR_CHANGE in value and self.channel_count == 2:
            self.change_channel()
            return

        if self.channel_count == 2 and not self.left_qr_enable:
            if self.is_allowed_unit4(self.right_air_leak, self.left_air_leak):
                self.right_air_leak.receive_keyboard.emit(value)
        else:
            if self.is_allowed_unit4(self.left_air_leak, self.right_air_leak):
                self.left_air_leak.receive_keyboard.emit(value)

    def is_allowed_unit4(self, enabled_slot, disabled_slot):
        return not (self.check_unit_count(enabled_slot) == 3 and self.check_unit_count(disabled_slot))

    def check_unit_count(self, slot):
        count = 0
        for unit in slot.units:
            if not unit.text():
                break
            count += 1
        return count

    def change_channel(self):
        self.left_qr_enable = False if self.left_qr_enable else True
        self.left_air_leak.qr_enable.emit(self.left_qr_enable)
        self.right_air_leak.qr_enable.emit(not self.left_qr_enable)

    def contextMenuEvent(self, e):

        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')
        use_one_slot = menu.addAction('USE 1 Slot')
        use_two_slot = menu.addAction('USE 2 Slots')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == order_action:
            OrderNumberDialog(self.order)
        elif action == db_action:
            MSSqlDialog()
        elif action == use_one_slot:
            self.channel_count = 1
        elif action == use_two_slot:
            self.channel_count = 2

    @property
    def channel_count(self):
        if not (get_config_value(AIR_LEAK_SECTION, CHANNEL)):
            set_config_value(AIR_LEAK_SECTION, CHANNEL, '2')
        return int(get_config_value(AIR_LEAK_SECTION, CHANNEL))

    @channel_count.setter
    def channel_count(self, value):
        set_config_value(AIR_LEAK_SECTION, CHANNEL, str(value))

        if value == 1:
            self.right_air_leak.setHidden(True)
            self.left_air_leak.unit_label.set_background_color()
            self.left_air_leak.result_label.set_background_color()
        else:
            self.right_air_leak.setHidden(False)
            self.left_qr_enable = False
            self.change_channel()

        self.left_air_leak.clean_units()
        self.left_air_leak.result.clean()
        self.right_air_leak.clean_units()
        self.right_air_leak.result.clean()


class AirLeakChannel(QGroupBox):
    qr_enable = Signal(bool)
    dm_full = Signal(bool)
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
        unit_label.setMaximumHeight(50)
        result_label.setMaximumHeight(50)

        self.unit_label = unit_label
        self.result_label = result_label
        self.result = result

        self.qr_enable.connect(self.received_change)
        self.receive_serial.connect(self.received_serial)
        self.receive_keyboard.connect(self.received_keyboard)

        self._mssql = MSSQL(STR_AIR)

        self.timer_result_clean = QTimer(self)
        self.timer_result_clean.timeout.connect(self.result.clean)

    def received_change(self, value):
        if value:
            self.unit_label.set_background_color(LIGHT_SKY_BLUE)
            self.result_label.set_background_color()
            self.result.clean()
        else:
            self.unit_label.set_background_color()
            self.result_label.set_background_color(LIGHT_SKY_BLUE)

    def received_serial(self, value):
        if not value:
            return

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
        self.timer_result_clean.stop()
        if STR_OK in value:
            self.timer_result_clean.start(4000)
            self.clean_units()

    def received_keyboard(self, value):
        if STR_RESET in value:
            self.clean_units()
            self.result.clean()
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
                    self.dm_full.emit(self.is_dm_full())
                    break

    def is_dm_full(self):
        for unit in self.units:
            if not unit.text():
                return False
        else:
            return True

    def clean_units(self):
        for unit in self.units:
            unit.clean()


if __name__ == '__main__':
    app = AirLeakQR(sys.argv)
    sys.exit(app.exec_())
