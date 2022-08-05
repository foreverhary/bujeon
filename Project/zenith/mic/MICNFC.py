import sys

from PySide2.QtWidgets import QApplication

from control.MICNFCControl import MICNFCControl
from view.MICNFCView import MICNFCView
from process_package.component.CustomComponent import style_sheet_setting, window_center
from process_package.screen.SplashScreen import SplashScreen

MIC_VERSION = "MIC v1.30"


class MICNFC(QApplication):
    def __init__(self, sys_argv):
        super(MICNFC, self).__init__(sys_argv)
        self._control = MICNFCControl()
        self._view = MICNFCView(self._control)
        self._view.setWindowTitle(MIC_VERSION)
        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = MICNFC(sys.argv)
    sys.exit(app.exec_())
