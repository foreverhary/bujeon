import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGridLayout, QGroupBox

from NFC import VirtualNFC
from process_package.PyQtCustomComponent import LineEdit, Button
from process_package.defined_variable_function import style_sheet_setting, window_bottom_left

SLOT = 3
COMPORT = ('com6', 'com8', 'com11')
COLUMN_COUNT = 2


class NFCDemo(QWidget):
    def __init__(self, app):
        super(NFCDemo, self).__init__()
        self.app = app
        self.setLayout(layout := QGridLayout())
        self.nfcs = []
        for index, com in enumerate(COMPORT):
            layout.addWidget(groupbox := NFCSlot(index, com), index // COLUMN_COUNT, index % COLUMN_COUNT)
            self.nfcs.append(groupbox)
        self.show_main_window()

    def show_main_window(self):
        style_sheet_setting(self.app)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

        window_bottom_left(self)


class NFCSlot(QGroupBox):
    def __init__(self, index, com):
        super(NFCSlot, self).__init__()
        self.nfc = VirtualNFC(index, com)
        self.nfc.signal.signal_dtr.connect(self.received_signal_dtr)
        self.nfc.signal.signal_read_msg.connect(self.received_signal_msg)
        if index == 0:
            self.setTitle("NFC IN")
        else:
            self.setTitle(f"NFC {index}")

        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(edit_line := LineEdit())
        layout.addWidget(write_button := Button('WRITE'))

        self.edit_line = edit_line
        self.edit_line.setMinimumWidth(800)
        self.write_button = write_button
        self.write_button.clicked.connect(self.clicked_write_button)

        self.received_signal_dtr()

    def clicked_write_button(self):
        self.nfc.send_msg(self.edit_line.text())

    def received_signal_msg(self, msg):
        self.edit_line.setText(msg)

    def received_signal_dtr(self):
        if self.nfc.dsr:
            self.edit_line.setEnabled(True)
            self.write_button.setEnabled(True)
        else:
            self.edit_line.setDisabled(True)
            self.write_button.setDisabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFCDemo(app)
    sys.exit(app.exec_())
