import sys
from threading import Thread
from winsound import Beep

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGridLayout, QGroupBox

from NFC import VirtualNFC
from nfc_layout import NFCLayout
from process_package.PyQtCustomComponent import LineEdit, Button, Label
from process_package.SplashScreen import SplashScreen
from process_package.check_string import check_nfc_uid
from process_package.defined_variable_function import style_sheet_setting, window_bottom_left, FREQ, DUR, logger

LOCATION = 'AA'


class NFCChecker(QWidget):
    def __init__(self, app):
        super(NFCChecker, self).__init__()
        self.app = app
        self.setLayout(layout := QGridLayout())
        self.grid_layout = layout
        self.nfc_layout = []

        self.load_nfc_window = SplashScreen("NFC Checker")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()

        for index, nfc in enumerate(nfc_list):
            self.grid_layout.addLayout(nfc_layout := NFCLayout(nfc), index // 2, index % 2)
            nfc_layout.input_signal.connect(self.input_text)
            self.nfc_layout.append(nfc_layout)
        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def input_text(self, input_msg):
        index = int(self.sender().nfc.serial_name[-1]) - 1
        self.nfc_layout[index].input_nfc.insertPlainText(input_msg)
        self.nfc_layout[index].input_nfc.moveCursor(QTextCursor.End)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFCChecker(app)
    sys.exit(app.exec_())
