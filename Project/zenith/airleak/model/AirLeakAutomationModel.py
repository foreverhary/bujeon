from PySide2.QtCore import Signal

from process_package.models.ConfigModel import ConfigModel
from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, STR_AIR_LEAK, STR_NFC
from process_package.tools.Config import set_config_value, get_config_value


class AirLeakAutomationModel(ConfigModel):
    set_nfc_port = Signal(int, str)
    set_available_ports = Signal(list)

    def __init__(self):
        super(AirLeakAutomationModel, self).__init__()
        self.units = []
        self.result = ''
        self.data_matrix = ''
        self.name = STR_AIR_LEAK
        self.baudrate = 38400
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1)

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
