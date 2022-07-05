import socket
import sys

from PySide2.QtCore import Signal, Slot, QObject
from PySide2.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QGridLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import style_sheet_setting, window_center, Widget, get_time
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.models.ConfigModel import ConfigModel
from process_package.old.defined_serial_port import get_serial_available_list
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.size import COMPORT_FIXED_HEIGHT, NFC_FIXED_HEIGHT
from process_package.resource.string import STR_AIR_LEAK, CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, STR_NFC, \
    STR_OK, STR_NG, STR_MACHINE_COMPORT, STR_DATA_MATRIX, STR_RESULT, STR_AIR
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger, write_beep
from process_package.tools.Config import get_config_value, set_config_value
from process_package.tools.db_update_from_file import UpdateDB
from process_package.tools.mssql_connect import MSSQL


class AirLeakSlot(QGroupBox):
    data_matrix_changed = Signal(str)
    write_signal = Signal(str)
    connection_signal = Signal(bool)

    def set_enable(self, value):
        self._model.enable = value

    def get_on(self):
        return self._model.enable

    def set_on(self, value):
        self._model.enable = value

    def is_nfc_connect(self):
        return self.nfc.is_nfc_connect()

    def set_port(self, value):
        self.nfc.set_port(value)

    def set_result(self, value):
        self._model.result = value

    def set_dtr(self, value):
        self.nfc.set_dtr(value)

    def get_dtr(self):
        return self.nfc.get_dtr()

    def write(self, value):
        self.nfc.write(value)

    def __init__(self, nfc_name):
        super(AirLeakSlot, self).__init__()

        self._model = AirLeakSlotModel()
        self._mssql = MSSQL(STR_AIR_LEAK)

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(nfc_name))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX, is_nfc=True, is_clean=True, clean_time=5000))
        layout.addWidget(result := GroupLabel(STR_RESULT, is_clean=True, clean_time=5000))

        # size
        nfc.setFixedHeight(NFC_FIXED_HEIGHT)
        data_matrix.setMinimumWidth(130)
        data_matrix.setFixedHeight(NFC_FIXED_HEIGHT)

        # assign
        self.nfc = nfc
        self.data_matrix = data_matrix.label
        self.result = result.label

        # event from out
        self.write_signal.connect(self.write)

        # event for control
        self.nfc.nfc_data_out.connect(self.received_nfc_data)
        self.nfc.connection_signal.connect(self.connection_signal.emit)

        # event from model
        self._model.nfc_enable.connect(self.set_dtr)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_changed.connect(self.data_matrix_changed.emit)
        self._model.result_changed.connect(self.result.setText)
        self._model.result_color_changed.connect(self.result.set_background_color)
        self._model.result_clean.connect(self.result.clean)

        self.delay_write_count = 0

    @Slot(dict)
    def received_nfc_data(self, value):
        if self.delay_write_count:
            self.delay_write_count -= 1

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self._model.data_matrix == data_matrix:
            return

        if not self._model.result:
            return

        if self._model.result != value.get(STR_AIR):
            self.write_signal.emit(f"{data_matrix},{STR_AIR}:{self._model.result}")
            self.delay_write_count = 2
        else:
            write_beep()
            self._model.data_matrix = data_matrix
            self.update_sql()

    @Slot(str)
    def update_sql(self):
        if self._model.result and self._model.data_matrix:
            self._mssql.start_query_thread(self._mssql.insert_pprd,
                                           self._model.data_matrix,
                                           get_time(),
                                           self._model.result,
                                           STR_AIR,
                                           '',
                                           socket.gethostbyname(socket.gethostname()))


class AirLeakSlotModel(QObject):
    nfc_enable = Signal(bool)
    data_matrix_changed = Signal(str)
    result_changed = Signal(str)
    result_color_changed = Signal(str)
    result_clean = Signal()

    def __init__(self):
        super(AirLeakSlotModel, self).__init__()
        self.enable = False
        self._data_matrix = ''
        self._result = ''

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = value
        self.nfc_enable.emit(value)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        if self.enable:
            self._data_matrix = value
            self.data_matrix_changed.emit(value)
            # self.result = ''

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)
        if value in [STR_OK, STR_NG]:
            self.result_color_changed.emit((RED, LIGHT_SKY_BLUE)[value == STR_OK])
            # self.data_matrix = ''
        else:
            self.result_clean.emit()


SLOT_COUNT = 4


