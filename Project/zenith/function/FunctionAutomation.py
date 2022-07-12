import csv
import os
import socket
import sys

from PySide2.QtCore import Qt, QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QMenu
from xlrd import open_workbook

from function.FunctionConfig import FunctionConfig
from function.model.NFCModel import NFCModel
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, window_right, Widget, get_time
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.models.ConfigModel import ConfigModel
from process_package.observer.FileObserver import Target
from process_package.resource.color import LIGHT_SKY_BLUE, GREEN, WHITE, YELLOW, RED
from process_package.resource.size import AUDIO_BUS_LABEL_MINIMUM_WIDTH, AUDIO_BUS_NFC_FIXED_HEIGHT, \
    AUDIO_BUS_NFC_FONT_SIZE
from process_package.resource.string import STR_FUNCTION, STR_NFC1, STR_NFC2, STR_GRADE, STR_WRITE_STATUS, STR_STATUS, \
    STR_AIR_LEAK, STR_FUN, STR_DATA_MATRIX, STR_SPL, STR_THD, STR_IMP, STR_MIC_FRF, STR_RUB_BUZ, \
    STR_HOHD, STR_POLARITY, B_GRADE_MAX, STR_NG, A_GRADE_MAX, STR_B, C_GRADE_MAX, STR_A, C_GRADE_MIN, STR_C, \
    STR_WRITE_DONE, SUMMARY_FILE_PATH, GRADE_FILE_PATH
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_audio_bus
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class FunctionAutomation(QApplication):
    def __init__(self, sys_argv):
        super(FunctionAutomation, self).__init__(sys_argv)
        self._model = FunctionAutomationModel()
        self._control = FunctionAutomationControl(self._model)
        self._view = FunctionAutomationView(self._model, self._control)
        self._model.begin_config_read()
        self.load_nfc_window = SplashScreen(STR_FUNCTION)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._view.show()
        self._control.begin()
        window_right(self._view)
        self.load_nfc_window.close()


class FunctionAutomationView(Widget):
    def __init__(self, *args):
        super(FunctionAutomationView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(nfc_layout := QHBoxLayout())
        nfc_layout.addWidget(nfc1 := NFCComponent(STR_NFC1))
        nfc_layout.addWidget(nfc2 := NFCComponent(STR_NFC2))
        layout.addWidget(grade := GroupLabel(STR_GRADE))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX, is_nfc=True))

        nfc1.setFixedHeight(AUDIO_BUS_NFC_FIXED_HEIGHT)
        nfc1.label.set_font_size(AUDIO_BUS_NFC_FONT_SIZE)
        nfc2.setFixedHeight(AUDIO_BUS_NFC_FIXED_HEIGHT)
        nfc2.label.set_font_size(AUDIO_BUS_NFC_FONT_SIZE)
        data_matrix.setMinimumWidth(AUDIO_BUS_LABEL_MINIMUM_WIDTH)

        self.grade = grade.label
        self.data_matrix = data_matrix.label

        self.setWindowTitle(f"{STR_FUNCTION} Automation v.0.1")

        # connect widgets to controller

        # listen for component event signals
        nfc1.nfc_data_out.connect(self._control.receive_nfc_data)
        nfc2.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for control event signals
        self._control.nfc1_write.connect(nfc1.write)
        self._control.nfc2_write.connect(nfc2.write)

        # listen for model event signals
        self._model.nfc1.nfc_changed.connect(nfc1.set_port)
        self._model.nfc2.nfc_changed.connect(nfc2.set_port)

        self._model.grade_changed.connect(self.grade.setText)
        self._model.grade_color_changed.connect(self.grade.set_color)

        self._model.data_matrix_changed.connect(self.data_matrix.setText)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        file_action = menu.addAction('Function File Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == file_action:
            FunctionConfig(self._model, self._control)
        if action == db_action:
            MSSqlDialog()


class FunctionAutomationControl(QObject):
    nfc_in_write = Signal(str)
    nfc1_write = Signal(str)
    nfc2_write = Signal(str)
    grade_signal = Signal(str)
    summary_signal = Signal(str)

    def __init__(self, model):
        super(FunctionAutomationControl, self).__init__()
        self._model = model

        self._mssql = MSSQL(STR_AIR_LEAK)
        self.update_db = UpdateDB()

        # controller event connect

        self.delay_write_count = 0
        self.ng_screen_opened = False
        self.process_name = STR_FUN
        self.previous = {}

        # file observer
        self.grade_file_observer = Target(signal=self.grade_signal)
        self.summary_file_observer = Target(signal=self.summary_signal)

        self.grade_signal.connect(self.grade_process)
        self.summary_signal.connect(self.summary_process)

        self.data_matrix = None

    @Slot(dict)
    def receive_nfc_data(self, value):

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if data_matrix == self._model.data_matrix:
            return

        if not self._model.grade:
            return

        if not (grade := value.get(STR_GRADE)):
            self.nfc1_write.emit(f"{data_matrix},{self._model.grade}")
            self.nfc2_write.emit(f"{data_matrix},{self._model.grade}")
            self.delay_write_count = 3
        else:
            self._model.data_matrix = data_matrix

    def sql_update(self):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       self._model.data_matrix,
                                       get_time(),
                                       self._model.result,
                                       STR_FUNCTION,
                                       self._model.get_error_code(),
                                       socket.gethostbyname(socket.gethostname()))

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
            self.summary_file_path = None
        except Exception as e:
            logger.error(e)

    @Slot(str)
    def summary_process(self, file_path):
        logger.debug(file_path)
        try:
            if self.summary_file_path == file_path:
                return
            self.summary_file_path = file_path
            self._model.status = 'Read Result...'
            sheet = open_workbook(file_path).sheet_by_name('Summary')
            self.parse_and_check_result(sheet)
            self.sql_update()
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
        self._model.init_result()
        for name, result_value in result.items():
            for key in self._model.error_code_result:
                if key in name and 'Failed' in result_value:
                    self._model.error_code_result[key] = False
        self._model.result = self._model.grade
        self._model.result = STR_NG if False in self._model.error_code_result.values() else self._model.grade

    def start_file_observe(self):
        if self.start_grade_file_observe() and self.start_summary_file_observe():
            self._model.status = 'Wait Result...'
        else:
            self._model.status = 'Click Right and Set File Path!!'
            self._model.status_color = RED

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
        self.start_file_observe()
        self._mssql.timer_for_db_connect()

    def right_clicked(self):
        FunctionConfig(self._model)

    def mid_clicked(self):
        MSSqlDialog()


