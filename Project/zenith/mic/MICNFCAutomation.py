import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QMenu

from MICNFC import MICNFCControl
from component.MICNFCAutoEach import MICNFCAutoEach
from component.MICNFConfig import MICNFCConfig
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget, window_center
from process_package.resource.string import STR_MIC, STR_NFC1, STR_NFC2
from process_package.screen.SplashScreen import SplashScreen


class MICNFCAutomation(QApplication):
    def __init__(self, sys_argv):
        super(MICNFCAutomation, self).__init__(sys_argv)
        self._control = MICNFCControl()
        self._view = MICNFCAutomationView(self)


class MICNFCAutomationView(Widget):
    def __init__(self, app):
        super(MICNFCAutomationView, self).__init__()
        self.app, self._control = app, app._control
        layout = QHBoxLayout(self)
        layout.addWidget(nfc1 := MICNFCAutoEach(STR_NFC1, self._control._mssql))
        layout.addWidget(nfc2 := MICNFCAutoEach(STR_NFC2, self._control._mssql))
        self.nfc1 = nfc1
        self.nfc2 = nfc2

        self._control.nfc1_result_changed.connect(nfc1.set_result)
        self._control.nfc1_error_result_changed.connect(nfc1.set_error_code)

        self._control.nfc2_result_changed.connect(nfc2.set_result)
        self._control.nfc2_error_result_changed.connect(nfc2.set_error_code)

        self.setWindowTitle(f"{STR_MIC} Automation v0.1")

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)
        self.load_nfc()

    def load_nfc(self):
        self.nfc1.nfc.close_force()
        self.nfc2.nfc.close_force()
        self.app.setStyleSheet("QWidget{};")
        self.hide()
        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def set_nfcs(self, nfcs):
        for port, nfc_name in nfcs.items():
            if nfc_name == STR_NFC1:
                self.nfc1.set_port(port)
            elif nfc_name == STR_NFC2:
                self.nfc2.set_port(port)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        mic_action = menu.addAction('MIC File Setting')
        db_action = menu.addAction('DB Setting')
        nfc_action = menu.addAction('Load NFC Port')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == mic_action:
            MICNFCConfig(self._control)
        elif action == db_action:
            MSSqlDialog()
        elif action == nfc_action:
            self.load_nfc()

    def show_main_window(self, nfcs):
        style_sheet_setting(self.app)
        for port, nfc_name in nfcs.items():
            if nfc_name == STR_NFC1:
                self.nfc1.nfc.set_port(port)
            elif nfc_name == STR_NFC2:
                self.nfc2.nfc.set_port(port)

        self.show()

        window_center(self)
        self.load_nfc_window.close()

if __name__ == '__main__':
    app = MICNFCAutomation(sys.argv)
    sys.exit(app.exec_())
