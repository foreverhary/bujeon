import sys
from threading import Thread

from PySide2.QtCore import Qt, Signal, Slot
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QApplication

from process_package.SerialMachine import SerialMachine
from process_package.check_string import check_dm
from process_package.controllers.LineReadKeyboard import LineReadKeyboard
from process_package.defined_variable_function import style_sheet_setting, window_center, logger, WHITE, \
    CONFIG_FILE_NAME, COMPORT_SECTION, LIGHT_SKY_BLUE, RED, NG, MACHINE_COMPORT_1, TOUCH, \
    get_time, BLUE, make_error_popup
from process_package.models.Config import get_order_number, get_config_value, set_config_value
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from touchUI import TouchUI


class Touch(TouchUI):
    key_enter_input_signal = Signal(str)

    def __init__(self):
        super(Touch, self).__init__()

        self.comport.setup_serial(
            port=get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1),
            baudrate=QSerialPort.Baud115200
        )

        self.show()
        window_center(self)

        # QR scan listener
        self.keyboard_listener = LineReadKeyboard()

        self.order_config_window = OderNumberDialog()
        self.mssql_config_window = MSSQLDialog()

        self.serial_machine = SerialMachine(baudrate=115200, serial_name=TOUCH)
        self.connect_event()
        self.mssql = MSSQL(TOUCH)
        self.mssql.timer_for_db_connect(self)

        self.input_order_number()

    def connect_event(self):
        self.keyboard_listener.keyboard_input_signal.connect(self.key_enter_process)
        self.order_config_window.orderNumberSendSignal.connect(self.input_order_number)
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)
        self.serial_machine.signal.machine_serial_error.connect(self.receive_machine_serial_error)

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.data_matrix.setText(dm)
            self.mssql.start_query_thread(self.mssql.insert_pprh,
                                          get_time(),
                                          get_order_number(),
                                          dm)
            self.machine.clean()
            self.update_status_msg("Wait for Machine Result", WHITE)

    @Slot(object)
    def receive_machine_serial_error(self, machine):
        self.check_serial_connection()
        make_error_popup(f"{self.serial_machine.port} Connect Fail!!")

    @Slot(list)
    def receive_machine_result(self, result):
        logger.info(result)
        self.result = result[0]
        self.machine.setText(self.result)
        self.machine.set_background_color((LIGHT_SKY_BLUE, RED)[self.result == NG])
        if self.order.text() and self.data_matrix.text():
            self.mssql.start_query_thread(self.mssql.insert_pprd,
                                          get_time(),
                                          self.data_matrix.text(),
                                          self.result)
            self.update_status_msg("WRITE DONE SCAN NEXT QR", LIGHT_SKY_BLUE)
        self.data_matrix.clear()

    def check_serial_connection(self):
        if self.serial_machine.is_open:
            self.connect_button.set_clicked(BLUE)
            self.comport_combobox.setDisabled(True)
        else:
            self.connect_button.set_clicked(RED)
            self.comport_combobox.setEnabled(True)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            if order := self.order.text():
                self.order_config_window.orderNumberEdit.setText(order)
            self.order_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.mssql_config_window.show_modal()

    def input_order_number(self):
        try:
            self.order.setText(order := get_order_number())
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
        if self.order.text():
            self.status.setText(msg)
            self.status.set_color(color)
        else:
            self.status.setText("Check Order Number")
            self.status.set_color(RED)


if __name__ == '__main__':
    logger.info("start touch process")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = Touch()
    sys.exit(app.exec_())
