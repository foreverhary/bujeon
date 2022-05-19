import sys
from threading import Thread
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from process_package.LineReadKeyboard import LineReadKeyboard
from process_package.SplashScreen import SplashScreen
from process_package.check_string import check_dm
from process_package.defined_variable_function import BLUE, RED, style_sheet_setting, window_center, logger, WHITE, NFC, \
    FREQ, DUR, OK, LIGHT_SKY_BLUE, TOUCH, PREVIOUS_PROCESS_OK, PREVIOUS_PROCESS_NG, TRY_NEXT_QR_SCAN, TAG_NFC_ZIG, \
    WRITE_DONE, READY_TO_QR_SCAN, CHECK_NFC_RESTART_PROGRAM
from process_package.mssql_connect import MSSQL
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
        self.mssql = MSSQL()
        self.mssql.signal.pre_process_result_signal.connect(self.received_preproess_result)
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)
        self.mssql.timer_for_db_connect(self)

        self.input_order_number()

        self.load_nfc_window = SplashScreen("QR RESISTOR")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
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
            self.status_signal.emit(READY_TO_QR_SCAN, LIGHT_SKY_BLUE)
        else:
            self.status_signal.emit(CHECK_NFC_RESTART_PROGRAM, RED)

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
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.status_signal.connect(self.status_update)

    @pyqtSlot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    def received_qr_write(self):
        Beep(FREQ, DUR)
        self.dm_label.clear()
        self.status_update(f"{WRITE_DONE}, {TRY_NEXT_QR_SCAN}", LIGHT_SKY_BLUE)

    def status_update(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.set_color(color)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()
        if e.buttons() & Qt.LeftButton:
            self.m_flag = True
            self.m_Position = e.globalPos() - self.pos()
            e.accept()
            self.setCursor((QCursor(Qt.OpenHandCursor)))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.dm_label.setText(dm)
            self.preprocess_label.clear()
            if self.mssql.con:
                self.mssql.start_query_thread(self.mssql.select_result_with_dm_keyword, dm, TOUCH)
            else:  # Fake
                self.preprocess_label.set_color(LIGHT_SKY_BLUE)
                self.preprocess_label.setText(PREVIOUS_PROCESS_OK)
                self.start_nfc_read()

    def received_preproess_result(self, preprocess_result):
        if not preprocess_result or preprocess_result == OK:
            self.preprocess_label.set_color(LIGHT_SKY_BLUE)
            self.preprocess_label.setText(PREVIOUS_PROCESS_OK)
            self.start_nfc_read()
        else:
            self.preprocess_label.set_color(RED)
            self.preprocess_label.setText(PREVIOUS_PROCESS_NG)
            self.status_update(TRY_NEXT_QR_SCAN, LIGHT_SKY_BLUE)

    def start_nfc_read(self):
        if self.nfc:
            self.status_signal.emit(TAG_NFC_ZIG, WHITE)
            self.nfc.start_nfc_write(self.dm_label.text())

    def input_order_number(self):
        try:
            # self.order_label.setText(get_order_number())
            pass
        except KeyError:
            logger.error('Need Config')

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # style_sheet_setting(app)
    ex = QRNFCWriter(app)
    sys.exit(app.exec_())
