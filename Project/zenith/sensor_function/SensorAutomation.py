import sys

from PySide2.QtCore import QObject, Qt, Slot, Signal
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.color import LIGHT_SKY_BLUE, WHITE, YELLOW
from process_package.resource.string import STR_MIC, STR_NFC1, STR_NFC2, STR_NFCIN, STR_PREVIOUS_PROCESS, STR_SEN, \
    STR_DATA_MATRIX, STR_AIR, STR_OK, STR_FUN, PROCESS_OK_RESULTS, STR_GRADE, STR_A, STR_B, STR_C
from process_package.screen.NGScreen import NGScreen
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL
from sensor_function.SensorChannel import SensorChannel


class SensorAutomation(QApplication):
    def __init__(self, sys_argv):
        super(SensorAutomation, self).__init__(sys_argv)
        self._model = SensorAutomationModel()
        self._control = SensorAutomationControl(self._model)
        self._view = SensorAutomationView(self._model, self._control)
        self.load_nfc_window = SplashScreen("Sensor Process")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._control.begin()
        self._view.begin()
        self._view.show()
        self.load_nfc_window.close()


class SensorAutomationControl(QObject):

    def __init__(self, model):
        super(SensorAutomationControl, self).__init__()
        self._model = model
        self._mssql = MSSQL(STR_SEN)

        self.process_name = STR_SEN

        self.ng_screen_opened = False
        self.update_db = UpdateDB()

    @Slot(dict)
    def check_previous(self, value):
        if self.ng_screen_opened:
            return
        if (data_matrix := value.get(STR_DATA_MATRIX)) \
                and (value.get(STR_AIR) == STR_OK) \
                and (value.get(STR_MIC) == STR_OK) \
                and (value.get(STR_FUN) in PROCESS_OK_RESULTS):
            self._model.previous = data_matrix
            self._model.grade = value.get(STR_FUN)
        else:
            self.previous = value
            self.ng_screen_opened = True
            NGScreen(self)

    def mid_clicked(self):
        pass

    # def update_db(self):
    #     UpdateDB()

    def begin(self):
        pass


class SensorAutomationView(Widget):
    def __init__(self, *args):
        super(SensorAutomationView, self).__init__()
        self._model, self._control = args
        layout = QVBoxLayout(self)

        layout.addLayout(process_layout := QHBoxLayout())
        process_layout.addWidget(channel1 := SensorChannel(1))
        process_layout.addWidget(channel2 := SensorChannel(2))

        # size

        # assign

        self.channel1 = channel1
        self.channel2 = channel2

        # component connect

        # listen for model event signals

        self.setWindowTitle('IR SENSOR Automation v0.1')
        self.setMinimumWidth(640)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)

    def set_nfcs(self, nfcs):
        nfc_ports = []
        for port, nfc_name in nfcs.items():
            if STR_NFCIN in nfc_name:
                nfc_ports.append(port)
                self.nfcin.set_port(port)
            elif nfc_name == STR_NFC1:
                self.channel1.set_port(port)
                nfc_ports.append(port)
            elif nfc_name == STR_NFC2:
                self.channel2.set_port(port)
                nfc_ports.append(port)
        self.channel1.nfc_ports(nfc_ports)
        self.channel2.nfc_ports(nfc_ports)

    def begin(self):
        self.channel1.begin()
        self.channel2.begin()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()


class SensorAutomationModel(QObject):
    previous_changed = Signal(str)
    previous_color_changed = Signal(str)

    grade_changed = Signal(str)
    grade_color_changed = Signal(str)

    def __init__(self):
        super(SensorAutomationModel, self).__init__()

    @property
    def previous(self):
        return self._previous

    @previous.setter
    def previous(self, value):
        self._previous = value
        self.previous_changed.emit(value)
        self.previous_color_changed.emit(LIGHT_SKY_BLUE)

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        self._grade = value
        self.grade_changed.emit(value)
        if value == STR_A:
            self.grade_color_changed.emit(WHITE)
        elif value == STR_B:
            self.grade_color_changed.emit('lightgreen')
        elif value == STR_C:
            self.grade_color_changed.emit(YELLOW)

    def begin(self):
        pass


if __name__ == '__main__':
    app = SensorAutomation(sys.argv)
    sys.exit(app.exec_())
