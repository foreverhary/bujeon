import csv
import os
import sys

from PySide2.QtCore import QObject, Signal, Qt
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout

from audio_bus.observer.FileObserver import Target
from mic.MICNFCReader import MICNFCReader
from mic.MICNFCWriter import MICNFCWriter
from mic.MICNFConfig import MICNFCConfig
from process_package.Views.CustomComponent import style_sheet_setting, Widget
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.string import STR_OK, STR_MIC, STR_NFC1, STR_NFC2, MIC_SECTION, FILE_PATH, STR_PASS, \
    STR_NG, CONFIG_FILE_NAME, STR_NFCIN, STR_NFCIN1
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger
from process_package.tools.Config import get_config_value
from process_package.tools.mssql_connect import MSSQL


class SensorProcess(QApplication):
    def __init__(self, sys_argv):
        super(SensorProcess, self).__init__(sys_argv)
        self._model = SensorProcessModel()
        self._control = SensorProcessControl(self._model)
        self._view = SensorProcessView(self._model, self._control)
        self._control.begin()
        self.load_nfc_window = SplashScreen("Sensor Process")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._view.show()
        self.load_nfc_window.close()


class SensorProcessControl(QObject):

    def __init__(self, model):
        super(SensorProcessControl, self).__init__()
        self._model = model
        self._mssql = MSSQL(STR_MIC)

    def right_clicked(self):
        MSSqlDialog()

    def mid_clicked():
        pass

    def begin(self):
        self._mssql.timer_for_db_connect()


class SensorProcessView(Widget):
    def __init__(self, *args):
        super(SensorProcessView, self).__init__()
        self._model, self._control = args
        layout = QVBoxLayout(self)
        layout.addLayout(process_layout := QHBoxLayout())
        layout.addWidget()

        self.setWindowTitle('IR SENSOR')
        self.setMinimumWidth(640)

        # assign


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

    def mousePressEvent(self, e):
        super().mousePressEvent(e)


class SensorProcessModel(QObject):
    def __init__(self):
        super(SensorProcessModel, self).__init__()
        self.error_code_nfc1_result = {}
        self.error_code_nfc2_result = {}

    def begin(self):
        pass


if __name__ == '__main__':
    app = SensorProcess(sys.argv)
    sys.exit(app.exec_())
