import re
import sys
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from airleak.nfc_ksd.AirLeakAutomationUi import AirLeakAutomationUi, AIR_LEAK_NFC_COUNT
from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, window_center, NFC, BLUE, LIGHT_SKY_BLUE, \
    RED, AIR_LEAK_UNIT_COUNT, AIR_LEAK_PROCESS, logger, NG, LEAK, AIR_LEAK_PREPROCESS, FREQ, DUR
from process_package.mssql_connect import insert_pprd
from process_package.mssql_dialog import MSSQLDialog


class AirLeakAutomation(AirLeakAutomationUi):
    status_signal = pyqtSignal(str, str)

    def __init__(self, app):
        super(AirLeakAutomation, self).__init__()
        self.app = app

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
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self, nfcs):

        for nfc in nfcs:
            nfc.previous_processes = AIR_LEAK_PREPROCESS
            if re.search(f'{NFC}[1-9]', nfc.serial_name):
                self.nfc[int(nfc.serial_name[-1])] = nfc
                nfc.signal.nfc_write_done_signal.connect(self.update_sql)
            else:
                nfc.close()

        if self.nfc.__len__() == AIR_LEAK_NFC_COUNT:
            self.status_signal.emit("READY", BLUE)
        else:
            self.status_signal.emit("NFC ERROR, CHECK NFC AND RESTART PROGRAM!!", RED)

        # machine connect from config value port
        self.fill_available_ports()
        self.connect_machine_button(1)

    def connect_event(self):
        self.status_signal.connect(self.status_update)
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)

    def is_odd_nfc_alive(self):
        for key, nfc in self.nfc.items():
            if key % 2:
                if nfc.th.is_alive()
        pass

    def is_even_nfc_alive(self):
        # TODO
        pass

    def start_odd_nfc(self):
        for key, nfc in self.nfc.items():
            if key % 2:
                nfc.start_previous_process_check_thread()

    def start_even_nfc(self):
        for key, nfc in self.nfc.items():
            if key % 2 == 0:
                nfc.start_previous_process_check_thread()

    @pyqtSlot(list)
    def receive_machine_result(self, result):
        logger.info(result)
        self.result = result[0]
        self.result_label.setText(self.result)
        self.result_label.set_text_property(color=(LIGHT_SKY_BLUE, RED)[self.result == NG])
        for unit_label in self.unit_list:
            unit_label.setText('')
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
                try:
                    insert_pprd(nfc.dm, self.result, LEAK)
                except Exception as e:
                    logger.error(f"{type(e)} : {e}")
                break
        if not nfc.unit_count:
            self.status_signal.emit("UNIT WRITE DONE!!", LIGHT_SKY_BLUE)

    @pyqtSlot(str, str)
    def status_update(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.set_text_property(color=color)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AirLeakAutomation(app)
    sys.exit(app.exec_())
