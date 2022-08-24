from PySide2.QtCore import Signal

from process_package.models.BasicModel import BasicModel
from process_package.resource.string import COMPORT_SECTION, MACHINE_COMPORT_1, STR_AIR_LEAK, STR_NFC
from process_package.tools.Config import set_config_value, get_config_value


class AirLeakAutomationModel(BasicModel):
    set_nfc_port = Signal(int, str)
    set_available_ports = Signal(list)

    def __init__(self):
        super(AirLeakAutomationModel, self).__init__()
        self.units = []
        self.result = ''
        self.data_matrix = ''
        self.name = STR_AIR_LEAK

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