class AirLeakManualFourModel(ConfigModel):
    result_changed = Signal(str)
    set_nfc_port = Signal(int, str)
    set_available_ports = Signal(list)

    def __init__(self):
        super(AirLeakManualFourModel, self).__init__()
        self.units = []
        self.result = ''
        self.data_matrix = ''
        self.name = STR_AIR_LEAK
        self.baudrate = 38400
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value
        set_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, value)

    @property
    def nfcs(self):
        return self._nfcs

    @nfcs.setter
    def nfcs(self, value):
        ports = []
        for port, nfc in value.items():
            if STR_NFC in nfc:
                slot_num = int(nfc[-1]) - 1
                self.set_nfc_port.emit(slot_num, port)
                ports.append(port)
        self._nfcs = ports

    @property
    def available_ports(self):
        return self._available_ports

    @available_ports.setter
    def available_ports(self, value):
        for port in self.nfcs:
            value.remove(port)
        self._available_ports = value
        self.set_available_ports.emit(value)


class AirLeakManualFourControl(QObject):
    set_result_slot = Signal(int, str)

    def __init__(self, model):
        super(AirLeakManualFourControl, self).__init__()
        self._model = model

        self.update_db = UpdateDB()

        # controller event connect

    @Slot(str)
    def comport_save(self, comport):
        self._model.comport = comport

    @Slot(str)
    def receive_serial_data(self, value):
        if value:
            self._model.result = STR_OK if STR_OK in value else STR_NG

    def begin(self):
        pass

    def mid_clicked(self):
        pass


class AirLeakManualFourView(Widget):
    open_odd_signal = Signal()
    open_even_signal = Signal()

    def begin(self):
        self.comport.begin()

    def check_all_connection(self, value):
        for index, slot in enumerate(self.slots):
            if slot == self.sender():
                self.slot_enables[index] = value

        if False not in self.slot_enables:
            for slot in self.slots:
                slot.set_enable(False)

    def open_odd(self):
        for index, slot in enumerate(self.slots):
            if index % 2 == 0:
                logger.debug(f"odd {index}")
                slot.set_enable(True)

    def open_even(self):
        for index, slot in enumerate(self.slots):
            if index % 2 != 0:
                logger.debug(f"even {index}")
                slot.set_enable(True)

    def check_odd_even(self, value):
        for index, slot in enumerate(self.slots):
            if slot == self.sender():
                slot.set_enable(False)
                break

        # odd
        if index % 2 == 0:
            self.check_odd_done()
        else:
            self.check_even_done()

    def check_odd_done(self):
        for index, slot in enumerate(self.slots):
            if index % 2 == 0 and slot.get_on():
                break
        else:
            self.open_even_signal.emit()

    def check_even_done(self):
        for index, slot in enumerate(self.slots):
            if index % 2 != 0 and slot.get_on():
                break

    def set_slots_disable(self):
        for slot in self.slots:
            slot.set_enable(False)

    def __init__(self, *args):
        super(AirLeakManualFourView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := SerialComboHBoxLayout(self._model))
        layout.addLayout(slot_layout1 := QGridLayout())
        slots = []
        for l in range(SLOT_COUNT):
            slot_layout1.addWidget(slot := AirLeakSlot(f"NFC {l + 1}"), l // 4, l % 4)
            slot.data_matrix_changed.connect(self.check_odd_even)
            slot.connection_signal.connect(self.check_all_connection)
            slots.append(slot)

        # size
        comport_box.setFixedHeight(COMPORT_FIXED_HEIGHT)
        self.setWindowTitle(f"{STR_AIR_LEAK} Manual v0.1")

        # assign
        self.slots = slots
        self.comport = comport
        self.slot_enables = [True for l in range(SLOT_COUNT)]

        # odd & even event
        self.open_odd_signal.connect(self.open_odd)
        self.open_even_signal.connect(self.open_even)

        # connect widgets to controller
        comport.comport_save.connect(self._control.comport_save)
        comport.serial_output_data.connect(self._control.receive_serial_data)

        # listen for control event signals
        self._control.set_result_slot.connect(lambda index, result: self.slots[index].set_result(result))

        # listen for model event signals
        self._model.result_changed.connect(self.insert_result_each_slot)
        self._model.set_nfc_port.connect(lambda index, port: self.slots[index].set_port(port))
        self._model.set_available_ports.connect(self.comport.set_available_ports)

    @Slot(str)
    def insert_result_each_slot(self, value):
        for slot in self.slots:
            slot.set_result(value)
        self.open_odd_signal.emit()

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()


class AirLeakManualFour(QApplication):
    def __init__(self, sys_argv):
        super(AirLeakManualFour, self).__init__(sys_argv)
        self.load_nfc_window = SplashScreen(STR_AIR_LEAK)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        self._model = AirLeakManualFourModel()
        self._control = AirLeakManualFourControl(self._model)
        self._view = AirLeakManualFourView(self._model, self._control)
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._model.available_ports = get_serial_available_list()
        self._view.show()
        self._view.begin()
        window_center(self._view)
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = AirLeakManualFour(sys.argv)
    sys.exit(app.exec_())
