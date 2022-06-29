from PySide2.QtCore import QObject, Signal

from process_package.resource.color import LIGHT_SKY_BLUE, RED


class NFCModel(QObject):
    nfc_connection_changed = Signal(str)
    nfc_changed = Signal(str)

    @property
    def nfc_connection(self):
        return self._nfc_connection

    @nfc_connection.setter
    def nfc_connection(self, value):
        self.nfc_connection_changed.emit(LIGHT_SKY_BLUE if value else RED)
