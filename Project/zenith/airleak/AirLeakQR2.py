import sys

from PySide2.QtWidgets import QApplication, QVBoxLayout, QMenu, QHBoxLayout, QGroupBox

from airleak.AirLeakQR import AirLeakChannel
from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.check_string import check_dm
from process_package.component.CustomComponent import style_sheet_setting, window_center, Widget, get_time
from process_package.component.CustomMixComponent import GroupLabel, SerialComportGroupBox, NetworkStatusGroupLabel
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.string import STR_ORDER_NUMBER, MACHINE_COMPORT, STR_MACHINE_COMPORT, STR_SCANNER_COMPORT, \
    STR_RESET, STR_NETWORK
from process_package.tools.Config import get_order_number
from process_package.tools.db_update_from_file import UpdateDB

AIR_LEAK_QR_2_VERSION = "Air Leak QR 2 v1.1"


class AirLeakQR2(QApplication):
    def __init__(self, sys_argv):
        super(AirLeakQR2, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._view = AirLeakQR2View()
        self._view.order.setText(get_order_number())
        self._view.setWindowTitle(AIR_LEAK_QR_2_VERSION)
        self._view.show()
        window_center(self._view)

        self.update_db = UpdateDB()


class AirLeakQR2View(Widget):
    def __init__(self):
        super(AirLeakQR2View, self).__init__()

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(order_network_status_layout := QHBoxLayout())
        order_network_status_layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        order_network_status_layout.addWidget(NetworkStatusGroupLabel(title=STR_NETWORK))
        layout.addLayout(channel_layout := QHBoxLayout())
        channel_layout.addWidget(left_air_leak := AirLeakQRChannel(1))
        channel_layout.addWidget(right_air_leak := AirLeakQRChannel(2))

        order.setMaximumHeight(70)

        self.order = order
        self.left_air_leak = left_air_leak
        self.right_air_leak = right_air_leak

    def contextMenuEvent(self, e):

        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == order_action:
            OrderNumberDialog(self.order)
        elif action == db_action:
            MSSqlDialog()


class AirLeakQRChannel(QGroupBox):
    def __init__(self, channel):
        super(AirLeakQRChannel, self).__init__()
        # UI
        self.setTitle('LEFT' if channel == 1 else 'RIGHT')
        layout = QVBoxLayout(self)
        layout.addWidget(machine_port := SerialComportGroupBox(title=STR_MACHINE_COMPORT,
                                                               port_cfg=f'{MACHINE_COMPORT}{channel}'))
        layout.addWidget(scanner_port := SerialComportGroupBox(title=STR_SCANNER_COMPORT,
                                                               port_cfg=f'{MACHINE_COMPORT}{channel + 2}'))
        layout.addWidget(air_leak_channel := AirLeak2Channel(''))

        machine_port.setMaximumHeight(70)
        scanner_port.setMaximumHeight(70)

        self.machine_port = machine_port.comport
        self.scanner_port = scanner_port.comport
        self.air_leak_channel = air_leak_channel
        self.set_start_comport()

        self.machine_port.serial_output_data.connect(self.air_leak_channel.receive_serial.emit)
        self.scanner_port.serial_output_data.connect(self.air_leak_channel.receive_keyboard.emit)

    def set_start_comport(self):
        self.machine_port.set_available_ports(get_serial_available_list())
        self.scanner_port.set_available_ports(get_serial_available_list())
        self.machine_port.begin()
        self.scanner_port.begin()


class AirLeak2Channel(AirLeakChannel):

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
                    if self.result.text():
                        self.result.clean()
                    break


if __name__ == '__main__':
    app = AirLeakQR2(sys.argv)
    sys.exit(app.exec_())
