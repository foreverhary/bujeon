import socket

from PySide2.QtCore import Signal, QObject, Slot
from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import Widget, get_time
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.size import NFC_FIXED_HEIGHT, COMPORT_FIXED_HEIGHT
from process_package.resource.string import STR_MACHINE_COMPORT, STR_RESULT, STR_AIR_LEAK, STR_DATA_MATRIX, STR_OK, \
    STR_NG, STR_AIR
from process_package.tools.CommonFunction import logger
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
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX, is_nfc=True))
        layout.addWidget(result := GroupLabel(STR_RESULT))

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
        self._model.result_changed.connect(self.update_sql)
        self._model.result_color_changed.connect(self.result.set_background_color)
        self._model.result_clean.connect(self.result.clean)

    @Slot(dict)
    def received_nfc_data(self, value):
        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self._model.data_matrix == data_matrix:
            return

        self._model.data_matrix = data_matrix

    @Slot(str)
    def update_sql(self, value):
        if value:
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
            self.result = ''

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)
        if value == STR_OK:
            self.result_color_changed.emit(LIGHT_SKY_BLUE)
        elif value == STR_NG:
            self.result_color_changed.emit(RED)
        else:
            self.result_clean.emit()


SLOT_COUNT = 8


class AirLeakAutomationView(Widget):
    open_odd_signal = Signal()
    open_even_signal = Signal()

    def begin(self):
        self.comport.begin()

    def check_all_connection(self, value):
        for index, slot in enumerate(self.slots):
            if slot == self.sender():
                self.slot_enables[index] = value

        if False in self.slot_enables:
            for slot in self.slots:
                slot.set_enable(False)
        else:
            self.open_odd_signal.emit()

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
        else:
            self.check_all_connection(True)

    def set_slots_disable(self):
        for slot in self.slots:
            slot.set_enable(False)

    def __init__(self, *args):
        super(AirLeakAutomationView, self).__init__()
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
        self.setWindowTitle(f"{STR_AIR_LEAK} AUTOMATION v1.0")

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
        self._model.set_nfc_port.connect(lambda index, port: self.slots[index].set_port(port))
        self._model.set_available_ports.connect(self.comport.set_available_ports)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        db_action = menu.addAction('DB Setting')
        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()
