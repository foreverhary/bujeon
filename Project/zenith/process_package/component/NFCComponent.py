from PySide2.QtCore import QObject, Signal, Slot

from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.tools.CommonFunction import logger
from process_package.tools.NFCSerialPort import NFCSerialPort


class NFCComponent(GroupLabel):
    nfc_data_out = Signal(dict)

    def __init__(self):
        super(NFCComponent, self).__init__()
        self._model = NFCComponentModel()
        self._control = NFCComponentControl(self._model)

        self._control.nfc_data_out.connect(self.data_out)

        self._model.nfc_changed.connect(self._control.nfc.set_port)
        self._model.nfc_changed.connect(self.label.setText)
        self._model.nfc_connection_changed.connect(self.label.set_background_color)

    @Slot(dict)
    def data_out(self, value):
        logger.debug(value)
        self.nfc_data_out.emit(value)

    def set_port(self, port):
        self._model.port = port

    def write(self, value):
        self._control.nfc.write(value)


class NFCComponentControl(QObject):
    nfc_data_out = Signal(dict)

    def __init__(self, model):
        super(NFCComponentControl, self).__init__()
        self._model = model

        self.nfc = NFCSerialPort()

        self.nfc.nfc_out_signal.connect(self.data_out)
        self.nfc.connection_signal.connect(self.receive_nfc_connection)

    @Slot(dict)
    def data_out(self, value):
        logger.debug(value)
        self.nfc_data_out.emit(value)

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
