import socket
import sys

from PySide2.QtCore import QObject, Qt, Slot, Signal
from PySide2.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, Widget, get_time
from process_package.resource.color import LIGHT_SKY_BLUE, WHITE, YELLOW
from process_package.resource.string import STR_MIC, STR_NFC1, STR_NFC2, STR_SEN, \
    STR_DATA_MATRIX, STR_AIR, STR_OK, STR_FUN, PROCESS_OK_RESULTS, STR_A, STR_B, STR_C, STR_NG, STR_SENSOR
from process_package.screen.NGScreen import NGScreen
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL
from sensor_function.SensorChannel import SensorChannel, SensorChannelModel, SensorChannelControl

TITLE = 'IR SENSOR Automation v0.2'


class SensorChannelAutomationControl(SensorChannelControl):
    def __init__(self, model):
        super(SensorChannelAutomationControl, self).__init__(model)

    @Slot(str)
    def input_serial_data(self, value):
        value = value.upper()
        if value[:2] not in ['L,', 'R,']:
            return
        # split_list = value.split(',')
        split_list = [item for item in value.split(',') if item]
        if len(split_list) < 2:
            return

        for item in split_list[1:]:
            if item not in [STR_OK, STR_NG]:
                return

        self._model.init_result()
        split_list = split_list[1:-1]
        for item, key in zip(split_list, self._model.error_code_result):
            self._model.error_code_result[key] = item == STR_OK
        if False in self._model.error_code_result.values():
            self._model.machine_result = STR_NG
        else:
            self._model.machine_result = STR_OK

        self.sql_update()

    def sql_update(self):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       self._model.data_matrix,
                                       get_time(),
                                       self._model.machine_result,
                                       STR_SENSOR,
                                       self._model.get_error_code(),
                                       socket.gethostbyname(socket.gethostname()))

    @Slot(dict)
    def receive_nfc_data(self, value):
        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if data_matrix == self._model.data_matrix:
            return

        self._model.data_matrix = data_matrix
        self._model.machine_result = ''


class SensorChannelAutomationModel(SensorChannelModel):
    pass


class SensorAutomationView(Widget):
    def __init__(self, *args):
        super(SensorAutomationView, self).__init__()
        self._model, self._control = args
        layout = QVBoxLayout(self)

        layout.addLayout(process_layout := QHBoxLayout())
        process_layout.addWidget(channel1 := SensorChannelAutomation(1))
        process_layout.addWidget(channel2 := SensorChannelAutomation(2))

        # size

        # assign

        self.channel1 = channel1
        self.channel2 = channel2

        # component connect

        # listen for model event signals

        self.setMinimumWidth(640)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # | Qt.FramelessWindowHint)

    def set_nfcs(self, nfcs):
        nfc_ports = []
        for port, nfc_name in nfcs.items():
            # if STR_NFCIN in nfc_name:
            #     nfc_ports.append(port)
            #     self.nfcin.set_port(port)
            if nfc_name == STR_NFC1:
                self.channel1.set_port(port)
                nfc_ports.append(port)
            elif nfc_name == STR_NFC2:
                self.channel2.set_port(port)
                nfc_ports.append(port)
        self.channel1.exclude_nfc_ports(nfc_ports)
        self.channel2.exclude_nfc_ports(nfc_ports)

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


class SensorChannelAutomation(SensorChannel):
    def __init__(self, channel):
        super(SensorChannelAutomation, self).__init__(channel)
        self._model = SensorChannelAutomationModel()
        self._control = SensorChannelAutomationControl(self._model)

        # view connect control
        self.comport.comport_save.connect(self._control.comport_save)
        self.comport.serial_output_data.connect(self._control.input_serial_data)
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # control connect view
        self._control.nfc_write.connect(self.nfc.write)

        # model connect view
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.machine_result_changed.connect(self.result.setText)


class SensorAutomationControl(QObject):

    def __init__(self, model):
        super(SensorAutomationControl, self).__init__()
        self._model = model
        self._mssql = MSSQL(STR_SEN)

        self.process_name = STR_SEN

        self.ng_screen_opened = False
        self.update_db = UpdateDB()

    def mid_clicked(self):
        pass

    def begin(self):
        pass


class SensorAutomation(QApplication):
    def __init__(self, sys_argv):
        super(SensorAutomation, self).__init__(sys_argv)
        self._model = SensorAutomationModel()
        self._control = SensorAutomationControl(self._model)
        self._view = SensorAutomationView(self._model, self._control)
        self._view.setWindowTitle(TITLE)
        self.load_nfc_window = SplashScreen("Sensor Process")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._view.set_nfcs(nfcs)
        self._control.begin()
        self._view.begin()
        self._view.show()
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = SensorAutomation(sys.argv)
    sys.exit(app.exec_())
