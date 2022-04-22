import os.path
import sys

import pandas as pd
import pymssql
from PyQt5.QtCore import Qt, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QApplication

from AudioBusUI import AudioBusUI
from FileObserver import Target
from process_package.Config import get_config_audio_bus
from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, window_right, logger, NFC_IN, \
    FUNCTION_PREPROCESS, NFC, LIGHT_SKY_BLUE, RED, GRADE_FILE_PATH, WHITE, SUMMARY_FILE_PATH, A, B, C, C_GRADE_MIN, \
    C_GRADE_MAX, B_GRADE_MAX, A_GRADE_MAX, NG, \
    FUNCTION_PROCESS, SPL, THD, IMP, MIC_FRF, RUB_BUZ, POLARITY, FUNCTION, HOHD, AUD
from process_package.mssql_connect import get_process_error_code_dict, insert_pprd

NFC_IN_COUNT = 1
NFC_OUT_COUNT = 2


class AudioBus(AudioBusUI):
    status_update_signal = pyqtSignal(object, str, str)
    grade_signal = pyqtSignal(str)
    summary_signal = pyqtSignal(str)
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

        # variable
        self.nfc = {}
        self.grade = ''
        self.grade_file_observer = Target(signal=self.grade_signal)
        self.summary_file_observer = Target(signal=self.summary_signal)
        try:
            self.error_code = get_process_error_code_dict(FUNCTION)
        except pymssql.OperationalError:
            pass
        self.result = {name: True for name in self.error_code}
        logger.debug(self.result)

        # NFC Auto connect
        self.load_window = SplashScreen("Audio Bus")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        if self.init_signal_event_and_serial(nfc_list):
            self.start_file_observe()
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
            if float(get_config_audio_bus(B_GRADE_MAX)) < value:
                self._grade = NG
            elif float(get_config_audio_bus(A_GRADE_MAX)) < value:
                self._grade = B
            elif float(get_config_audio_bus(C_GRADE_MAX)) < value:
                self._grade = A
            elif float(get_config_audio_bus(C_GRADE_MIN)) <= value:
                self._grade = C
            else:
                self._grade = NG
            self.status_update_signal.emit(self.grade_label, f"{self._grade} : {value:.2f}", WHITE)
        elif isinstance(value, str):
            self._grade = value
        else:
            self._grade = NG
        logger.debug(self._grade)

    @pyqtSlot(object)
    def update_sql(self, nfc):
        try:
            insert_pprd(dm=nfc.dm, result=self.grade, pcode=FUNCTION, ecode=self.get_ecode(), keyword=AUD)
        except Exception as e:
            logger.error(e)
        self.status_update_signal.emit(self.status_label, f"{nfc.dm} is Write Done", LIGHT_SKY_BLUE)
        self.init_result_true()

    def get_ecode(self):
        return ','.join([
                self.error_code[key] for key, value in self.result.items() if not value
            ])

    def init_result_true(self):
        self.result = {key: True for key in self.result}

    def init_signal_event_and_serial(self, nfc_list):
        self.audio_bus_config_window.close_signal.connect(self.start_file_observe)
        self.status_update_signal.connect(self.update_label)
        self.grade_signal.connect(self.grade_process)
        self.summary_signal.connect(self.summary_process)

        nfc_in_count = nfc_out_count = 0
        for nfc in nfc_list:
            nfc.previous_process_list = FUNCTION_PREPROCESS
            if NFC_IN in nfc.serial_name and int(nfc.serial_name[-1]) < NFC_IN_COUNT + 1:
                self.nfc[nfc.serial_name] = nfc
                nfc.signal.previous_process_signal.connect(self.previous_process_receive)
                nfc.signal.serial_error_signal.connect(self.serial_error_receive)
                nfc.start_previous_process_check_thread()
                nfc_in_count += 1
            elif NFC in nfc.serial_name and int(nfc.serial_name[-1]) < NFC_OUT_COUNT + 1:
                self.nfc[nfc.serial_name] = nfc
                nfc.signal.nfc_write_done_signal.connect(self.update_sql)
                nfc_out_count += 1
            else:
                nfc.close()

        if (nfc_in_count, nfc_out_count) == (NFC_IN_COUNT, NFC_OUT_COUNT):
            self.status_update_signal.emit(self.status_label, "READY NFC", LIGHT_SKY_BLUE)
        else:
            self.status_update_signal.emit(self.status_label, "CHECK NFC & RESTART PROGRAM!!", RED)
        return (nfc_in_count, nfc_out_count) == (NFC_IN_COUNT, NFC_OUT_COUNT)

    @pyqtSlot(str)
    def serial_error_receive(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    @pyqtSlot(tuple)
    def previous_process_receive(self, info):
        serial_name, msg, color = info
        self.status_update_signal.emit(self.previous_process_label, msg, color)

    @pyqtSlot(object, str, str)
    def update_label(self, label, text, color):
        label.setText(text)
        label.set_text_property(color=color)

    @pyqtSlot(str)
    def grade_process(self, file_path):
        try:
            logger.debug(file_path)
            df = pd.read_csv(file_path)
            self.grade = float(df.iloc[2][1])
            self.status_update_signal.emit(self.status_label, 'Reading Grade File...', WHITE)
        except Exception as e:
            logger.error(e)

    @pyqtSlot(str)
    def summary_process(self, file_path):
        try:
            logger.debug(file_path)
            self.status_update_signal.emit(self.status_label, 'Read Result...', WHITE)
            df = pd.read_excel(file_path, sheet_name="Summary", engine='xlrd', header=None)
            self.parse_and_check_result(df)
            self.status_update_signal.emit(self.status_label, 'TAG NFC', WHITE)
            for index in range(1, 3):
                self.nfc[f"{NFC}{index}"].start_nfc_write(
                    process_result=f"{FUNCTION_PROCESS}:{self.grade}"
                )
        except ValueError as e:
            logger.error(type(e))
        except Exception as e:
            logger.debug(e)

    def parse_and_check_result(self, df):
        row_iter = df.iterrows()
        result = {}
        for item in row_iter:
            if 'Summary' in item[1][0]:
                next(row_iter)
                data = next(row_iter)
                name = item[1][0].split('Summary:')[1].strip().upper()
                result[name] = (data[1][1], data[1][2])

        for name, result_value in result.items():
            for key in self.result:
                if key in name and 'Failed' in result_value:
                    self.result[key] = False

        # if False in self.result.values():
        #     self.grade = NG

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

    def closeEvent(self, e):
        for nfc in self.nfc.values():
            nfc.is_open_close()
        # self.grade_file_observer.observer.stop()
        # self.summary_file_observer.observer.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AudioBus(app)
    sys.exit(app.exec_())
