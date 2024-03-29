import sys

from PySide2.QtWidgets import QApplication

from control.TouchControl import TouchControl
from model.TouchModel import TouchModel
from process_package.resource.string import STR_TOUCH_PROCESS
from view.TouchView import TouchView
from process_package.component.CustomComponent import style_sheet_setting
from process_package.tools.CommonFunction import logger


TOUCH_VERSION = f"{STR_TOUCH_PROCESS} v1.33"


class Touch(QApplication):
    def __init__(self, sys_argv):
        super(Touch, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._model = TouchModel()
        self._control = TouchControl(self._model)
        self._view = TouchView(self._model, self._control)
        self._view.setWindowTitle(TOUCH_VERSION)
        self._view.show()


if __name__ == '__main__':
    logger.debug("start touch process")
    app = Touch(sys.argv)
    sys.exit(app.exec_())
