import sys

from PySide2.QtWidgets import QApplication

from process_package.screen.SplashScreen import SplashScreen
from process_package.component.CustomComponent import style_sheet_setting, window_center
from qr_nfc_write.control.QRNFCWriterControl import QRNFCWriterControl
from qr_nfc_write.model.QRNFCWriterModel import QRNFCWriterModel
from qr_nfc_write.view.QRNFCWriterView import QRNFCWriterView


class QRNFCWriter(QApplication):
    def __init__(self, sys_argv):
        super(QRNFCWriter, self).__init__(sys_argv)
        self._model = QRNFCWriterModel()
        self._control = QRNFCWriterControl(self._model)
        self._view = QRNFCWriterView(self._model, self._control)
        self.load_nfc_window = SplashScreen("QR MATCHING")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = QRNFCWriter(sys.argv)
    sys.exit(app.exec_())
