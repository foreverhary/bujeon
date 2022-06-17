import sys

from PySide2.QtCore import Qt, Signal, Slot, QObject
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QApplication

from process_package.SerialMachine import SerialMachine
from process_package.Views.CustomComponent import get_time, style_sheet_setting, window_center
from process_package.check_string import check_dm
from process_package.tools.CommonFunction import logger
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.models.Config import get_order_number, get_config_value, set_config_value
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from process_package.order_number_dialog import OderNumberDialog
from process_package.resource.color import WHITE, LIGHT_SKY_BLUE, RED
from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, STR_TOUCH, STR_NG, \
    STR_WRITE_DONE_SCAN_NEXT_QR
from TouchView import TouchView
from TouchControl import TouchControl
from TouchModel import TouchModel


class Touech(QObject):
    key_enter_input_signal = Signal(str)

    def __init__(self):
        super(Touch, self).__init__()

        self.view = TouchView()
        self.model = TouchModel()
        self.control = TouchControl()

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

        self.serial_machine = SerialMachine(baudrate=115200, serial_name=STR_TOUCH)
        self.connect_event()
        self.mssql = MSSQL(STR_TOUCH)
        self.mssql.timer_for_db_connect(self)

        self.input_order_number()

    def connect_event(self):
        self.comport.serial_open_signal.connect(
            lambda x: set_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, x)
        )
        self.comport.serial_line_signal.connect(self.receive_machine_line_message)
        self.keyboard_listener.keyboard_input_signal.connect(self.key_enter_process)
        self.order_config_window.orderNumberSendSignal.connect(self.input_order_number)
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)

    def key_enter_process(self, line_data):
        if dm := check_dm(line_data):
            self.data_matrix.setText(dm)
            self.mssql.start_query_thread(self.mssql.insert_pprh,
                                          get_time(),
                                          get_order_number(),
                                          dm)
            self.machine.clean()
            self.update_status_msg("Wait for Machine Result", WHITE)

    @Slot(list)
    def receive_machine_result(self, result):
        logger.info(result)
        self.result = result[0]
        self.machine.setText(self.result)
        self.machine.set_background_color((LIGHT_SKY_BLUE, RED)[self.result == STR_NG])
        if self.order.text() and self.data_matrix.text():
            self.mssql.start_query_thread(self.mssql.insert_pprd,
                                          get_time(),
                                          self.data_matrix.text(),
                                          self.result)
            self.update_status_msg(STR_WRITE_DONE_SCAN_NEXT_QR, LIGHT_SKY_BLUE)
        self.data_matrix.clear()

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


class Touch(QApplication):
    def __init__(self, sys_argv):
        super(Touch, self).__init__(sys_argv)
        style_sheet_setting(self)
        self.model = TouchModel()
        self.control = TouchControl(self.model)
        self.view = TouchView(self.model, self.control)
        self.model.begin_config_read()
        self.control.begin()
        self.view.show()

if __name__ == '__main__':
    logger.info("start touch process")
    app = Touch(sys.argv)
    sys.exit(app.exec_())
