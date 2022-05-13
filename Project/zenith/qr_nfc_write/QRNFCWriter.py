import sys
from threading import Thread
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtWidgets import QApplication

from process_package.Config import get_order_number
from process_package.LineReadKeyboard import LineReadKeyboard
from process_package.SplashScreen import SplashScreen
from process_package.check_string import check_dm
from process_package.defined_variable_function import BLUE, RED, style_sheet_setting, window_center, logger, WHITE, NFC, \
    FREQ, DUR, OK, LIGHT_SKY_BLUE
from process_package.mssql_connect import insert_pprh, select_result_with_dm_keyword
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from qr_nfc_write.QRNFCWriterUI import QRNFCWriterUI


class QRNFCWriter(QRNFCWriterUI):
    key_enter_input_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, str)

    def __init__(self, app):
        super(QRNFCWriter, self).__init__()

        self.app = app

        self.nfc = None

        # QR scan listener
        self.start_keyboard_listener()

        self.order_config_window = OderNumberDialog()
        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.connect_event()

        self.input_order_number()

        self.load_nfc_window = SplashScreen("QR RESISTOR")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self, nfc_list):
        ready_nfc = False
        for nfc in nfc_list:
            if nfc.serial_name == f"{NFC}1":
                self.nfc = nfc
                self.nfc.signal.qr_write_done_signal.connect(self.received_qr_write)
                self.nfc.signal.serial_error_signal.connect(self.receive_serial_error)
                ready_nfc = True
            else:
                nfc.close()
        if ready_nfc:
            self.status_signal.emit("READY TO QR SCAN!!", BLUE)
        else:
            self.status_signal.emit("CHECK NFC RESTART PROGRAM!!", RED)

    def start_keyboard_listener(self):
        self.keyboard_listener = Thread(target=self.listen_keyboard, args=(LineReadKeyboard,), daemon=True)
        self.keyboard_listener.start()

    def listen_keyboard(self, func):
        listener = func()
        self.key_enter_input_signal.emit(listener.get_line())
        self.start_keyboard_listener()

    def connect_event(self):
        self.key_enter_input_signal.connect(self.key_enter_process)
        self.order_config_window.orderNumberSendSignal.connect(self.input_order_number)
        self.status_signal.connect(self.status_update)

    @pyqtSlot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    def received_qr_write(self, msg, color):
        Beep(FREQ, DUR)
        self.status_update(msg, color)

    def status_update(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.set_text_property(color=color)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.order_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.mssql_config_window.show_modal()

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.dm_label.setText(dm)
            if touch_result := select_result_with_dm_keyword(dm, 'touch'):
                if touch_result[0] == OK:
                    self.preprocess_label.set_text_property(color=LIGHT_SKY_BLUE)
                    self.preprocess_label.setText("PREPROCESS OK")
                else:
                    self.preprocess_label.set_text_property(color=RED)
                    self.preprocess_label.setText("PREPROCESS NG")
            else:
                self.preprocess_label.set_text_property(color=RED)
                self.preprocess_label.setText("DM IS NOT REGISTERED\nOR\nNETWORK FAIL!!")

    def start_nfc_read(self):
        if self.nfc:
            self.status_signal.emit("TAG NFC ZIG", WHITE)
            self.nfc.start_nfc_write(self.dm_label.text())

    def input_order_number(self):
        try:
            # self.order_label.setText(get_order_number())
            pass
        except KeyError:
            logger.error('Need Config')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # style_sheet_setting(app)
    ex = QRNFCWriter(app)
    sys.exit(app.exec_())
