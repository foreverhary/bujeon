from PySide2.QtCore import QObject, Signal, Slot

from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.nfc_checker import NFCCheckerDialog
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.clickable import clickable


class NFCComponent(GroupLabel):
    nfc_data_out = Signal(dict)
    nfc_data_out_to_checker = Signal(dict)
    connection_signal = Signal(bool)

    def is_nfc_connect(self):
        return self._control.nfc.is_nfc_connect()

    def set_port(self, port):
        self._model.port = port

    def get_port(self):
        return self._model.port

    def set_dtr(self, value):
        self._control.nfc.set_dtr(value)

    def get_dtr(self):
        return self._control.nfc.get_dtr()

    def get_nfc_name(self):
        return self._model.nfc_name

    def write(self, value):
        self._control.nfc.write(value)

    def __init__(self, title=''):
        super(NFCComponent, self).__init__(title)
        self._model = NFCComponentModel()
        self._control = NFCComponentControl(self._model)

        self._control.nfc_data_out.connect(self.nfc_data_bridge)
        self._control.connection_signal.connect(self.connection_signal.emit)

        self._model.nfc_name = title
        self._model.nfc_changed.connect(self._control.nfc.set_port)
        self._model.nfc_changed.connect(self.label.setText)
        self._model.nfc_connection_changed.connect(self.label.set_background_color)

        clickable(self).connect(self.open_checker)

        self.checker_on = False

    def nfc_data_bridge(self, value):
        if self.checker_on:
            self.nfc_data_out_to_checker.emit(value)
        else:
            self.nfc_data_out.emit(value)

    def open_checker(self):
        self.checker_on = True
        NFCCheckerDialog(self)


class NFCComponentControl(QObject):
    nfc_data_out = Signal(dict)
    connection_signal = Signal(bool)

    def __init__(self, model):
        super(NFCComponentControl, self).__init__()
        self._model = model

        self.nfc = NFCSerialPort()

        self.nfc.nfc_out_signal.connect(self.nfc_data_out.emit)
        self.nfc.connection_signal.connect(self.receive_nfc_connection)
        self.nfc.connection_signal.connect(self.connection_signal.emit)

    @Slot(bool)
    def receive_nfc_connection(self, connection):
        self._model.nfc_connection = connection


class NFCComponentModel(QObject):
    nfc_connection_changed = Signal(str)
    nfc_changed = Signal(str)

    def __init__(self):
        super(NFCComponentModel, self).__init__()

    @property
    def nfc_connection(self):
        return self._nfc_connection

    @nfc_connection.setter
    def nfc_connection(self, value):
        self.nfc_connection_changed.emit(LIGHT_SKY_BLUE if value else RED)

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self.nfc_changed.emit(value)

    @property
    def nfc_name(self):
        return self._nfc_name

    @nfc_name.setter
    def nfc_name(self, value):
        self._nfc_name = value
