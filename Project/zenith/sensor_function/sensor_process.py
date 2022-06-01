import sys
from threading import Timer
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from process_package.NGScreen import NGScreen
from process_package.SplashScreen import SplashScreen
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import style_sheet_setting, NFC_IN, SENSOR_PREVIOUS_PROCESS, \
    NFC, RED, LIGHT_SKY_BLUE, FREQ, DUR, SENSOR, OK, SENSOR_PROCESS, WHITE, window_center, make_error_popup, \
    NFCIN1, NFC1, NFC2
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from sensor_ui import SensorUI


class SensorProcess(SensorUI):
    status_update_signal = pyqtSignal(object, str, str)
    machine_signal = pyqtSignal(str)
    checker_signal = pyqtSignal(object)

    def __init__(self, app):
        super(SensorProcess, self).__init__()
        self.app = app

        self.mssql = MSSQL(SENSOR)
        self.mssql.timer_for_db_connect(self)

        for frame in self.ch_frame:
            frame.mssql = self.mssql

        # variable
        self.nfc = {}

        self.mssql_config_window = MSSQLDialog()
        self.ng_screen = NGScreen()

        self.connect_event()

        self.load_window = SplashScreen("IR SENSOR")
        self.load_window.start_signal.connect(self.show_main_window)

        if not ports:
            self.show_main_window([])

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)

    def nfc_check(self, nfc_list):
        for nfc in nfc_list:
            self.nfc[nfc.serial_name] = nfc
            nfc.signal.serial_error_signal.connect(self.receive_serial_error)
            nfc.start_previous_process_check_thread()
            if nfc.serial_name == NFCIN1:
                nfc.signal.previous_process_signal.connect(self.received_previous_process)
            else:
                self.ch_frame[int(nfc.serial_name[-1]) - 1].nfc = nfc
                nfc.signal.previous_process_signal.connect(
                    self.ch_frame[int(nfc.serial_name[-1]) - 1].received_previous_process
                )
        check_nfc_set = {NFCIN1, NFC1, NFC2}
        connected_nfc_set = {nfc.serial_name for nfc in self.nfc.values()}
        if not check_nfc_set - connected_nfc_set:
            return all(nfc.is_open for nfc in self.nfc.values())
        return False

    def init_serial(self, nfc_list):
        for frame in self.ch_frame:
            frame.fill_available_ports()
            frame.connect_machine_button(1)
            frame.serial_machine.signal.machine_serial_error.connect(self.receive_machine_serial_error)

        if self.nfc_check(nfc_list):
            self.status_update_signal.emit(self.status_label, "READY", LIGHT_SKY_BLUE)
        else:
            self.status_update_signal.emit(
                self.status_label,
                "CHECK NFC AND RESTART PROGRAM!!",
                RED
            )

    def connect_event(self):
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.status_update_signal.connect(self.update_label)

    @pyqtSlot(object)
    def received_previous_process(self, nfc):
        nfc.clean_check_dm()
        if self.ng_screen.isActiveWindow():
            return
        Beep(FREQ, DUR)
        label = self.previous_process_label[int(nfc.serial_name.replace(NFC_IN, '')) - 1]
        if nfc.dm and nfc.check_pre_process(SENSOR_PREVIOUS_PROCESS):
            color = LIGHT_SKY_BLUE
        else:
            self.ng_screen.set_text(nfc, SENSOR_PREVIOUS_PROCESS)
            self.ng_screen.show_modal()
            return

        label.set_background_color(color)
        if nfc.dm:
            self.status_update_signal.emit(label, nfc.dm, WHITE)

    @pyqtSlot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    @pyqtSlot(object)
    def receive_machine_serial_error(self, machine):
        frame = self.ch_frame[0] if '1' in machine.serial_name else self.ch_frame[1]
        frame.check_serial_connection()
        make_error_popup(f"{frame.serial_machine.port} Connect Fail!!")

    @pyqtSlot(object, str, str)
    def update_label(self, label, text, color):
        label.setText(text)
        label.set_color(color)

    def keyPressEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.ng_screen.show_modal()
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SensorProcess(app)
    sys.exit(app.exec_())
