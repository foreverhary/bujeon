from PySide2.QtCore import Signal
from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox

from process_package.Views.CustomComponent import Label, Button, LabelTimerClean, LabelBlink, LabelNFC
from process_package.resource.size import DEFAULT_FONT_SIZE


class GroupLabelNumber(QGroupBox):
    def __init__(self, title='', count=1, font_size=DEFAULT_FONT_SIZE):
        super(GroupLabelNumber, self).__init__()
        self.setTitle(title)
        layout = QHBoxLayout(self)
        self.labels = [GroupLabel(font_size=font_size) for _ in range(count)]
        for label in self.labels:
            layout.addWidget(label)

    def setText(self, value):
        if not value:
            for label in self.labels:
                label.clear()
        for text, label in zip(value, self.labels):
            label.setText(text)


class GroupLabel(QGroupBox):
    def __init__(self, title='', font_size=DEFAULT_FONT_SIZE, blink_time=0, is_clean=False, clean_time=2000,
                 is_nfc=False):
        super(GroupLabel, self).__init__()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        if is_nfc:
            layout.addWidget(label := LabelNFC(font_size=font_size,
                                               is_clean=is_clean,
                                               clean_time=clean_time))
        elif is_clean:
            layout.addWidget(label := LabelTimerClean(font_size=font_size,
                                                      is_clean=is_clean,
                                                      clean_time=clean_time))
        elif blink_time:
            layout.addWidget(label := LabelBlink(font_size=font_size,
                                                 blink_time=blink_time))
        else:
            layout.addWidget(label := Label(font_size=font_size))

        self.label = label

    def setText(self, value):
        self.label.setText(value)


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
