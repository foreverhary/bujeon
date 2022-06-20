from PySide2.QtWidgets import QDialog, QGridLayout, QGroupBox, QVBoxLayout


class NFCCheckerDialog(QDialog):
    def __init__(self, nfc_list):
        super(NFCCheckerDialog, self).__init__()
        layout = QGridLayout(self)


class NFCBox(QGroupBox):
    def __init__(self, name):
        self.setLayout(layout := QVBoxLayout())
        layout.

