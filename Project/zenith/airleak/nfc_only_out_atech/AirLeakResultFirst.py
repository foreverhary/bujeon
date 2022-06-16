import sys
from threading import Timer
from winsound import Beep

from PySide2.QtCore import Signal, Slot, Qt
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtWidgets import QApplication

from airleak.nfc_only_out_atech.AirLeakResultFirstUi import AirLeakUi
from process_package.SplashScreen import SplashScreen
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import style_sheet_setting, window_center, LIGHT_SKY_BLUE, \
    RED, AIR_LEAK_UNIT_COUNT, AIR_LEAK_PROCESS, logger, NG, AIR_LEAK_PREVIOUS_PROCESS, FREQ, DUR, get_time, AIR_LEAK, \
    make_error_popup, WHITE, OK, LIGHT_BLUE
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog


class AirLeak(AirLeakUi):
    status_signal = Signal(str, str)

    def __init__(self, app):
        super(AirLeak, self).__init__()
        self.app = app

        self.mssql = MSSQL(AIR_LEAK)
        self.mssql.timer_for_db_connect(self)

        # variable
        self.nfc = None
        self.dm_list = []

        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.connect_event()

        # window setting
        self.setWindowTitle('Air Leak v0.1')
        self.setWindowIcon(QIcon("./icon/python-icon.png"))

        self.load_window = SplashScreen("AIR LEAK")
        self.load_window.start_signal.connect(self.show_main_window)

        if not ports:
            self.show_main_window([])

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self, nfc_list):
        if len(nfc_list):
            self.nfc = nfc_list[0]
            self.nfc.previous_processes = AIR_LEAK_PREVIOUS_PROCESS
            self.nfc.signal.previous_process_signal.connect(self.received_previous_process)
            self.nfc.start_previous_process_check_thread()
            self.nfc.signal.nfc_write_done_signal.connect(self.update_sql)

            self.status_signal.emit("READY", LIGHT_SKY_BLUE)
        else:
            self.status_signal.emit("CHECK NFC & RESTART PROGRAM", RED)

        # machine connect from config value port
        self.fill_available_ports()
        self.connect_machine_button(1)

    def connect_event(self):
        self.status_signal.connect(self.status_update)
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)
        self.serial_machine.signal.machine_serial_error.connect(self.receive_machine_serial_error)

    @Slot(object)
    def receive_machine_serial_error(self, machine):
        self.check_serial_connection()
        make_error_popup(f"{self.serial_machine.port} Connect Fail!!")

    @Slot(list)
    def receive_machine_result(self, result):
        self.dm_list = []
        logger.info(result)
        self.result = result[0]
        self.result = OK if self.result == OK else NG
        self.result_label.set_background_color((RED, LIGHT_SKY_BLUE)[self.result == OK])
        self.result_label.set_color(WHITE)
        self.result_label.setText(self.result)
        for unit_label in self.unit_list:
            unit_label.clean()
        self.nfc.enable = True
        self.status_signal.emit("MACHINE RESULT RECEIVED ➡️ TAG NFC JIG", LIGHT_SKY_BLUE)

    @Slot(object)
    def received_previous_process(self, nfc):
        nfc.check_dm = ''
        self.unit_list[len(self.dm_list)].set_background_color(LIGHT_BLUE)
        if nfc.dm in self.dm_list:
            self.receive_same_dm(self.dm_list.index(nfc.dm))
            return
        if not self.result_label.text():
            return
        nfc_msg = [nfc.dm]
        nfc_msg.extend(f"{k}:{v}" for k, v in nfc.nfc_previous_process.items())
        msg = [nfc.dm, f"{AIR_LEAK_PROCESS}:{self.result_label.text()}"]
        logger.info(msg)
        if ','.join(nfc_msg) == ','.join(msg):
            self.mssql.start_query_thread(self.mssql.insert_pprd,
                                          get_time(),
                                          nfc.dm,
                                          self.result_label.text())
            self.update_sql(nfc)
        else:
            nfc.write(','.join(msg).encode())

    def blink_text(self, label, text):
        label.setText(text)

    def receive_same_dm(self, index):
        dm_label = self.unit_list[index]
        dm = self.dm_list[index]
        dm_label.clear()
        timer = Timer(0.1, self.blink_text, args=(dm_label, dm))
        timer.daemon = True
        timer.start()

    # @Slot(object)
    def update_sql(self, nfc):
        Beep(FREQ, DUR)
        dm_label = self.unit_list[len(self.dm_list)]
        dm_label.setText(nfc.dm)
        dm_label.set_color(WHITE)
        self.mssql.start_query_thread(self.mssql.insert_pprd,
                                      get_time(),
                                      nfc.dm,
                                      self.result)
        self.dm_list.append(nfc.dm)

        if len(self.dm_list) == AIR_LEAK_UNIT_COUNT:
            nfc.enable = False
            self.dm_list = []
            self.result_label.clean()
            self.status_signal.emit("UNIT WRITE DONE!!", LIGHT_SKY_BLUE)

    @Slot(str, str)
    def status_update(self, msg, color):
        self.status_label.setText(msg)
        self.status_label.set_color(color)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AirLeak(app)
    sys.exit(app.exec_())
