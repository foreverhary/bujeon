import sys
from threading import Thread

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QApplication

from process_package.Config import get_order_number
from process_package.LineReadKeyboard import LineReadKeyboard
from process_package.check_string import check_dm
from process_package.defined_variable_function import style_sheet_setting, window_center, logger, WHITE
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from touchUI import TouchUI


class Touch(TouchUI):
    key_enter_input_signal = pyqtSignal(str)

    def __init__(self, app):
        super(Touch, self).__init__()
        self.app = app

        # QR scan listener
        self.start_keyboard_listener()

        self.order_config_window = OderNumberDialog()
        self.mssql_config_window = MSSQLDialog()

        self.connect_event()

        self.show_main_window()

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

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.dm_label.setText(dm)
            # insert_pprh(get_order_number(), dm)
            # self.start_nfc_read()

    def input_order_number(self):
        try:
            self.order_label.setText(get_order_number())
        except KeyError:
            logger.error('Need Config')

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.order_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.mssql_config_window.show_modal()

    def show_main_window(self):
        style_sheet_setting(self.app)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)

    def update_status_msg(self, msg, color=WHITE):
        if self.order_label.text():
            self.status_label.setText(msg)
            self.status_label.set_text_property(color=color)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Touch(app)
    sys.exit(app.exec_())
