from PySide2.QtCore import QObject, Signal


class NFCModel(QObject):
    nfc_changed = Signal(str)
