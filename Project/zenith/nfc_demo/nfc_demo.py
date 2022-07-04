import sys

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QApplication, QVBoxLayout, QGridLayout, QGroupBox

from NFC import VirtualNFC
from process_package.component.CustomComponent import LineEdit, Button, style_sheet_setting, window_bottom_left, Widget

SLOT = 3
COMPORT = ('com5', 'com7', 'com9', 'com11')
# COMPORT = ('com3', 'com5', 'com7')
COLUMN_COUNT = 2


class NFCDemo(Widget):
    def __init__(self, app):
        super(NFCDemo, self).__init__()
        self.app = app
        self.setLayout(layout := QGridLayout())
        self.nfcs = []
        # layout.addWidget(groupbox := NFCSlot(0, COMPORT[0]), 0, 0)
        # self.nfcs.append(groupbox)
        # layout.addWidget(groupbox := NFCSlot(2, COMPORT[2]), 0, 1)
        # self.nfcs.append(groupbox)
        for index, com in enumerate(COMPORT):
            layout.addWidget(groupbox := NFCSlot(index+1, com), index // COLUMN_COUNT, index % COLUMN_COUNT)
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
