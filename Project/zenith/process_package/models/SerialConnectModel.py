from PySide2.QtCore import QObject, Signal

from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1
from process_package.tools.Config import set_config_value


class SerialConnectModel(QObject):
    comport_changed = Signal(str)
    comport_open_changed = Signal(bool)
    available_comport_changed = Signal(list)

    def __init__(self):
        pass

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        if isinstance(value, int):
            self._comrpot = self._available_comport[value]
        else:
            self._comport = value
        self.comport_changed.emit(self.comport)

    @property
    def comport_open(self):
        return self._comport_open

    @comport_open.setter
    def comport_open(self, value):
        self._comport_open = bool(value)
        self.comport_open_changed.emit(self._comport_open)
        if self._comport_open:
            set_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, self.comport)

    @property
    def available_comport(self):
        return self._available_comport