import sys

from PySide2.QtWidgets import QApplication

from process_package.Views.CustomComponent import style_sheet_setting, window_center
from control.ReleaseProcessControl import ReleaseProcessControl
from model.ReleaseProcessModel import ReleaseProcessModel
from process_package.resource.string import STR_RELEASE
from process_package.screen.SplashScreen import SplashScreen
from view.ReleaseProcessView import ReleaseProcessView


class ReleaseProcess(QApplication):
    def __init__(self, sys_argv):
        super(ReleaseProcess, self).__init__(sys_argv)
        self._model = ReleaseProcessModel()
        self._control = ReleaseProcessControl(self._model)
        self._view = ReleaseProcessView(self._model, self._control)
        self.load_nfc_window = SplashScreen(STR_RELEASE)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._view.show()
        window_center(self._view)

if __name__ == '__main__':
    app = ReleaseProcess(sys.argv)
    sys.exit(app.exec_())
