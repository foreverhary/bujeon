from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QMenu, QVBoxLayout

from mic.component.MICNFCReader import MICNFCReader
from mic.component.MICNFCWriter import MICNFCWriter
from mic.component.MICNFConfig import MICNFCConfig
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import Widget, style_sheet_setting, window_center
from process_package.component.CustomMixComponent import NetworkStatusGroupLabel
from process_package.resource.string import STR_NFC1, STR_NFCIN, STR_NFC2, STR_NFCIN1, STR_NETWORK
from process_package.screen.SplashScreen import SplashScreen


class MICNFCView(Widget):
    def __init__(self, app):
        super(MICNFCView, self).__init__()
        self.app, self._control = app, app._control
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(NetworkStatusGroupLabel(STR_NETWORK))
        main_layout.addLayout(layout := QHBoxLayout())
        layout.addWidget(nfc1 := MICNFCWriter(STR_NFC1, self._control._mssql))
        layout.addWidget(nfcin := MICNFCReader(STR_NFCIN))
        layout.addWidget(nfc2 := MICNFCWriter(STR_NFC2, self._control._mssql))
        self.nfc1 = nfc1
        self.nfc2 = nfc2
        self.nfcin = nfcin

        self._control.nfc1_result_changed.connect(nfc1.set_result)
        self._control.nfc1_error_result_changed.connect(nfc1.set_error_code)

        self._control.nfc2_result_changed.connect(nfc2.set_result)
        self._control.nfc2_error_result_changed.connect(nfc2.set_error_code)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)

        self.load_nfc()

    def load_nfc(self):
        self.nfcin.close_force()
        self.nfc1.close_force()
        self.nfc2.close_force()
        self.app.setStyleSheet("QWidget{};")
        self.hide()
        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

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
                self.nfc1.set_port(port)
            elif nfc_name == STR_NFC2:
                self.nfc2.set_port(port)
            elif nfc_name == STR_NFCIN1:
                self.nfcin.set_port(port)

        self.show()

        window_center(self)
        self.load_nfc_window.close()