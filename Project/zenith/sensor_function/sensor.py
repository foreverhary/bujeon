import sys

from PySide2.QtCore import QObject, Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget, window_center
from process_package.component.CustomMixComponent import NetworkStatusGroupLabel
from process_package.resource.string import STR_NFC1, STR_NFC2, STR_SEN, STR_NETWORK
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL
from SensorChannel import SensorChannel

SENSOR_VERSION = 'IR SENSOR v1.34'


class SensorProcess(QApplication):
    def __init__(self, sys_argv):
        super(SensorProcess, self).__init__(sys_argv)
        self._control = SensorProcessControl()
        self._view = SensorProcessView(self)


class SensorProcessControl(QObject):

    def __init__(self):
        super(SensorProcessControl, self).__init__()
        self._mssql = MSSQL(STR_SEN)

        self.process_name = STR_SEN

        self.ng_screen_opened = False
        self.update_db = UpdateDB()


class SensorProcessView(Widget):
    def __init__(self, app):
        super(SensorProcessView, self).__init__()
        self.app, self._control = app, app._control
        layout = QVBoxLayout(self)

        layout.addWidget(NetworkStatusGroupLabel(STR_NETWORK))
        layout.addLayout(process_layout := QHBoxLayout())
        process_layout.addWidget(channel1 := SensorChannel(1))
        process_layout.addWidget(channel2 := SensorChannel(2))

        # size
        self.channel1 = channel1
        self.channel2 = channel2

        # component connect
        # self.nfcin.nfc_data_out.connect(self._control.check_previous)

        # listen for model event signals

        self.setWindowTitle(SENSOR_VERSION)
        self.setMinimumWidth(640)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)
        self.load_nfc()

    def load_nfc(self):
        self.channel1.nfc.close_force()
        self.channel2.nfc.close_force()
        self.channel1.comport.serial.close()
        self.channel2.comport.serial.close()
        self.app.setStyleSheet("QWidget{};")
        self.hide()
        self.load_nfc_window = SplashScreen("Sensor Process")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self.app)
        nfc_ports = []
        for port, nfc_name in nfcs.items():
            if nfc_name == STR_NFC1:
                self.channel1.set_port(port)
                nfc_ports.append(port)
            elif nfc_name == STR_NFC2:
                self.channel2.set_port(port)
                nfc_ports.append(port)
        self.channel1.exclude_nfc_ports(nfc_ports)
        self.channel2.exclude_nfc_ports(nfc_ports)
        self.show()

        window_center(self)
        self.load_nfc_window.close()
        self.begin()

    def begin(self):
        self.channel1.begin()
        self.channel2.begin()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        nfc_action = menu.addAction('Load NFC Port')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()
        elif action == nfc_action:
            self.load_nfc()


if __name__ == '__main__':
    app = SensorProcess(sys.argv)
    sys.exit(app.exec_())
