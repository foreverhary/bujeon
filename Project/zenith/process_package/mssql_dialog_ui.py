from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGridLayout, QHBoxLayout

from process_package.PyQtCustomComponent import LeftAlignLabel, LineEdit, Button


class MSSQLDialogUI(QDialog):
    def __init__(self):
        super(MSSQLDialogUI, self).__init__()
        self.setWindowTitle('Server Setting')

        layout = QVBoxLayout()

        ip_label = LeftAlignLabel("IP")
        port_label = LeftAlignLabel("PORT")
        id_label = LeftAlignLabel("ID")
        password_label = LeftAlignLabel("PASSWORD")
        database_label = LeftAlignLabel("DATABASE")

        self.ip_line_edit = LineEdit()
        self.port_line_edit = LineEdit()
        self.id_line_edit = LineEdit()
        self.password_line_edit = LineEdit()
        self.password_line_edit.setEchoMode(LineEdit.Password)
        self.database_line_edit = LineEdit()

        grid_layout = QGridLayout()
        grid_layout.addWidget(ip_label, 0, 0)
        grid_layout.addWidget(port_label, 1, 0)
        grid_layout.addWidget(id_label, 2, 0)
        grid_layout.addWidget(password_label, 3, 0)
        grid_layout.addWidget(database_label, 4, 0)

        grid_layout.addWidget(self.ip_line_edit, 0, 1)
        grid_layout.addWidget(self.port_line_edit, 1, 1)
        grid_layout.addWidget(self.id_line_edit, 2, 1)
        grid_layout.addWidget(self.password_line_edit, 3, 1)
        grid_layout.addWidget(self.database_line_edit, 4, 1)

        button_layout = QHBoxLayout()
        self.saveButton = Button('SAVE')
        self.saveButton.setMinimumWidth(150)
        self.cancelButton = Button('CANCEL')
        self.cancelButton.setMinimumWidth(150)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.cancelButton)

        layout.addLayout(grid_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)
