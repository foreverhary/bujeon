import re
import sys
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from airleak.nfc_only_out_atech.AirLeakResultFirstUi import AirLeakUi
from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, window_center, NFC, BLUE, LIGHT_SKY_BLUE, \
    RED, AIR_LEAK_UNIT_COUNT, AIR_LEAK_PROCESS, logger, NG, AIR_LEAK_PREPROCESS, FREQ, DUR, get_time
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog


class AirLeak(AirLeakUi):
    status_signal = pyqtSignal(str, str)

    def __init__(self, app):
        super(AirLeak, self).__init__()
        self.app = app

        self.mssql = MSSQL()
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)
        self.mssql.timer_for_db_connect(self)

        # variable
        self.nfc = {}

        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.connect_event()

        # window setting
        self.setWindowTitle('Air Leak v0.1')
        self.setWindowIcon(QIcon("./icon/python-icon.png"))

        self.load_window = SplashScreen("AIR LEAK")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self, nfc_list):

        for nfc in nfc_list:
            nfc.previous_processes = AIR_LEAK_PREPROCESS
            if re.search(f'{NFC}[1-9]', nfc.serial_name):
                self.nfc[nfc.serial_name] = nfc
                nfc.signal.nfc_write_done_signal.connect(self.update_sql)
            else:
                nfc.close()

        if self.nfc.__len__() == 1:
            self.status_signal.emit("READY", BLUE)
        else:
            self.status_signal.emit("CHECK NFC & RESTART PROGRAM", RED)

        # machine connect from config value port
        self.fill_available_ports()
        self.connect_machine_button(1)

    def connect_event(self):
        self.status_signal.connect(self.status_update)
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)

    @pyqtSlot(list)
    def receive_machine_result(self, result):
        logger.info(result)
        self.result = result[0]
        self.result_label.setText(self.result)
        self.result_label.set_color((LIGHT_SKY_BLUE, RED)[self.result == NG])
        for unit_label in self.unit_list:
            unit_label.setText('')
        if self.nfc.get(f"{NFC}1"):
            self.nfc[f"{NFC}1"].start_nfc_write(
                unit_count=AIR_LEAK_UNIT_COUNT,
                process_result=f"{AIR_LEAK_PROCESS}:{self.result}"
            )
        self.status_signal.emit("MACHINE RESULT RECEIVED ➡️ TAG NFC ZIG", LIGHT_SKY_BLUE)

    @pyqtSlot(object)
    def update_sql(self, nfc):
        Beep(FREQ, DUR)
        for output_label in self.unit_list:
            if output_label.text() == '':
                output_label.setText(nfc.dm)
                self.mssql.start_query_thread(self.mssql.insert_pprd,
                                              get_time(),
                                              nfc.dm,
                                              self.result)
                break
        if not nfc.unit_count:
            self.status_signal.emit("UNIT WRITE DONE!!", LIGHT_SKY_BLUE)

    @pyqtSlot(str, str)
    def status_update(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.set_color(color)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AirLeak(app)
    sys.exit(app.exec_())
