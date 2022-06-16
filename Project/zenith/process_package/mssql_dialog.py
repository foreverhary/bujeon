import sys

from PySide2.QtCore import Qt, Signal
from PySide2.QtWidgets import QApplication

from process_package.models.Config import set_config_mssql, get_config_mssql
from process_package.defined_variable_function import style_sheet_setting, MSSQL_IP, MSSQL_PORT, \
    MSSQL_PASSWORD, MSSQL_DATABASE, MSSQL_ID
from process_package.mssql_dialog_ui import MSSQLDialogUI


class MSSQLDialog(MSSQLDialogUI):
    mssql_change_signal = Signal()

    def __init__(self):
        super(MSSQLDialog, self).__init__()

        # config data
        self.input_config_value()

        # button event connect
        self.saveButton.clicked.connect(self.save_button_clicked)
        self.cancelButton.clicked.connect(self.cancel_button_clicked)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def save_button_clicked(self):
        set_config_mssql(MSSQL_IP, self.ip_line_edit.text())
        set_config_mssql(MSSQL_PORT, self.port_line_edit.text())
        set_config_mssql(MSSQL_ID, self.id_line_edit.text())
        set_config_mssql(MSSQL_PASSWORD, self.password_line_edit.text())
        set_config_mssql(MSSQL_DATABASE, self.database_line_edit.text())
        self.mssql_change_signal.emit()
        self.close()

    def input_config_value(self):
        self.ip_line_edit.setText(get_config_mssql(MSSQL_IP))
        self.port_line_edit.setText(get_config_mssql(MSSQL_PORT))
        self.password_line_edit.setText(get_config_mssql(MSSQL_PASSWORD))
        self.id_line_edit.setText(get_config_mssql(MSSQL_ID))
        self.database_line_edit.setText(get_config_mssql(MSSQL_DATABASE))

    def cancel_button_clicked(self):
        self.close()

    def show_modal(self):
        return super().exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = MSSQLDialog()
    ex.show()
    sys.exit(app.exec_())
