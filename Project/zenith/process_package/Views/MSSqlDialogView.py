from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout

from process_package.Views.CustomComponent import LeftAlignLabel, LineEdit, Button


class MSSqlDialogView(QDialog):
    def __init__(self, model, control):
        super(MSSqlDialogView, self).__init__()
        self._model = model
        self._control = control

        # UI
        self.setWindowTitle('Server Setting')
        layout = QVBoxLayout(self)

        layout.addLayout(grid_layout := QGridLayout())

        grid_layout.addWidget(LeftAlignLabel("IP"), 0, 0)
        grid_layout.addWidget(LeftAlignLabel("PORT"), 1, 0)
        grid_layout.addWidget(LeftAlignLabel("ID"), 2, 0)
        grid_layout.addWidget(LeftAlignLabel("PASSWORD"), 3, 0)
        grid_layout.addWidget(LeftAlignLabel("DATABASE"), 4, 0)

        grid_layout.addWidget(ip_line_edit := LineEdit(), 0, 1)
        grid_layout.addWidget(port_line_edit := LineEdit(), 1, 1)
        grid_layout.addWidget(id_line_edit := LineEdit(), 2, 1)
        grid_layout.addWidget(password_line_edit := LineEdit(), 3, 1)
        grid_layout.addWidget(database_line_edit := LineEdit(), 4, 1)

        layout.addLayout(button_layout := QHBoxLayout())
        button_layout.addWidget(saveButton := Button('SAVE'))
        button_layout.addWidget(cancelButton := Button('CANCEL'))

        password_line_edit.setEchoMode(LineEdit.Password)

        saveButton.setMinimumWidth(150)
        cancelButton.setMinimumWidth(150)

        self.ip_line_edit = ip_line_edit
        self.port_line_edit = port_line_edit
        self.id_line_edit = id_line_edit
        self.password_line_edit = password_line_edit
        self.database_line_edit = database_line_edit

        self.saveButton = saveButton
        self.cancelButton = cancelButton

        # connect widgets to controller
        self.ip_line_edit.textChanged.connect(self._control.change_ip)
        self.port_line_edit.textChanged.connect(self._control.change_port)
        self.id_line_edit.textChanged.connect(self._control.change_id)
        self.password_line_edit.textChanged.connect(self._control.change_password)
        self.database_line_edit.textChanged.connect(self._control.change_database)

        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)

        # listen for model event signals
        self._model.change_ip.connect(self.ip_line_edit.setText)
        self._model.change_port.connect(self.port_line_edit.setText)
        self._model.change_id.connect(self.id_line_edit.setText)
        self._model.change_password.connect(self.password_line_edit.setText)
        self._model.change_database.connect(self.database_line_edit.setText)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def save(self):
        self._model.save()
        self.close()

    def showModal(self):
        return super().exec_()