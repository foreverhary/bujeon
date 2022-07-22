from PySide2.QtCore import Qt
from PySide2.QtWidgets import QHBoxLayout, QMenu

from mic.component.MICNFCReader import MICNFCReader
from mic.component.MICNFCWriter import MICNFCWriter
from mic.component.MICNFConfig import MICNFCConfig
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import Widget
from process_package.resource.string import STR_NFC1, STR_NFCIN, STR_NFC2, STR_MIC, STR_NFCIN1


class MICNFCView(Widget):
    def __init__(self, control):
        super(MICNFCView, self).__init__()
        self._control = control
        layout = QHBoxLayout(self)
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

    def set_nfcs(self, nfcs):
        for port, nfc_name in nfcs.items():
            if nfc_name == STR_NFC1:
                self.nfc1.set_port(port)
            elif nfc_name == STR_NFC2:
                self.nfc2.set_port(port)
            elif nfc_name == STR_NFCIN1:
                self.nfcin.set_port(port)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        mic_action = menu.addAction('MIC File Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == mic_action:
            MICNFCConfig(self._control)
        elif action == db_action:
            MSSqlDialog()
