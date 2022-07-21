from PySide2.QtCore import QObject


class MICNFCModel(QObject):
    def __init__(self):
        super(MICNFCModel, self).__init__()
        self.error_code_nfc1_result = {}
        self.error_code_nfc2_result = {}

    def begin(self):
        pass

