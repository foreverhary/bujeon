import sys
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication

from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, NFC_IN, SENSOR_PREPROCESS, \
    NFC, BLUE, RED, LIGHT_SKY_BLUE, FREQ, DUR, window_right, CON_OS, POGO_OS, VBAT_ID, C_TEST, LED, PCM, \
    PROX_TEST, BATTERY, MIC, Hall_IC, SENSOR, OK, SENSOR_PROCESS, WHITE, get_time
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog
from sensor_ui import SensorUI, NFC_IN_COUNT, NFC_OUT_COUNT


class SensorProcess(SensorUI):
    status_update_signal = pyqtSignal(object, str, str)
    machine_signal = pyqtSignal(str)
    error_code = {
        CON_OS: 1,
        POGO_OS: 2,
        LED: 3,
        VBAT_ID: 4,
        C_TEST: 5,
        BATTERY: 6,
        MIC: 7,
        PROX_TEST: 8,
        PCM: 9,
        Hall_IC: 10
    }

    def __init__(self, app):
        super(SensorProcess, self).__init__()
        self.app = app

        self.mssql = MSSQL(SENSOR)
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)
        self.mssql.timer_for_db_connect(self)

        # variable
        self.nfc = {}

        self.result = {name: True for name in self.error_code}

        self.connect_event()
        self.mssql_config_window = MSSQLDialog()

        self.load_window = SplashScreen("IR SENSOR")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)

        self.show()
        window_right(self)

    def nfc_check(self, nfcs):
        nfc_in_count = nfc_out_count = 0
        for nfc in nfcs:
            nfc.previous_processes = SENSOR_PREPROCESS
            if nfc.serial_name not in self.__dict__:
                self.__setattr__(nfc.serial_name, nfc)
                if NFC_IN in nfc.serial_name:
                    self.nfc[nfc.serial_name] = nfc
                    nfc.signal.previous_process_signal.connect(self.received_previous_process)
                    nfc.signal.serial_error_signal.connect(self.receive_serial_error)
                    nfc.start_previous_process_check_thread()
                    nfc_in_count += 1
                elif NFC in nfc.serial_name \
                        and int(nfc.serial_name[-1]) <= NFC_OUT_COUNT:
                    self.nfc[nfc.serial_name] = nfc
                    nfc.signal.nfc_write_done_signal.connect(self.update_sql)
                    nfc_out_count += 1
                else:
                    nfc.close()
        return (nfc_in_count, nfc_out_count) == (NFC_IN_COUNT, NFC_OUT_COUNT)

    def init_serial(self, nfc_list):
        for frame in self.ch_frame:
            frame.fill_available_ports()
            frame.connect_machine_button(1)
            frame.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)

        if self.nfc_check(nfc_list):
            self.status_update_signal.emit(self.status_label, "READY", BLUE)
        else:
            self.status_update_signal.emit(
                self.status_label,
                "CHECK NFC AND RESTART PROGRAM!!",
                RED
            )

    def connect_event(self):
        self.status_update_signal.connect(self.update_label)

    @pyqtSlot(object)
    def received_previous_process(self, nfc):
        Beep(FREQ, DUR)
        if nfc.check_pre_process():
            msg = f"{nfc.dm} is PASS"
            color = LIGHT_SKY_BLUE
        else:
            msg = f"{nfc.dm} is FAIL"
            color = RED
        label = self.previous_process_label[int(nfc.serial_name.replace(NFC_IN, '')) - 1]
        self.status_update_signal.emit(label, msg, color)

    @pyqtSlot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    @pyqtSlot(list)
    def receive_machine_result(self, result):
        self.init_result_true()
        if result[-1] != OK:
            for item, key in zip(result[1:-1], self.result):
                self.result[key] = item == OK
        if self.nfc.get(f"{NFC}1"):
            self.nfc[f"{NFC}1"].start_nfc_write(
                unit_count=1,
                process_result=f"{SENSOR_PROCESS}:{result[-1]}"
            )
            self.status_update_signal.emit(
                self.ch_frame[0].resultInput,
                result[-1],
                LIGHT_SKY_BLUE if result[-1] == OK else RED
            )
            self.status_update_signal.emit(
                self.status_label,
                "MACHINE RESULT RECEIVED ➡️ TAG NFC",
                LIGHT_SKY_BLUE)

    @pyqtSlot(object)
    def update_sql(self, nfc):
        result = nfc.current_process_result.split(':')[1]
        self.msslq.start_query_thread(self.mssql.insert_pprd,
                                      get_time(),
                                      nfc.dm,
                                      result,
                                      SENSOR,
                                      self.get_ecode())
        self.status_update_signal.emit(self.ch_frame[0].dmInput, nfc.dm, WHITE)
        self.status_update_signal.emit(self.status_label, f"{nfc.dm} is Write Done", LIGHT_SKY_BLUE)
        Beep(FREQ, DUR)

    @pyqtSlot(object, str, str)
    def update_label(self, label, text, color):
        label.setText(text)
        label.set_color(color)

    def get_ecode(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.result.items() if not value
        ])

    def init_result_true(self):
        self.result = {key: True for key in self.result}

    def keyPressEvent(self, event):
        pass

    def closeEvent(self, event):
        pass

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SensorProcess(app)
    sys.exit(app.exec_())
