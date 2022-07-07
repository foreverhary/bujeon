import csv
import os
import sys

from PySide2.QtCore import QObject, Signal, Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QMenu

from mic.MICNFCReader import MICNFCReader
from mic.MICNFCWriter import MICNFCWriter
from mic.MICNFConfig import MICNFCConfig
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget, window_center
from process_package.observer.FileObserver import Target
from process_package.resource.string import STR_OK, STR_MIC, STR_NFC1, STR_NFC2, MIC_SECTION, FILE_PATH, STR_PASS, \
    STR_NG, CONFIG_FILE_NAME, STR_NFCIN, STR_NFCIN1
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_value
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class MICNFC(QApplication):
    def __init__(self, sys_argv):
        super(MICNFC, self).__init__(sys_argv)
        self._model = MICNFCModel()
        self._control = MICNFCControl(self._model)
        self._view = MICNFCView(self._model, self._control)
        self._control.begin()
        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


class MICNFCControl(QObject):
    file_path_signal = Signal(str)

    nfc1_result_changed = Signal(str)
    nfc1_error_result_changed = Signal(dict)
    nfc2_result_changed = Signal(str)
    nfc2_error_result_changed = Signal(dict)

    def __init__(self, model):
        super(MICNFCControl, self).__init__()
        self._model = model
        self._mssql = MSSQL(STR_MIC)

        self.update_db = UpdateDB()

        self.result_file_observer = Target(signal=self.file_path_signal)

        self.file_path_signal.connect(self.receive_file_name)
        self.start_file_observe()
        self.side, self.error, self.result = None, None, None

    def start_file_observe(self):
        if not os.path.isdir(path := get_config_value(CONFIG_FILE_NAME, MIC_SECTION, FILE_PATH)):
            return False

        if self.__getattribute__("result_file_observer") and self.result_file_observer.is_alive():
            self.result_file_observer.observer.stop()
        self.result_file_observer = Target(path, self.file_path_signal)
        self.result_file_observer.start()
        return True

    def receive_file_name(self, value):  # sourcery no-metrics
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

    def mid_clicked(self):
        pass

    def begin(self):
        self._mssql.timer_for_db_connect()


class MICNFCView(Widget):
    def __init__(self, *args):
        super(MICNFCView, self).__init__()
        self._model, self._control = args
        layout = QHBoxLayout(self)
        layout.addWidget(nfc1 := MICNFCWriter(STR_NFC1, self._control._mssql))
        layout.addWidget(nfcin := MICNFCReader(STR_NFCIN))
        layout.addWidget(nfc2 := MICNFCWriter(STR_NFC2, self._control._mssql))
        self.nfc1 = nfc1
        self.nfc2 = nfc2
        self.nfcin = nfcin

        self._control.nfc1_result_changed.connect(nfc1.set_result)
        self._control.nfc1_error_result_changed.connect(nfc1.set_error_code)

        self._control.nfc2_result_changed.connect(nfc2.set_result)
        self._control.nfc2_error_result_changed.connect(nfc2.set_error_code)

        self.setWindowTitle(STR_MIC)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)

    def set_nfcs(self, nfcs):
        for port, nfc_name in nfcs.items():
            if nfc_name == STR_NFC1:
                self.nfc1.set_port(port)
            elif nfc_name == STR_NFC2:
                self.nfc2.set_port(port)
            elif nfc_name == STR_NFCIN1:
                self.nfcin.set_port(port)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        mic_action = menu.addAction('MIC File Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == mic_action:
            MICNFCConfig(self._control)
        elif action == db_action:
            MSSqlDialog()


class MICNFCModel(QObject):
    def __init__(self):
        super(MICNFCModel, self).__init__()
        self.error_code_nfc1_result = {}
        self.error_code_nfc2_result = {}

    def begin(self):
        pass


if __name__ == '__main__':
    app = MICNFC(sys.argv)
    sys.exit(app.exec_())
