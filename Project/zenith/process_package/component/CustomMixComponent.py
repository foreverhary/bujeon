import socket
from threading import Thread

from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox

from process_package.component.CustomComponent import Label, Button, LabelTimerClean, LabelBlink, LabelNFC
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.resource.color import RED, LIGHT_SKY_BLUE
from process_package.resource.size import DEFAULT_FONT_SIZE
from process_package.resource.string import STR_NG
from process_package.tools.mssql_connect import MSSQL


class SerialComportGroupBox(QGroupBox):
    def __init__(self, *argv, **kwargs):
        super(SerialComportGroupBox, self).__init__()
        self.setTitle(kwargs.pop('title'))
        self.setLayout(comport := SerialComboHBoxLayout(*argv, **kwargs))
        self.comport = comport


class GroupLabelNumber(QGroupBox):
    def __init__(self, title='', count=1, font_size=DEFAULT_FONT_SIZE):
        super(GroupLabelNumber, self).__init__()
        self.setTitle(title)
        layout = QHBoxLayout(self)
        self.labels = [Label(font_size=font_size) for _ in range(count)]
        for label in self.labels:
            layout.addWidget(label)

    def clean(self):
        for label in self.labels:
            label.clean()

    def setText(self, value):
        if not value:
            for label in self.labels:
                label.clean()
        color = RED if len(value) < len(self.labels) else LIGHT_SKY_BLUE
        for text, label in zip(value, self.labels):
            if STR_NG in text:
                color = RED
            label.setText(text)
        [label.set_background_color(color) for label in self.labels]
        self.setStyleSheet(f'background-color: {color}')


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

    def set_font_size(self, value):
        self.label.set_font_size(value)

    def set_background_color(self, value):
        self.label.set_background_color(value)

    def setText(self, value):
        self.label.setText(value)

    def clean(self):
        self.label.clean()

    def clear(self):
        self.label.clear()


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


class NetworkStatusGroupLabel(GroupLabel):
    network_label_color_changed = Signal(str)

    def __init__(self, *args, **kwargs):
        super(NetworkStatusGroupLabel, self).__init__(*args, **kwargs)
        Thread(target=self.check_network, args=(RED,), daemon=True).start()
        self.network_label_color_changed.connect(self.label.set_background_color)
        self.fail_count = 0

    def check_network(self, value):
        self.network_label_color_changed.emit(value)
        mssql = MSSQL()
        try:
            mssql.get_mssql_conn()
        except:
            self.fail_count += 1
        else:
            self.fail_count = 0
        finally:
            if self.fail_count >= 3:
                self.fail_count = 3
                Thread(target=self.check_network, args=(RED,), daemon=True).start()
            else:
                Thread(target=self.check_network, args=(LIGHT_SKY_BLUE,), daemon=True).start()

