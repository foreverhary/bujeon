import csv
import os.path
import sys
from threading import Timer

from PySide2.QtCore import Qt, Slot, Signal
from PySide2.QtWidgets import QApplication
from winsound import Beep
from xlrd import open_workbook

from AudioBusUI import AudioBusUI
from FileObserver import Target
from audio_bus.AudioBusConfig import AudioBusConfig
from process_package.NGScreen import NGScreen
from process_package.SplashScreen import SplashScreen
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import style_sheet_setting, window_right, logger, \
    FUNCTION_PREVIOUS_PROCESS, \
    LIGHT_SKY_BLUE, RED, GRADE_FILE_PATH, WHITE, SUMMARY_FILE_PATH, A, B, C, C_GRADE_MIN, \
    C_GRADE_MAX, B_GRADE_MAX, A_GRADE_MAX, NG, \
    FUNCTION_PROCESS, SPL, THD, IMP, MIC_FRF, RUB_BUZ, POLARITY, FUNCTION, HOHD, AUD, FREQ, DUR, get_time, YELLOW, \
    GREEN, NFCIN1, NFC1, LIGHT_BLUE, PROCESS_NAMES
from process_package.models.Config import get_config_audio_bus
from process_package.mssql_connect import MSSQL
from process_package.mssql_dialog import MSSQLDialog

NFC_IN_COUNT = 1
NFC_OUT_COUNT = 2


