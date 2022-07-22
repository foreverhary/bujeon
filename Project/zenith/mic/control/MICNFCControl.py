import csv
import os

from PySide2.QtCore import QObject, Signal

from process_package.observer.FileObserver import Target
from process_package.resource.string import STR_MIC, CONFIG_FILE_NAME, MIC_SECTION, FILE_PATH, STR_OK, STR_PASS, STR_NG
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_value
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class MICNFCControl(QObject):
    file_path_signal = Signal(str)

    nfc1_result_changed = Signal(str)
    nfc1_error_result_changed = Signal(dict)
    nfc2_result_changed = Signal(str)
    nfc2_error_result_changed = Signal(dict)

    def __init__(self):
        super(MICNFCControl, self).__init__()
        self._mssql = MSSQL(STR_MIC)
        self.update_db = UpdateDB()
        self.result_file_observer = Target(signal=self.file_path_signal)
        self.file_path_signal.connect(self.receive_file_name)
        self.start_file_observe()
        self.side, self.error, self.result = None, None, None

    def start_file_observe(self):
        if not os.path.isdir(path := get_config_value(MIC_SECTION, FILE_PATH)):
            return False

        if self.__getattribute__("result_file_observer") and self.result_file_observer.is_alive():
            self.result_file_observer.observer.stop()
        self.result_file_observer = Target(path, self.file_path_signal)
        self.result_file_observer.start()
        return True

    def receive_file_name(self, value):
        logger.debug(value)
        try:
            with open(value) as f:
                csv_lines = list(csv.reader(f))
            csv_line_index = -1
            fill_line_num = 0
            lines = []
            while fill_line_num < 2:
                if line := csv_lines[csv_line_index]:
                    lines.append(iter(line))
                    fill_line_num += 1
                csv_line_index -= 1
        except IndexError:
            return
        error = {}
        for first, second in zip(*lines):
            if first == second:
                if 'CH' in first:
                    channel = tuple(map(next, lines))
                    if '1' in channel and '2' in channel:
                        side = 'L'
                    elif '3' in channel and '4' in channel:
                        side = 'R'

                if 'FRF' in first or 'SENS' in first or 'CURRENT' in first:
                    [tuple(map(next, lines)) for _ in range(3)]
                    error_result_set = set(map(next, lines))
                    error[first] = len(error_result_set) == 1 and error_result_set.pop() == STR_OK
                if 'Pass/Fail' in first:
                    result_set = set(map(next, lines))
                    if len(result_set) == 1 and result_set.pop() == STR_PASS:
                        result = STR_OK
                    else:
                        result = STR_NG
        if self.side == side and self.error == error and self.result == result:
            return
        self.side, self.error, self.result = side, error, result
        if side == 'L':
            self.nfc1_error_result_changed.emit(error)
            self.nfc1_result_changed.emit(result)
        elif side == 'R':
            self.nfc2_error_result_changed.emit(error)
            self.nfc2_result_changed.emit(result)
