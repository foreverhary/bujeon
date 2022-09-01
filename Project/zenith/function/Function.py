import sys

from PySide2.QtWidgets import QApplication

from function.control.FunctionControl import FunctionControl
from function.model.FunctionModel import FunctionModel
from function.view.FunctionView import FunctionView
from process_package.resource.string import STR_FUNCTION
from process_package.tools.CommonFunction import logger

FUNCTION_VERSION = f"{STR_FUNCTION} v1.35"


class Function(QApplication):
    def __init__(self, sys_argv):
        super(Function, self).__init__(sys_argv)
        self._model = FunctionModel()
        self._control = FunctionControl(self._model)
        self._view = FunctionView(self)
        self._view.setWindowTitle(FUNCTION_VERSION)


if __name__ == '__main__':
    logger.debug('function start')
    app = Function(sys.argv)
    sys.exit(app.exec_())
