from PySide2.QtCore import QObject, Signal

from process_package.check_string import check_dm
from process_package.defined_serial_port import get_serial_available_list
from process_package.models.Config import get_order_number, get_config_value, set_config_value, set_order_number, \
    set_config_mssql
from process_package.models.ConfigModel import ConfigModel
from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, MSSQL_IP, STR_OK, \
    STR_NG


class TouchModel(ConfigModel):
    data_matrix_changed = Signal(str)
    order_number_changed = Signal(str)
    comport_changed = Signal(str)
    comport_open_changed = Signal(bool)
    machine_result_changed = Signal(str)
    available_comport_changed = Signal(list)

    @property
    def order_number(self):
        return self._order_number

    @order_number.setter
    def order_number(self, value):
        self._order_number = value
        self.order_number_changed.emit(value)
        set_order_number(value)

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

    @available_comport.setter
    def available_comport(self, value):
        port_numbers = [int(port[3:]) for port in value]
        port_numbers.sort()
        ports = [f"COM{port}" for port in port_numbers]
        self._available_comport = ports
        self.comport = self._available_comport[0]
        self.available_comport_changed.emit(ports)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        if data_matrix := check_dm(value):
            self._data_matrix = data_matrix
            # TODO mssql update
        else:
            self._data_matrix = ''
        self.data_matrix_changed.emit(self._data_matrix)

    @property
    def machine_result(self):
        return self._machine_result

    @machine_result.setter
    def machine_result(self, value):
        if "TEST RESULT" in value and self.data_matrix:
            self._machine_result = STR_OK if STR_OK in value else STR_NG
            self.machine_result_changed.emit(self._machine_result)

    def begin_config_read(self):
        self.get_order_number()
        self.available_comport = get_serial_available_list()
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1)

    def get_order_number(self):
        self.order_number = get_order_number()

    def __init__(self):
        super(TouchModel, self).__init__()
        self.data_matrix = ''
