import sys

from PySide2.QtWidgets import QApplication

from touch.control.TouchControl import TouchControl
from touch.model.TouchModel import TouchModel
from touch.view.TouchView import TouchView
from process_package.Views.CustomComponent import style_sheet_setting
from process_package.tools.CommonFunction import logger


class Touch(QApplication):
    def __init__(self, sys_argv):
        super(Touch, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._model = TouchModel()
        self._control = TouchControl(self._model)
        self._view = TouchView(self._model, self._control)
        self._model.begin_config_read()
        self._control.begin()
        self._view.show()


if __name__ == '__main__':
    logger.info("start touch process")
    app = Touch(sys.argv)
    sys.exit(app.exec_())
