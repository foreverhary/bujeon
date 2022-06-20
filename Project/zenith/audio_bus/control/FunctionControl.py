import csv
import os

from PySide2.QtCore import QObject, Slot, Signal
from xlrd import open_workbook

from audio_bus.FunctionConfig import FunctionConfig
from audio_bus.observer.FileObserver import Target
from process_package.Views.CustomComponent import get_time
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.string import STR_NFC, STR_AIR_LEAK, STR_DATA_MATRIX, STR_AIR, STR_NG, GRADE_FILE_PATH, \
    SUMMARY_FILE_PATH
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.Config import get_config_audio_bus
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.mssql_connect import MSSQL


class FunctionControl(QObject):
    nfc_in_write = Signal(str)
    nfc1_write = Signal(str)
    nfc2_write = Signal(str)
    grade_signal = Signal(str)
    summary_signal = Signal(str)

    def __init__(self, model):
        super(FunctionControl, self).__init__()
        self._model = model

        self._mssql = MSSQL(STR_AIR_LEAK)

        # controller event connect

        self.delay_write_count = 0

        # file observer
        self.grade_file_observer = Target(signal=self.grade_signal)
        self.summary_file_observer = Target(signal=self.summary_signal)

        self.grade_signal.connect(self.grade_process)
        self.summary_signal.connect(self.summary_process)

    @Slot(dict)
    def check_previous(self, value):
        pass

    @Slot(dict)
    def receive_nfc_data(self, value):
        if not self._model.result:
            return

        if value.get(STR_DATA_MATRIX) in self._model.units:
            self._model.unit_blink = self._model.units.index(value[STR_DATA_MATRIX])
            return

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        self._model.unit_color = len(self._model.units)

        if self._model.data_matrix != value.get(STR_DATA_MATRIX) \
                or self._model.result != value.get(STR_AIR):
            self._model.data_matrix = value.get(STR_DATA_MATRIX)
            self.nfc.write(f"{self._model.data_matrix},{STR_AIR}:{self._model.result}")
            self.delay_write_count = 2
        else:
            write_beep()
            self._model.unit_input = self._model.data_matrix
            self._mssql.start_query_thread(self._mssql.insert_pprd,
                                           get_time(),
                                           self._model.data_matrix,
                                           self._model.result)
            self._model.data_matrix = ''

    @Slot(str)
    def grade_process(self, file_path):
        try:
            logger.debug(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                rdr = csv.reader(f)
                for line in rdr:
                    logger.debug(line)
                    if line[0].upper() == "CH1":
                        self._model.grade = float(line[1])
                        break
            self._model.status = "Reading Grade File..."
            self.summary_file_path = None
        except Exception as e:
            logger.error(e)

    @Slot(str)
    def summary_process(self, file_path):
        try:
            if self.summary_file_path == file_path:
                return
            self.summary_file_path = file_path
            self._model.status = 'Read Result...'
            sheet = open_workbook(file_path).sheet_by_name('Summary')
            self.parse_and_check_result(sheet)
            self._model.status = 'NFC TAG'
        except ValueError as e:
            logger.error(type(e))
        except Exception as e:
            logger.debug(e)

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
        self._model.init_result_true()
        for name, result_value in result.items():
            for key in self.result:
                if key in name and 'Failed' in result_value:
                    self._model.error_code_result[key] = False
        self._model.result = STR_NG if False in self._model.error_code_result.values() else self._model.grade

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

    def begin(self):
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        FunctionConfig(self._model)

    def mid_clicked(self):
        MSSqlDialog()
