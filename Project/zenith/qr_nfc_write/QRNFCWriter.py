import sys
from threading import Thread

from PySide2.QtCore import Signal, Qt, Slot
from PySide2.QtWidgets import QApplication
from winsound import Beep

from process_package.check_string import check_dm
from process_package.controllers.LineReadKeyboard import LineReadKeyboard
from process_package.controllers.NFCCheck import NFCCheck
from process_package.defined_variable_function import style_sheet_setting, window_center, logger, FREQ, DUR, \
    OK, PREVIOUS_PROCESS_OK, PREVIOUS_PROCESS_NG, TRY_NEXT_QR_SCAN, TAG_NFC_ZIG, \
    WRITE_DONE, TOUCH
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from process_package.resource.color import LIGHT_SKY_BLUE, RED, WHITE
from process_package.resource.string import STR_READY_TO_QR_SCAN
from qr_nfc_write.QRNFCWriterUI import QRNFCWriterUI


class QRNFCWriter(QRNFCWriterUI):
    key_enter_input_signal = Signal(str)
    status_signal = Signal(str, str)

    def __init__(self):
        super(QRNFCWriter, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)

        self.status.setText("Check NFC ...")
        search_nfcs = NFCCheck()

        search_nfcs.serial_check_done.connect(self.init_serial)

        # QR scan listener
        self.keyboard_listener = LineReadKeyboard()

        self.order_config_window = OderNumberDialog()
        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.mssql = MSSQL()
        self.mssql.signal.pre_process_result_signal.connect(self.received_preproess_result)
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)
        self.mssql.timer_for_db_connect(self)

        self.input_order_number()

        # self.load_nfc_window = SplashScreen("QR RESISTOR")
        # self.load_nfc_window.start_signal.connect(self.show_main_window)

    def init_serial(self, nfcs):
        logger.info(nfcs)
        # ready_nfc = False
        # for nfc in nfcs:
        #     self.nfc = nfc
        #     self.nfc.signal.qr_write_done_signal.connect(self.received_qr_write)
        #     self.nfc.signal.serial_error_signal.connect(self.receive_serial_error)
        #     ready_nfc = True
        # if ready_nfc:
        #     self.status_signal.emit(READY_TO_QR_SCAN, LIGHT_SKY_BLUE)
        # else:
        #     self.status_signal.emit(CHECK_NFC_RESTART_PROGRAM, RED)
        self.connect_event()

    def start_keyboard_listener(self):
        self.keyboard_listener = Thread(target=self.listen_keyboard, args=(LineReadKeyboard,), daemon=True)
        self.keyboard_listener.start()

    def listen_keyboard(self, func):
        listener = func()
        self.key_enter_input_signal.emit(listener.get_line())
        self.start_keyboard_listener()

    def connect_event(self):
        self.status_update(STR_READY_TO_QR_SCAN, LIGHT_SKY_BLUE)
        self.keyboard_listener.keyboard_input_signal.connect(self.key_enter_process)
        self.order_config_window.orderNumberSendSignal.connect(self.input_order_number)
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.status_signal.connect(self.status_update)

    @Slot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status, msg, RED)

    def received_qr_write(self):
        Beep(FREQ, DUR)
        self.data_matrix.clear()
        self.status_update(f"{WRITE_DONE}, {TRY_NEXT_QR_SCAN}", LIGHT_SKY_BLUE)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.data_matrix.setText(dm)
            self.previous_process.clear()
            if self.mssql.con:
                self.mssql.start_query_thread(self.mssql.select_result_with_dm_keyword, dm, TOUCH)
            else:  # Fake
                self.previous_process.set_color(LIGHT_SKY_BLUE)
                self.previous_process.setText(PREVIOUS_PROCESS_OK)
                self.start_nfc_read()

    def received_preproess_result(self, preprocess_result):
        if not preprocess_result or preprocess_result == OK:
            self.previous_process.set_color(LIGHT_SKY_BLUE)
            self.previous_process.setText(PREVIOUS_PROCESS_OK)
            self.start_nfc_read()
        else:
            self.previous_process.set_color(RED)
            self.previous_process.setText(PREVIOUS_PROCESS_NG)
            self.status_update(TRY_NEXT_QR_SCAN, LIGHT_SKY_BLUE)

    def start_nfc_read(self):
        if self.nfc:
            self.status_signal.emit(TAG_NFC_ZIG, WHITE)
            self.nfc.start_nfc_write(self.data_matrix.text())

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
    style_sheet_setting(app)
    ex = QRNFCWriter()
    sys.exit(app.exec_())
