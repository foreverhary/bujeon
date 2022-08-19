import csv
import os
import socket
import sys

from PySide2.QtCore import Qt, QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QMenu, QGroupBox
from xlrd import open_workbook

from FunctionConfig2Grade import FunctionConfig2Grade
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, window_right, Widget, get_time
from process_package.component.CustomMixComponent import GroupLabel, NetworkStatusGroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.models.BasicModel import BasicModel
from process_package.observer.FileObserver import Target
from process_package.resource.color import GREEN, WHITE, YELLOW, RED
from process_package.resource.size import FUNCTION_LABEL_MINIMUM_WIDTH, FUNCTION_NFC_FIXED_HEIGHT, \
    FUNCTION_NFC_FONT_SIZE, COMPORT_FIXED_HEIGHT
from process_package.resource.string import STR_FUNCTION, STR_NFC1, STR_NFC2, STR_GRADE, STR_AIR_LEAK, STR_DATA_MATRIX, \
    STR_SPL, STR_THD, STR_IMP, STR_MIC_FRF, STR_RUB_BUZ, \
    STR_HOHD, STR_POLARITY, B_GRADE_MAX, STR_NG, A_GRADE_MAX, STR_B, C_GRADE_MAX, STR_A, C_GRADE_MIN, STR_C, \
    SUMMARY_FILE_PATH, GRADE_FILE_PATH, STR_NETWORK, GRADE_FILE_PATH_2
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_audio_bus
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL

FUNCTION_AUTOMATION_VERSION = f"{STR_FUNCTION} Automation v0.5"


class FunctionAutomation(QApplication):
    def __init__(self, sys_argv):
        super(FunctionAutomation, self).__init__(sys_argv)
        self._model = FunctionAutomationModel()
        self._control = FunctionAutomationControl(self._model)
        self._view = FunctionAutomationView(self._model, self._control)
        self._view.setWindowTitle(FUNCTION_AUTOMATION_VERSION)
        self.load_nfc_window = SplashScreen(STR_FUNCTION)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfc(nfcs)
        self._view.start_file_observe()
        self._view.show()
        # self._control.begin()
        window_right(self._view)
        self.load_nfc_window.close()
        self.update_db = UpdateDB()


class FunctionAutomationView(Widget):
    def __init__(self, *args):
        super(FunctionAutomationView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(network := NetworkStatusGroupLabel(STR_NETWORK))
        layout.addLayout(channel_layout := QHBoxLayout())
        channel_layout.addWidget(channel1 := FunctionAutomationChannel('LEFT'))
        channel_layout.addWidget(channel2 := FunctionAutomationChannel('RIGHT'))

        network.setFixedHeight(COMPORT_FIXED_HEIGHT)
        self.channel1 = channel1
        self.channel2 = channel2

        # connect widgets to controller

        # listen for model event signals

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def start_file_observe(self):
        self.channel1.start_file_observe()
        self.channel2.start_file_observe()

    def set_nfc(self, value):
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if nfc == STR_NFC1:
                self.channel1.nfc.set_port(port)
            if nfc == STR_NFC2:
                self.channel2.nfc.set_port(port)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        file_action = menu.addAction('Function File Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == file_action:
            FunctionConfig2Grade(self)
            # FunctionConfig(self)
        if action == db_action:
            MSSqlDialog()


class FunctionAutomationControl(QObject):
    pass
    #


class FunctionAutomationModel(BasicModel):
    pass


class FunctionAutomationChannel(QGroupBox):
    grade_signal = Signal(str)
    summary_signal = Signal(str)

    def __init__(self, title=''):
        super(FunctionAutomationChannel, self).__init__()

        self.grade_file_path_option = GRADE_FILE_PATH if title == 'LEFT' else GRADE_FILE_PATH_2

        self._model = FunctionAutomationChannelModel()

        self.setTitle(title)

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(STR_NFC1))
        layout.addWidget(grade := GroupLabel(STR_GRADE))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX))

        nfc.label.set_font_size(FUNCTION_NFC_FONT_SIZE)

        nfc.setFixedHeight(FUNCTION_NFC_FIXED_HEIGHT)
        data_matrix.setMinimumWidth(FUNCTION_LABEL_MINIMUM_WIDTH // 2)

        self.nfc = nfc
        self.grade_label = grade.label
        self.data_matrix_label = data_matrix

        nfc.nfc_data_out.connect(self.receive_nfc_data)

        self._model.grade_changed.connect(self.grade_label.setText)
        self._model.grade_color_changed.connect(self.grade_label.set_color)
        self._model.data_matrix_changed.connect(self.data_matrix_label.setText)

        self._mssql = MSSQL(STR_AIR_LEAK)
        self.grade_file_observer = Target(signal=self.grade_signal)
        self.summary_file_observer = Target(signal=self.summary_signal)

        self.grade_signal.connect(self.grade_process)
        self.summary_signal.connect(self.summary_process)
        self.delay_write_count = 0

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

        if (grade := value.get(STR_GRADE)) != self._model.grade:
            self.sender().write(f"{data_matrix},{self._model.grade}")
            self.delay_write_count = 3
        else:
            self._model.data_matrix = data_matrix

    def sql_update(self):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       self._model.data_matrix,
                                       get_time(),
                                       self._model.machine_result,
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
        if not self._model.grade:
            return
        try:
            if self.summary_file_path == file_path:
                return
            self.summary_file_path = file_path
            sheet = open_workbook(file_path).sheet_by_name('Summary')
            self.parse_and_check_result(sheet)
            self.sql_update()
            if self._model.data_matrix:
                self._model.grade = ''
                self._model.data_matrix = ''
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
        self._model.machine_result = STR_NG if False in self._model.error_code_result.values() else self._model.grade

    def start_file_observe(self):
        if self.start_grade_file_observe() \
                and self.start_summary_file_observe():
            self._model.status = 'Wait Result...'
        else:
            self._model.status = 'Click Right and Set File Path!!'
            self._model.status_color = RED

    def start_grade_file_observe(self):
        if os.path.isdir(grade_path := get_config_audio_bus(self.grade_file_path_option)):
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


class FunctionAutomationChannelModel(BasicModel):
    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

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
        super(FunctionAutomationChannelModel, self).__init__()
        self.init_result()

    @property
    def grade(self):
        if not hasattr(self, '_grade'):
            self._grade = ''
        return self._grade

    @grade.setter
    def grade(self, value):
        if isinstance(value, float):
            if float(get_config_audio_bus(B_GRADE_MAX)) < value:
                self._grade = STR_NG
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
                self._grade = STR_NG
            self.grade_changed.emit(f"{self._grade} : {value:.2f}")
            self.grade_color_changed.emit(color)
        elif isinstance(value, str):
            self._grade = value
            self.grade_changed.emit(value)
            self.grade_color = RED

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_result(self):
        self.error_code_result = {name: True for name in self.error_code}


if __name__ == '__main__':
    logger.debug('function start')
    app = FunctionAutomation(sys.argv)
    sys.exit(app.exec_())
