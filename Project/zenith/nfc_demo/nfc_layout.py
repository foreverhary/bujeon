from threading import Thread
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QTextEdit

from process_package.PyQtCustomComponent import Label
from process_package.check_string import check_nfc_uid
from process_package.defined_variable_function import logger, FREQ, DUR, LIGHT_SKY_BLUE

EDIT_WIDTH_SIZE = 650
EDIT_HEIGHT_SIZE = 150
TITLE_FONT_SIZE = 30
TEXT_EDIT_FONT_SIZE = 15


class NFCLayout(QVBoxLayout):
    input_signal = pyqtSignal(object)

    def __init__(self, nfc):
        super(NFCLayout, self).__init__()
        self.nfc = nfc

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

        self.th = Thread(target=self.nfc_check, daemon=True)
        self.th.start()

    def nfc_check(self):
        while True:
            if read_line := self.nfc.readline().decode():
                self.input_signal.emit(read_line)

    def is_enable_display(self):
        if self.enable:
            self.label_nfc_enable.set_background_color(LIGHT_SKY_BLUE)
            self.enable = False
        else:
            self.label_nfc_enable.clean()

    def input_text(self, input_msg):
        if input_msg:
            self.enable = True
