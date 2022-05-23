from threading import Thread
from winsound import Beep

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QGroupBox, QTextEdit

from process_package.PyQtCustomComponent import Label
from process_package.check_string import check_nfc_uid
from process_package.defined_variable_function import logger, FREQ, DUR

EDIT_WIDTH_SIZE = 500
EDIT_HEIGHT_SIZE = 200


class NFCLayout(QVBoxLayout):
    input_signal = pyqtSignal(object)

    def __init__(self, nfc):
        super(NFCLayout, self).__init__()
        self.nfc = nfc

        self.addWidget(port_goup_box := QGroupBox('PORT'))
        port_goup_box.setLayout(port_layout := QVBoxLayout())
        port_layout.addWidget(Label(nfc.port))

        self.addWidget(id_group_box := QGroupBox("NFC ID"))
        id_group_box.setLayout(id_layout := QVBoxLayout())
        id_layout.addWidget(Label(nfc.serial_name))

        self.addWidget(input_group_box := QGroupBox('IN'))
        input_group_box.setLayout(input_layout := QVBoxLayout())
        input_layout.addWidget(input_nfc := QTextEdit())
        input_nfc.setFixedSize(EDIT_WIDTH_SIZE, EDIT_HEIGHT_SIZE)
        self.input_nfc = input_nfc

        self.th = Thread(target=self.nfc_check, daemon=True)
        self.th.start()

    def nfc_check(self):
        while True:
            if read_line := self.nfc.readline().decode():
                self.input_signal.emit(read_line)
