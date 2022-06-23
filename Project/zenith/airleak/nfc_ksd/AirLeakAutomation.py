import re
import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon, QCursor
from PyQt5.QtWidgets import QApplication

from airleak.nfc_ksd.AirLeakAutomationUi import AirLeakAutomationUi, AIR_LEAK_NFC_COUNT
from process_package.screen.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, window_center, NFC, BLUE, RED, logger, \
    AIR_LEAK_PREVIOUS_PROCESS, get_time, make_error_popup
from process_package.tools.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog


class AirLeakAutomation(AirLeakAutomationUi):
    status_signal = pyqtSignal(str, str)

    def __init__(self, app):
        super(AirLeakAutomation, self).__init__()
        self.app = app

        self.mssql = MSSQL()
        self.mssql.timer_for_db_connect(self)

        # variable
        self.nfc = {}

        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.connect_event()

        # window setting
        self.setWindowTitle('Air Leak Automation v0.1')
        self.setWindowIcon(QIcon("./icon/python-icon.png"))

        self.load_window = SplashScreen("AIR LEAK")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        self.input_nfc_status()
        self.fill_machine_comport_combobox()
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self, nfcs):

        for nfc in nfcs:
            nfc.previous_processes = AIR_LEAK_PREVIOUS_PROCESS
            if re.search(f'{NFC}[1-9]', nfc.serial_name):
                self.nfc[nfc.num] = nfc
                nfc.signal.dm_read_done_signal.connect(self.received_nfc_read_done)
            else:
                nfc.close()

    def input_nfc_status(self):
        if self.nfc.__len__() == AIR_LEAK_NFC_COUNT:
            self.status_signal.emit("READY", BLUE)
            self.start_odd_nfc()
        else:
            self.status_signal.emit("NFC ERROR, CHECK NFC AND RESTART PROGRAM!!", RED)

    def fill_machine_comport_combobox(self):
        self.fill_available_ports()
        self.connect_machine_button(1)

    def connect_event(self):
        self.status_signal.connect(self.status_update)
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.serial_machine.signal.machine_result_ksd_signal.connect(self.receive_machine_result)
        self.serial_machine.signal.machine_serial_error.connect(self.receive_machine_serial_error)

    def is_odd_nfc_alive(self):
        return any(key % 2 and nfc.th.is_alive() for key, nfc in self.nfc.items())

    def is_even_nfc_alive(self):
        return any(key % 2 == 0 and nfc.th.is_alive() for key, nfc in self.nfc.items())

    def start_odd_nfc(self):
        logger.debug("")
        for key, nfc in self.nfc.items():
            if key % 2:
                nfc.start_read_dm_thread()
            else:
                nfc.power_down()

    def start_even_nfc(self):
        logger.debug("")
        for key, nfc in self.nfc.items():
            if key % 2 == 0:
                nfc.start_read_dm_thread()
            else:
                nfc.power_down()

    @pyqtSlot(object)
    def receive_machine_serial_error(self, machine):
        self.check_serial_connection()
        make_error_popup(f"{self.serial_machine.port} Connect Fail!!")

    @pyqtSlot(tuple)
    def receive_machine_result(self, channel_data):
        logger.debug(channel_data)
        channel, result = channel_data
        self.slots[channel - 1].result = result
        self.update_sql(channel - 1)

    @pyqtSlot(object)
    def received_nfc_read_done(self, nfc):
        logger.debug(nfc.num)
        self.slots[nfc.num - 1].dm = nfc.dm
        if nfc.num % 2:
            if not self.is_odd_nfc_alive():
                self.start_even_nfc()
        elif not self.is_even_nfc_alive():
            self.start_odd_nfc()

    @pyqtSlot(str, str)
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

    def update_sql(self, slot):
        self.mssql.start_query_thread(self.mssql.insert_pprd,
                                      self.slots[slot].dm,
                                      get_time(),
                                      self.slots[slot].result)

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AirLeakAutomation(app)
    sys.exit(app.exec_())
