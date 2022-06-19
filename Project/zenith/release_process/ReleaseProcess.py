import sys

from PySide2.QtWidgets import QApplication

from process_package.Views.CustomComponent import style_sheet_setting
from release_process.control.ReleaseProcessControl import ReleaseProcessControl
from release_process.model.ReleaseProcessModel import ReleaseProcessModel
from release_process.view.ReleaseProcessView import ReleaseProcessView


class ReleaseProcess(QApplication):
    def __init__(self, sys_argv):
        super(ReleaseProcess, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._model = ReleaseProcessModel()
        self._control = ReleaseProcessControl(self._model)
        self._view = ReleaseProcessView(self._model, self._control)
        self._view.show()

if __name__ == '__main__':
    app = ReleaseProcess(sys.argv)
    sys.exit(app.exec_())
