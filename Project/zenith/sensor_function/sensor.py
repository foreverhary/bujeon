import sys

from PySide2.QtCore import QObject, Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget
from process_package.component.CustomMixComponent import NetworkStatusGroupLabel
from process_package.resource.string import STR_NFC1, STR_NFC2, STR_SEN, STR_NETWORK
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL
from SensorChannel import SensorChannel

SENSOR_VERSION = 'IR SENSOR v1.33'


class SensorProcess(QApplication):
    def __init__(self, sys_argv):
        super(SensorProcess, self).__init__(sys_argv)
        self._control = SensorProcessControl()
        self._view = SensorProcessView(self._control)
        self.load_nfc_window = SplashScreen("Sensor Process")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._view.begin()
        self._view.show()
        self.load_nfc_window.close()


class SensorProcessControl(QObject):

    def __init__(self):
        super(SensorProcessControl, self).__init__()
        self._mssql = MSSQL(STR_SEN)

        self.process_name = STR_SEN

        self.ng_screen_opened = False
        self.update_db = UpdateDB()


class SensorProcessView(Widget):
    def __init__(self, control):
        super(SensorProcessView, self).__init__()
        self._control = control
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

    def set_nfcs(self, nfcs):
        nfc_ports = []
        for port, nfc_name in nfcs.items():
            # if STR_NFCIN in nfc_name:
            #     nfc_ports.append(port)
            #     self.nfcin.set_port(port)
            if nfc_name == STR_NFC1:
                self.channel1.set_port(port)
                nfc_ports.append(port)
            elif nfc_name == STR_NFC2:
                self.channel2.set_port(port)
                nfc_ports.append(port)
        self.channel1.exclude_nfc_ports(nfc_ports)
        self.channel2.exclude_nfc_ports(nfc_ports)

    def begin(self):
        self.channel1.begin()
        self.channel2.begin()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()


if __name__ == '__main__':
    app = SensorProcess(sys.argv)
    sys.exit(app.exec_())
