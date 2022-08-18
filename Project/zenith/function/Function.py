import sys

from PySide2.QtWidgets import QApplication

from function.control.FunctionControl import FunctionControl
from function.model.FunctionModel import FunctionModel
from function.view.FunctionView import FunctionView
from process_package.component.CustomComponent import style_sheet_setting, window_right
from process_package.resource.string import STR_FUNCTION
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger

FUNCTION_VERSION = f"{STR_FUNCTION} v1.33"


class Function(QApplication):
    def __init__(self, sys_argv):
        super(Function, self).__init__(sys_argv)
        self._model = FunctionModel()
        self._control = FunctionControl(self._model)
        self._view = FunctionView(self._model, self._control)
        self._view.setWindowTitle(FUNCTION_VERSION)
        self.load_nfc_window = SplashScreen(STR_FUNCTION)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._view.show()
        self._control.begin()
        window_right(self._view)
        self.load_nfc_window.close()


if __name__ == '__main__':
    logger.debug('function start')
    app = Function(sys.argv)
    sys.exit(app.exec_())