class AudioBus(AudioBusUI):
    status_update_signal = Signal(object, str, str)
    grade_signal = Signal(str)
    summary_signal = Signal(str)
    error_code = {
        SPL: 1,
        THD: 2,
        IMP: 3,
        MIC_FRF: 4,
        RUB_BUZ: 5,
        HOHD: 6,
        POLARITY: 7,
    }

    def __init__(self, app):
        super(AudioBus, self).__init__()
        self.app = app

        self.mssql = MSSQL(AUD)
        self.mssql.timer_for_db_connect(self)

        # sub windows
        self.audio_bus_config_window = AudioBusConfig()
        self.mssql_config_window = MSSQLDialog()
        self.ng_screen = NGScreen()

        # variable
        self.nfc = {}
        self.received_nfc = None
        self.summary_file_path = ''
        self.grade = ''
        self.grade_file_observer = Target(signal=self.grade_signal)
        self.summary_file_observer = Target(signal=self.summary_signal)

        self.result = {name: True for name in self.error_code}
        logger.debug(self.result)

        # NFC Auto connect
        self.load_window = SplashScreen("Audio Bus", [])
        self.load_window.start_signal.connect(self.show_main_window)
        if not ports:
            self.show_main_window([])

        self.timer_check_result = Timer(3, self.check_result)

        self.write_nfc_msg = ''
        self.write_delay_count = 0
        self.nfc_write_result = ''

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_event()
        if self.init_nfc_serial(nfc_list):
            self.start_file_observe()
        else:
            self.status_update_signal.emit(self.status_label, 'CHECK NFC & RESTART PROGRAM!!', RED)
        style_sheet_setting(self.app)

        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

        window_right(self)

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if isinstance(value, float):
            color = RED
            if float(get_config_audio_bus(B_GRADE_MAX)) < value:
                self._grade = NG
            elif float(get_config_audio_bus(A_GRADE_MAX)) < value:
                self._grade = B
                color = GREEN
            elif float(get_config_audio_bus(C_GRADE_MAX)) < value:
                self._grade = A
                color = WHITE
            elif float(get_config_audio_bus(C_GRADE_MIN)) <= value:
                self._grade = C
                color = YELLOW
            else:
                self._grade = NG
            self.status_update_signal.emit(self.grade_label, f"{self._grade} : {value:.2f}", color)
        elif isinstance(value, str):
            self._grade = value
            self.status_update_signal.emit(self.grade_label, NG, RED)
        else:
            self._grade = NG
        logger.debug(self._grade)

    @Slot(object)
    def update_sql(self, nfc):
        self.mssql.start_query_thread(self.mssql.insert_pprd,
                                      get_time(),
                                      nfc.dm,
                                      self.grade,
                                      FUNCTION,
                                      self.get_ecode())

    def get_ecode(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.result.items() if not value
        ])

    def init_result_true(self):
        self.result = {key: True for key in self.result}

    def init_event(self):
        self.mssql_config_window.mssql_change_signal.connect(self.mssql_reconnect)
        self.audio_bus_config_window.close_signal.connect(self.start_file_observe)
        self.status_update_signal.connect(self.update_label)
        self.grade_signal.connect(self.grade_process)
        self.summary_signal.connect(self.summary_process)

    def init_nfc_serial(self, nfc_list):
        for nfc in nfc_list:
            self.nfc[nfc.serial_name] = nfc
            nfc.signal.previous_process_signal.connect(self.receive_nfc_signal)
            nfc.signal.serial_error_signal.connect(self.receive_serial_error)
            nfc.start_previous_process_check_thread()
        return self.is_nfc_ok()

    @Slot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    @Slot(object)
    def receive_nfc_signal(self, nfc):
        if self.is_nfc_in_exist():
            self.previous_process_label.is_clean = True
            if NFCIN1 == nfc.serial_name:
                nfc.clean_check_dm()
                if self.ng_screen.isActiveWindow():
                    return
                Beep(FREQ, DUR)
                if nfc.check_pre_process(FUNCTION_PREVIOUS_PROCESS):
                    color = LIGHT_SKY_BLUE
                else:
                    self.ng_screen.set_text(nfc, FUNCTION_PREVIOUS_PROCESS)
                    self.ng_screen.show_modal()
                    return
                self.previous_process_label.set_background_color(color)
                self.status_update_signal.emit(self.previous_process_label, nfc.dm, WHITE)
            else:
                nfc.clean_check_dm()
                self.write_label.set_background_color(LIGHT_BLUE)
                if not nfc.check_pre_process_valid(FUNCTION_PREVIOUS_PROCESS):
                    return
                msg = [nfc.dm]
                msg.extend(
                    f"{process_name}:{nfc.nfc_previous_process[process_name]}"
                    for process_name in PROCESS_NAMES
                    if process_name in nfc.nfc_previous_process
                )
                if self.write_delay_count:
                    self.write_delay_count -= 1
                    return
                if not self.nfc_write_result:
                    return
                if self.write_nfc_msg != ','.join(msg):
                    self.write_delay_count += 1
                    write_msg = [nfc.dm]
                    write_msg.extend(
                        f"{process_name}:{nfc.nfc_previous_process[process_name]}"
                        for process_name in FUNCTION_PREVIOUS_PROCESS
                        if process_name in nfc.nfc_previous_process
                    )
                    write_msg.append(f"{FUNCTION_PROCESS}:{self.nfc_write_result}")
                    self.write_nfc_msg = ','.join(write_msg)
                    msg = self.write_nfc_msg
                    nfc.write(msg.encode())
                else:
                    self.write_label.setText(nfc.dm)
                    self.update_sql(nfc)
                    self.nfc_write_result = ''
                    self.status_update_signal.emit(self.status_label, f"{nfc.dm} is Write Done", LIGHT_SKY_BLUE)
                    self.reset_anti_repeat_parameter()
        else:
            color = LIGHT_SKY_BLUE if nfc.check_pre_process(FUNCTION_PREVIOUS_PROCESS) else RED
            self.previous_process_label.set_background_color(color)
            self.status_update_signal.emit(self.previous_process_label, nfc.dm, WHITE)
            if nfc.check_pre_process_valid(FUNCTION_PREVIOUS_PROCESS):
                self.received_nfc = nfc
                self.reset_anti_repeat_parameter()

    @Slot(object, str, str)
    def update_label(self, label, text, color):
        label.setText(text)
        label.set_color(color)

    @Slot(str)
    def grade_process(self, file_path):
        try:
            logger.debug(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                rdr = csv.reader(f)
                for line in rdr:
                    logger.debug(line)
                    if line[0].upper() == "CH1":
                        self.grade = float(line[1])
                        break
            self.status_label.clean()
            self.status_update_signal.emit(self.status_label, 'Reading Grade File...', WHITE)
            self.summary_file_path = None
        except Exception as e:
            logger.error(e)

    @Slot(str)
    def summary_process(self, file_path):
        try:
            if self.summary_file_path == file_path:
                return
            self.summary_file_path = file_path
            self.status_update_signal.emit(self.status_label, 'Read Result...', WHITE)
            sheet = open_workbook(file_path).sheet_by_name('Summary')
            self.parse_and_check_result(sheet)
            self.status_update_signal.emit(self.status_label, 'NFC TAG', WHITE)
            # self.update_sql(self.received_nfc)
            # self.timer_check_result = Timer(3, self.check_result)
            # self.timer_check_result.daemon = True
            # self.timer_check_result.start()
        except ValueError as e:
            logger.error(type(e))
        except Exception as e:
            logger.debug(e)

    def check_result(self):
        self.status_label.set_background_color(RED)
        self.status_update_signal.emit(self.status_label, f"{self.received_nfc.dm} WRITE MISS", WHITE)

    def is_nfc_in_exist(self):
        return NFCIN1 in self.nfc

    def is_nfc_ok(self):
        # check_nfc_set = {NFC1, NFC2}
        check_nfc_set = {NFC1}
        connected_nfc_set = {nfc.serial_name for nfc in self.nfc.values()}
        if not check_nfc_set - connected_nfc_set:
            return all(nfc.is_open for nfc in self.nfc.values())
        return False

    def reset_anti_repeat_parameter(self):
        self.summary_file_path = ''

    def parse_and_check_result(self, sheet):
        summary = []
        for i in range(sheet.nrows):
            row = [sheet.cell_value(i, l) for l in range(sheet.ncols)]
            summary.append(row)
        row_iter = summary.__iter__()
        result = {}
        for item in row_iter:
            if 'Summary' in item[0]:
                next(row_iter)
                data = next(row_iter)
                name = item[0].split('Summary:')[1].strip().upper()
                result[name] = (data[1], data[2])
        self.init_result_true()
        for name, result_value in result.items():
            for key in self.result:
                if key in name and 'Failed' in result_value:
                    self.result[key] = False

        self.nfc_write_result = NG if False in self.result.values() else self.grade
        # msg = [self.received_nfc.dm]
        # msg.extend(
        #     f"{process_name}:{self.received_nfc.nfc_previous_process[process_name]}"
        #     for process_name in FUNCTION_PREVIOUS_PROCESS
        #     if process_name in self.received_nfc.nfc_previous_process
        # )
        #
        # msg.append(f"{FUNCTION_PROCESS}:{self.grade}")
        # self.received_nfc.write(','.join(msg).encode())

    def start_file_observe(self):
        if self.start_grade_file_observe() and self.start_summary_file_observe():
            self.status_update_signal.emit(self.status_label, 'Wait Result...', WHITE)
        else:
            self.status_update_signal.emit(self.status_label, 'Click Right and Set File Path!!', RED)

    def start_grade_file_observe(self):
        if os.path.isdir(grade_path := get_config_audio_bus(GRADE_FILE_PATH)):
            if self.grade_file_observer.is_alive():
                self.grade_file_observer.observer.stop()
            self.grade_file_observer = Target(grade_path, self.grade_signal)
            self.grade_file_observer.start()
            return True
        return False

    def start_summary_file_observe(self):
        if os.path.isdir(summary_path := get_config_audio_bus(SUMMARY_FILE_PATH)):
            if self.summary_file_observer.is_alive():
                self.summary_file_observer.observer.stop()
            self.summary_file_observer = Target(summary_path, self.summary_signal)
            self.summary_file_observer.start()
            return True
        return False

    def mssql_reconnect(self):
        self.mssql.start_query_thread(self.mssql.get_mssql_conn)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            self.audio_bus_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.mssql_config_window.show_modal()

    def closeEvent(self, e):
        for nfc in self.nfc.values():
            nfc.is_open_close()
        # self.grade_file_observer.observer.stop()
        # self.summary_file_observer.observer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioBus(app)
    sys.exit(app.exec_())
