from threading import Thread

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox

from process_package.PyQtCustomComponent import Label

EDIT_WIDTH_SIZE = 650
EDIT_HEIGHT_SIZE = 170
TITLE_FONT_SIZE = 30
TEXT_EDIT_FONT_SIZE = 15


class NFCLayout(QVBoxLayout):
    input_signal = pyqtSignal(str)
    checker_signal = pyqtSignal(object)

    def __init__(self, nfc):
        super(NFCLayout, self).__init__()
        self.nfc = nfc
        nfc.signal.debug_nfc_signal.connect(self.input_text)

        self.addWidget(port_goup_box := QGroupBox('PORT'))
        port_goup_box.setLayout(port_layout := QVBoxLayout())
        port_layout.addWidget(port := Label(nfc.port))
        port.set_font_size(TITLE_FONT_SIZE)
        self.addWidget(id_group_box := QGroupBox("NFC ID"))
        id_group_box.setLayout(id_layout := QVBoxLayout())
        id_layout.addWidget(serial := Label(nfc.serial_name))
        serial.set_font_size(TITLE_FONT_SIZE)
        self.addWidget(input_group_box := QGroupBox('IN'))
        input_group_box.setLayout(input_layout := QVBoxLayout())
        input_layout.addWidget(nfc_enable := Label())
        nfc_enable.setFixedSize(EDIT_WIDTH_SIZE, EDIT_HEIGHT_SIZE)
        self.label_nfc_enable = nfc_enable
        self.enable = False
        self.line_num = 0
        self.check_timer = QTimer(self)
        self.check_timer.start(300)
        self.check_timer.timeout.connect(self.is_enable_display)

        self.input_signal.connect(self.input_text)
        self.checker_signal.connect(self.received_previous_process)

        self.th = Thread(target=self.nfc_check, daemon=True)
        self.th.start()

    def nfc_check(self):
        while True:
            if read_line := self.nfc.readline().decode():
                self.input_signal.emit(read_line)

    def is_enable_display(self):
        if self.enable:
            self.enable = False
        else:
            self.label_nfc_enable.clean()

    def received_previous_process(self, nfc):
        msg = [
            nfc.uid,
            nfc.dm,
            ','.join([f"{k}:{v}" for k, v in nfc.nfc_previous_process.items()]),
        ]
        self.label_nfc_enable.setText('\n'.join(msg))
        self.enable = True

    def input_text(self, input_msg):
        print(input_msg)
        if input_msg:
            split_data = input_msg.split(',')
            length = len(split_data)
            msg = ''
            if length == 1:
                msg = input_msg
            elif length == 2:
                msg = '\n'.join(split_data)
            else:
                msg = split_data[0] + '\n' + split_data[1] + '\n' + ','.join(split_data[2:])
            self.label_nfc_enable.setText(msg)
            self.enable = True
