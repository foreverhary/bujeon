import sys
from threading import Thread

from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from process_package.Config import get_order_number, get_config_value, set_config_value
from process_package.LineReadKeyboard import LineReadKeyboard
from process_package.SerialMachine import SerialMachine
from process_package.check_string import check_dm
from process_package.defined_variable_function import style_sheet_setting, window_center, logger, WHITE, \
    CONFIG_FILE_NAME, COMPORT_SECTION, AIR_LEAK_ATECH, LIGHT_SKY_BLUE, RED, NG, MACHINE_COMPORT_1, TOUCH, \
    get_time, BLUE, make_error_popup
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from touchUI import TouchUI


class Touch(TouchUI):
    key_enter_input_signal = pyqtSignal(str)

    def __init__(self, app):
        super(Touch, self).__init__()
        self.app = app

        self.show_main_window()

        # QR scan listener
        self.start_keyboard_listener()

        self.order_config_window = OderNumberDialog()
        self.mssql_config_window = MSSQLDialog()

        self.serial_machine = SerialMachine(baudrate=115200, serial_name=TOUCH)
        self.connect_event()
        self.mssql = MSSQL(TOUCH)
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)
        self.mssql.timer_for_db_connect(self)

        self.input_order_number()

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
        self.connect_button.clicked.connect(self.connect_machine_button)
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)
        self.serial_machine.signal.machine_serial_error.connect(self.receive_machine_serial_error)
        self.connect_machine_button(1)

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.dm_label.setText(dm)
            self.mssql.start_query_thread(self.mssql.insert_pprh,
                                          get_time(),
                                          get_order_number(),
                                          dm)
            self.machine_label.clean()
            self.update_status_msg("Wait for Machine Result", WHITE)

    @pyqtSlot(object)
    def receive_machine_serial_error(self, machine):
        self.check_serial_connection()
        make_error_popup(f"{self.serial_machine.port} Connect Fail!!")

    @pyqtSlot(list)
    def receive_machine_result(self, result):
        logger.info(result)
        self.result = result[0]
        self.machine_label.setText(self.result)
        self.machine_label.set_background_color((LIGHT_SKY_BLUE, RED)[self.result == NG])
        if self.order_label.text() and self.dm_label.text():
            self.mssql.start_query_thread(self.mssql.insert_pprd,
                                          get_time(),
                                          self.dm_label.text(),
                                          self.result)
            self.update_status_msg("WRITE DONE SCAN NEXT QR", LIGHT_SKY_BLUE)
        self.dm_label.clear()

    def connect_machine_button(self, not_key=None):
        if not_key:
            button = self.connect_button
            self.comport_combobox.setCurrentText(
                get_config_value(
                    CONFIG_FILE_NAME,
                    COMPORT_SECTION,
                    MACHINE_COMPORT_1
                )
            )
        else:
            button = self.sender()

        if self.serial_machine.connect_serial(self.comport_combobox.currentText()):
            set_config_value(
                CONFIG_FILE_NAME,
                COMPORT_SECTION,
                MACHINE_COMPORT_1,
                self.serial_machine.port
            )
            self.serial_machine.start_machine_read()
        self.check_serial_connection()

    def check_serial_connection(self):
        if self.serial_machine.is_open:
            self.connect_button.set_clicked(BLUE)
            self.comport_combobox.setDisabled(True)
        else:
            self.connect_button.set_clicked(RED)
            self.comport_combobox.setEnabled(True)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            if order := self.order_label.text():
                self.order_config_window.orderNumberEdit.setText(order)
            self.order_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
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

    def show_main_window(self):
        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)

    def input_order_number(self):
        try:
            self.order_label.setText(order := get_order_number())
            if order:
                if order != self.mssql.aufnr:
                    self.mssql.aufnr = order
                self.update_status_msg("READY", LIGHT_SKY_BLUE)
            else:
                self.update_status_msg("Check Order Number", RED)
        except KeyError:
            logger.error('Need Config')

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)

    def update_status_msg(self, msg, color=WHITE):
        if self.order_label.text():
            self.status_label.setText(msg)
            self.status_label.set_color(color)
        else:
            self.status_label.setText("Check Order Number")
            self.status_label.set_color(RED)


if __name__ == '__main__':
    logger.info("start touch process")
    app = QApplication(sys.argv)
    ex = Touch(app)
    sys.exit(app.exec_())
