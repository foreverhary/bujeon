import sys

from PySide2.QtWidgets import QApplication

from airleak.control.AirLeakAutomationControl import AirLeakAutomationControl
from airleak.model.AirLeakAutomationModel import AirLeakAutomationModel
from airleak.view.AirLeakAutomationView import AirLeakAutomationView
from process_package.component.CustomComponent import style_sheet_setting, window_center
from process_package.resource.string import STR_AIR_LEAK
from process_package.screen.SplashScreen import SplashScreen


class AirLeakAutomation(QApplication):
    def __init__(self, sys_argv):
        super(AirLeakAutomation, self).__init__(sys_argv)
        self._model = AirLeakAutomationModel()
        self._control = AirLeakAutomationControl(self._model)
        self._view = AirLeakAutomationView(self._model, self._control)
        self.load_nfc_window = SplashScreen(STR_AIR_LEAK)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        self._control.begin()
        window_center(self._view)
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = AirLeakAutomation(sys.argv)
    sys.exit(app.exec_())
