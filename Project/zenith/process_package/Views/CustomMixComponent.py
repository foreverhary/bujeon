from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox

from process_package.Views.CustomComponent import Label, Button
from process_package.resource.size import DEFAULT_FONT_SIZE


class GroupLabel(QGroupBox):
    def __init__(self, title='', font_size=DEFAULT_FONT_SIZE):
        super(GroupLabel, self).__init__()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(label := Label(font_size=font_size))

        self.label = label


class HBoxComboButton(QHBoxLayout):

    def __init__(self, name, button_text='CONNECT'):
        super(HBoxComboButton, self).__init__()
        self.addWidget(comport := QComboBox())
        self.addWidget(button := Button(button_text))

        self.comport = comport
        self.button = button

    def fill_combobox(self, rows):
        self.comport.clear()
        self.comport.addItems(rows)

    def serial_connection(self, connection):
        self.button.set_connect_color(connection)
        self.comport.setEnabled(not connection)

