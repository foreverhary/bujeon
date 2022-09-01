import sys

from PySide2.QtWidgets import QApplication

from qr_nfc_write.control.QRNFCWriterControl import QRNFCWriterControl
from qr_nfc_write.model.QRNFCWriterModel import QRNFCWriterModel
from qr_nfc_write.view.QRNFCWriterView import QRNFCWriterView

QR_MATCHING_VERSION = 'v1.35'


class QRNFCWriter(QApplication):
    def __init__(self, sys_argv):
        super(QRNFCWriter, self).__init__(sys_argv)
        self._model = QRNFCWriterModel()
        self._control = QRNFCWriterControl(self._model)
        self._view = QRNFCWriterView(self)
        self._view.setWindowTitle(f"QR Matching {QR_MATCHING_VERSION}")
        self._view.load_nfc()


if __name__ == '__main__':
    app = QRNFCWriter(sys.argv)
    sys.exit(app.exec_())
