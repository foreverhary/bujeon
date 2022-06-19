import sys

from PySide2.QtWidgets import QApplication

from airleak.AirLeakManual.control.AirLeakControl import AirLeakControl
from airleak.AirLeakManual.model.AirLeakModel import AirLeakModel
from airleak.AirLeakManual.view.AirLeakView import AirLeakView
from process_package.screen.SplashScreen import SplashScreen
from process_package.Views.CustomComponent import style_sheet_setting, window_center
from process_package.resource.string import STR_AIR_LEAK


class AirLeak(QApplication):
    def __init__(self, sys_argv):
        super(AirLeak, self).__init__(sys_argv)
        self._model = AirLeakModel()
        self._control = AirLeakControl(self._model)
        self._view = AirLeakView(self._model, self._control)
        self._model.begin_config_read()
        self.load_nfc_window = SplashScreen(STR_AIR_LEAK)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        self._control.begin()
        window_center(self._view)


if __name__ == '__main__':
    app = AirLeak(sys.argv)
    sys.exit(app.exec_())
