import sys

from PySide2.QtWidgets import QApplication

from audio_bus.control.FunctionControl import FunctionControl
from audio_bus.model.FunctionModel import FunctionModel
from audio_bus.view.FunctionView import FunctionView
from process_package.screen.SplashScreen import SplashScreen
from process_package.Views.CustomComponent import style_sheet_setting, window_center
from process_package.resource.string import STR_AIR_LEAK


class Function(QApplication):
    def __init__(self, sys_argv):
        super(Function, self).__init__(sys_argv)
        self._model = FunctionModel()
        self._control = FunctionControl(self._model)
        self._view = FunctionView(self._model, self._control)
        self._model.begin_config_read()
        self.load_nfc_window = SplashScreen(STR_AIR_LEAK)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._view.show()
        self._control.begin()
        window_center(self._view)


if __name__ == '__main__':
    app = Function(sys.argv)
    sys.exit(app.exec_())
