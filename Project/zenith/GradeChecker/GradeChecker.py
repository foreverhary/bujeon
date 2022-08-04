import logging
import sys
import time
from threading import Thread, Timer

import pymcprotocol as pm
from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QVBoxLayout, QMenu

from NFCForGradeChecker import NFCComponentGradeChecker
from PLCDialog import PLCDialog
from process_package.component.CustomComponent import Widget, style_sheet_setting, window_center
from process_package.component.CustomMixComponent import GroupLabel
from process_package.models.BasicModel import BasicModel
from process_package.resource.string import STR_NFC, STR_DATA_MATRIX, STR_GRADE, grade_colors, STR_A, STR_B, STR_C, \
    MSSQL_IP, MSSQL_PORT, STR_STATUS
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_mssql


class GradeChecker(QApplication):
    def __init__(self, sys_argv):
        super(GradeChecker, self).__init__(sys_argv)
        self._model = GradeCheckerModel()
        self._control = GradeCheckerControl(self._model)
        self._view = GradeCheckerView(self._model, self._control)
        self.load_nfc_window = SplashScreen('Grade Checker')
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


class GradeCheckerControl(QObject):
    def __init__(self, model):
        super(GradeCheckerControl, self).__init__()
        self._model = model
        self.pymc = pm.Type3E()
        self.pymc.setaccessopt(commtype='binary')
        self.plc_thread = Thread(target=self.plc_process, daemon=True)
        self.plc_thread.start()

    def start_timer(self, func):
        timer = Timer(0.1, func)
        timer.daemon = True
        timer.start()

    def read_process(self):
        if self.read_plc('B20', 1)[0]:
            try:
                self.write_plc('B21', [1])
                self.write_plc('B22', [1])
                self.write_plc(f'B2{self._model.grade}', [1])
            except Exception as e:
                logger.error(e)
            self.start_timer(self.end_process)
        else:
            self.start_timer(self.read_process)

    def end_process(self):
        if self.read_plc('B23', 1)[0]:
            try:
                self.write_plc('B21', [0])
                self.write_plc('B22', [0])
                self.write_plc(f'B2{self._model.grade}', [0])
                self._model.grade = ''
            except Exception as e:
                logger.error(e)
            self.start_timer(self.plc_process)
        else:
            self.start_timer(self.end_process)

    def plc_process(self):
        if self._model.grade:
            self.start_timer(self.read_process)
        else:
            self.start_timer(self.plc_process)

    def read_plc(self, addr, size):
        try:
            self.pymc.connect(get_config_mssql(MSSQL_IP), int(get_config_mssql(MSSQL_PORT)))
            return_value = self.pymc.batchread_bitunits(headdevice=addr, readsize=size)
            self.pymc.close()
            self._model.status = f"read : {addr}"
        except TimeoutError:
            return_value = None
        return return_value

    def write_plc(self, addr, value):
        try:
            self.pymc.connect(get_config_mssql(MSSQL_IP), int(get_config_mssql(MSSQL_PORT)))
            self.pymc.batchwrite_bitunits(headdevice=addr, values=value)
            self.pymc.close()
            self._model.status = f"write : {addr}, {value}"
            return True
        except TimeoutError:
            return False

    @Slot(dict)
    def receive_nfc_data(self, value):
        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if not (grade := value.get(STR_GRADE)):
            return

        self._model.data_matrix = data_matrix
        self._model.grade = grade
        logger.debug(value)


class GradeCheckerModel(BasicModel):
    nfc_set_port = Signal(str)
    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        self._grade = value
        self.grade_changed.emit(value)
        if value in [STR_A, STR_B, STR_C]:
            self.grade_color_changed.emit(grade_colors[value])

    @property
    def nfc(self):
        return self._nfc

    @nfc.setter
    def nfc(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logging.debug(f"{port}:{nfc}")
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_set_port.emit(port)
                break

    def __init__(self):
        super(GradeCheckerModel, self).__init__()
        self.data_matrix = ''
        self.grade = ''


class GradeCheckerView(Widget):
    def __init__(self, *args):
        super(GradeCheckerView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponentGradeChecker(STR_NFC))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX))
        layout.addWidget(grade := GroupLabel(title=STR_GRADE))
        layout.addWidget(status := GroupLabel(title=STR_STATUS))

        self.setWindowTitle("Grade Checker v0.1")

        # size
        nfc.setFixedHeight(80)
        data_matrix.setFixedHeight(80)
        grade.setMinimumSize(400, 300)
        grade.label.set_font_size(150)

        # assign
        self.nfc = nfc
        self.data_matrix = data_matrix.label
        self.grade = grade.label
        self.status = status

        # signal from component
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event signals
        self._model.nfc_set_port.connect(self.nfc.set_port)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.grade_changed.connect(self.grade.setText)
        self._model.grade_color_changed.connect(self.grade.set_color)
        self._model.status_changed.connect(self.status.setText)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        plc_action = menu.addAction('PLC IP Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == plc_action:
            PLCDialog()


if __name__ == '__main__':
    app = GradeChecker(sys.argv)
    sys.exit(app.exec_())
    # p = pm.Type3E()
    # p.setaccessopt(commtype='binary')
    # p.connect('127.0.0.1', 1025)
    # p.batchread_bitunits(headdevice='B20', readsize=1)
