import sys

from PySide2.QtCore import QObject
from PySide2.QtWidgets import QApplication

from process_package.component.CustomComponent import style_sheet_setting
from process_package.Views.MSSqlDialogView import MSSqlDialogView
from process_package.controllers.MSSqlDialogControl import MSSqlDialogControl
from process_package.models.MSSqlDialogModel import MSSqlDialogModel


class MSSqlDialog(QObject):
    def __init__(self):
        super(MSSqlDialog, self).__init__()
        self._model = MSSqlDialogModel()
        self._control = MSSqlDialogControl(self._model)
        self._view = MSSqlDialogView(self._model, self._control)
        self._model.read_mssql_config()
        self._view.showModal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = MSSqlDialog()
    ex.showModal()
    sys.exit(app.exec_())
