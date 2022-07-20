from PySide2.QtCore import QObject
from PySide2.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout

from process_package.component.CustomComponent import LeftAlignLabel, LineEdit, Button
from process_package.resource.string import MSSQL_IP, MSSQL_PORT
from process_package.tools.Config import set_config_mssql, get_config_mssql


class PLCDialog(QObject):
    def __init__(self):
        super(PLCDialog, self).__init__()
        self._view = PLCDialogView()
        self._view.showModal()


class PLCDialogView(QDialog):
    def __init__(self):
        super(PLCDialogView, self).__init__()

        # UI
        self.setWindowTitle('PLC IP Setting')
        layout = QVBoxLayout(self)
        layout.addLayout(grid_layout := QGridLayout())

        grid_layout.addWidget(LeftAlignLabel("IP"), 0, 0)
        grid_layout.addWidget(LeftAlignLabel("PORT"), 1, 0)

        grid_layout.addWidget(ip_line_edit := LineEdit(), 0, 1)
        grid_layout.addWidget(port_line_edit := LineEdit(), 1, 1)

        layout.addLayout(button_layout := QHBoxLayout())
        button_layout.addWidget(saveButton := Button('SAVE'))
        button_layout.addWidget(cancelButton := Button('CANCEL'))

        saveButton.setMinimumWidth(150)
        cancelButton.setMinimumWidth(150)

        self.ip_line_edit = ip_line_edit
        self.port_line_edit = port_line_edit
        self.saveButton = saveButton
        self.cancelButton = cancelButton

        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)

        self.read_config()

    def read_config(self):
        self.ip_line_edit.setText(get_config_mssql(MSSQL_IP))
        self.port_line_edit.setText(get_config_mssql(MSSQL_PORT))

    def save(self):
        set_config_mssql(MSSQL_IP, self.ip_line_edit.text())
        set_config_mssql(MSSQL_PORT, self.port_line_edit.text())
        self.close()

    def showModal(self):
        return super().exec_()
