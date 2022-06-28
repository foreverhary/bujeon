import sys

from PySide2.QtCore import QObject, Qt, QTimer, Slot, Signal
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMenu

from process_package.Views.CustomComponent import style_sheet_setting, Widget
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.controllers.MSSqlDialog import MSSqlDialog
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.number import CHECK_DB_UPDATE_TIME
from process_package.resource.string import STR_MIC, STR_NFC1, STR_NFC2, STR_NFCIN, STR_PREVIOUS_PROCESS, STR_SEN, \
    STR_DATA_MATRIX, STR_AIR, STR_OK, STR_FUN, PROCESS_OK_RESULTS
from process_package.screen.NGScreen import NGScreen
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL
from sensor_function.SensorChannel import SensorChannel


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
        self._mssql = MSSQL(STR_SEN)

        self.ng_screen_opened = False
        self.db_update_timer = QTimer(self)
        self.db_update_timer.start(CHECK_DB_UPDATE_TIME)
        self.db_update_timer.timeout.connect(self.update_db)

    @Slot(dict)
    def check_previous(self, value):
        if self.ng_screen_opened:
            return
        if (data_matrix := value.get(STR_DATA_MATRIX)) \
                and (value.get(STR_AIR) == STR_OK) \
                and (value.get(STR_MIC) == STR_OK) \
                and (value.get(STR_FUN) in PROCESS_OK_RESULTS):
            self._model.previous = data_matrix
        else:
            self.previous = value
            self.ng_screen_opened = True
            NGScreen(self)

    def mid_clicked(self):
        pass

    def update_db(self):
        UpdateDB()

    def begin(self):
        self._mssql.timer_for_db_connect()


class SensorProcessView(Widget):
    def __init__(self, *args):
        super(SensorProcessView, self).__init__()
        self._model, self._control = args
        layout = QVBoxLayout(self)
        layout.addLayout(previous_layout := QVBoxLayout())
        previous_layout.addWidget(nfc_in := NFCComponent(STR_NFCIN))
        previous_layout.addWidget(previous := GroupLabel(title=STR_PREVIOUS_PROCESS, is_clean=True, clean_time=3000))
        layout.addLayout(process_layout := QHBoxLayout())
        process_layout.addWidget(channel1 := SensorChannel(1))
        process_layout.addWidget(channel2 := SensorChannel(2))

        # size
        nfc_in.setFixedHeight(80)
        previous.set_font_size(80)

        # assign
        self.nfcin = nfc_in
        self.previous = previous.label

        self.channel1 = channel1
        self.channel2 = channel2

        # component connect
        self.nfcin.nfc_data_out.connect(self._control.check_previous)

        # listen for model event signals
        self._model.previous_changed.connect(self.previous.setText)
        self._model.previous_color_changed.connect(self.previous.set_background_color)

        self.setWindowTitle('IR SENSOR')
        self.setMinimumWidth(640)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)

    def set_nfcs(self, nfcs):
        for port, nfc_name in nfcs.items():
            if STR_NFCIN in nfc_name:
                self.nfcin.set_port(port)
            elif nfc_name == STR_NFC1:
                self.channel1.set_port(port)
            elif nfc_name == STR_NFC2:
                self.channel2.set_port(port)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()


class SensorProcessModel(QObject):
    previous_changed = Signal(str)
    previous_color_changed = Signal(str)

    def __init__(self):
        super(SensorProcessModel, self).__init__()

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value
        self.previous_changed.emit(value)
        self.previous_color_changed.emit(LIGHT_SKY_BLUE)

    def begin(self):
        pass


if __name__ == '__main__':
    app = SensorProcess(sys.argv)
    sys.exit(app.exec_())
