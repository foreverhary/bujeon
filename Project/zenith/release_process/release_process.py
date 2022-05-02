import sys

import pymssql
import qdarkstyle
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from pynput import keyboard
from pynput.keyboard import Key

from process_package.SplashScreen import SplashScreen
from process_package.check_string import keyboard_event_check_char
from process_package.defined_variable_function import window_center, style_sheet_setting, NFC_IN, FUNCTION_PROCESS, \
    PROCESS_OK_RESULTS, PROCESS_NAMES
from process_package.logger import get_logger
from process_package.mssql_connect import *
from release_process_ui import ReleaseProcessUI
from process_package.style.style import STYLE

NFC_IN_COUNT = 1


class ReleaseProcess(ReleaseProcessUI):
    key_enter_input_signal = pyqtSignal()

    def __init__(self, app):
        super(ReleaseProcess, self).__init__()
        self.app = app
        self.nfc = None

        self.load_window = SplashScreen("Release")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        self.load_window.close()
        self.init_event()
        self.init_nfc_serial(nfcs)
        style_sheet_setting(self.app)

        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        self.dm_input_label.setText('AA1100001')
        self.result_input_label.setText("""
        this
        is
        spa
        """)

        window_center(self)

    def init_event(self):
        pass

    def init_nfc_serial(self, nfcs):
        nfc_in_count = 0
        for nfc in nfcs:
            if NFC_IN in nfc.serial_name:
                nfc.previous_processes = PROCESS_NAMES
                self.nfc = nfc
                nfc.signal.previous_process_signal.connect(self.received_previous_process)
                nfc.start_previous_process_check_thread()
                nfc_in_count += 1
            else:
                nfc.close()

        return nfc_in_count == NFC_IN_COUNT

    # @pyqtSignal(object)
    def received_previous_process(self, nfc):
        msg = ''
        if nfc.check_pre_process():
            msg += nfc.nfc_previous_process[FUNCTION_PROCESS]
        else:
            for process, result in nfc.nfc_previous_process.items():
                if result not in PROCESS_OK_RESULTS:
                    if msg:
                        msg += '\n'
                    msg += f"{process} : {result}"
        self.dm_input_label.setText(nfc.dm)
        self.result_input_label.setText(msg)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReleaseProcess(app)
    sys.exit(app.exec_())