class FunctionAutomationModel(ConfigModel):
    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

    data_matrix_changed = Signal(str)

    error_code = {
        STR_SPL: 1,
        STR_THD: 2,
        STR_IMP: 3,
        STR_MIC_FRF: 4,
        STR_RUB_BUZ: 5,
        STR_HOHD: 6,
        STR_POLARITY: 7,
    }

    def __init__(self):
        super(FunctionAutomationModel, self).__init__()
        self.nfc1 = NFCModel()
        self.nfc2 = NFCModel()
        self.data_matrix = ''
        self.result = ''
        self.error_code_result = {}

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if isinstance(value, float):
            if float(get_config_audio_bus(B_GRADE_MAX)) < value:
                self._grade = ''
            elif float(get_config_audio_bus(A_GRADE_MAX)) < value:
                self._grade = STR_B
                color = GREEN
            elif float(get_config_audio_bus(C_GRADE_MAX)) < value:
                self._grade = STR_A
                color = WHITE
            elif float(get_config_audio_bus(C_GRADE_MIN)) <= value:
                self._grade = STR_C
                color = YELLOW
            else:
                self._grade = ''
            self.grade_changed.emit(f"{self._grade} : {value:.2f}")
            self.grade_color = color
        elif isinstance(value, str):
            self._grade = value

    @property
    def grade_color(self):
        return self._grade_color

    @grade_color.setter
    def grade_color(self, value):
        self._grade_color = value
        self.grade_color_changed.emit(value)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self.grade = ''
        self._result = value

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(value)

    @property
    def nfcs(self):
        return self._nfcs

    @nfcs.setter
    def nfcs(self, value):
        if not isinstance(value, dict):
            return
        self._nfcs = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if nfc == STR_NFC1:
                self.nfc1.nfc_changed.emit(port)
            if nfc == STR_NFC2:
                self.nfc2.nfc_changed.emit(port)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}

    def begin_config_read(self):
        self.init_result()


if __name__ == '__main__':
    logger.debug('function start')
    app = FunctionAutomation(sys.argv)
    sys.exit(app.exec_())
