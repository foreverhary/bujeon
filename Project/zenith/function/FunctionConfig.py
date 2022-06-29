import sys

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QApplication

from function.control.FunctionConfigControl import FunctionConfigControl
from function.model.FunctionConfigModel import FunctionConfigModel
from function.view.FunctionConfigView import FunctionConfigView
from process_package.component.CustomComponent import style_sheet_setting


class FunctionConfig(QObject):
    def __init__(self, parent_model, parent_control):
        super(FunctionConfig, self).__init__()
        self._parent_model = parent_model
        self._parent_control = parent_control
        self._model = FunctionConfigModel()
        self._control = FunctionConfigControl(self._model)
        self._view = FunctionConfigView(self._model, self._control, self._parent_control)
        self._model.begin_config_read()
        self._view.showModal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = FunctionConfig(FunctionConfigModel())
    sys.exit(app.exec_())
