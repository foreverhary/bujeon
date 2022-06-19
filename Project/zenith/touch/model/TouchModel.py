from PySide2.QtCore import Signal

from process_package.check_string import check_dm
from process_package.defined_serial_port import get_serial_available_list
from process_package.models.SerialConnectModel import SerialConnectModel
from process_package.resource.color import RED, LIGHT_SKY_BLUE, WHITE
from process_package.tools.mssql_connect import MSSQL
from process_package.tools.Config import get_order_number, get_config_value, set_config_value, set_order_number
from process_package.models.ConfigModel import ConfigModel
from process_package.resource.string import CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1, STR_OK, \
    STR_NG, STR_TOUCH, STR_INSERT_ORDER_NUMBER, STR_READY, STR_WRITE_DONE_SCAN_NEXT_QR, STR_WAIT_FOR_MACHINE_RESULT


class TouchModel(ConfigModel):
    comport_changed = Signal(str)
    comport_open_changed = Signal(bool)
    available_comport_changed = Signal(list)
    data_matrix_changed = Signal(str)
    order_number_changed = Signal(str)
    machine_result_changed = Signal(str)
    status_changed = Signal(str)
    status_color_changed = Signal(str)

    def __init__(self):
        super(TouchModel, self).__init__()
        self.serial = SerialConnectModel()
        self.data_matrix = ''

    @property
    def order_number(self):
        return self._order_number

    @order_number.setter
    def order_number(self, value):
        self.status = STR_READY if value else STR_INSERT_ORDER_NUMBER
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
        if value:
            self.status = STR_WAIT_FOR_MACHINE_RESULT
        self._data_matrix = value
        self.data_matrix_changed.emit(self._data_matrix)

    @property
    def machine_result(self):
        return self._machine_result

    @machine_result.setter
    def machine_result(self, value):
        if value:
            self.status = STR_WRITE_DONE_SCAN_NEXT_QR
        self._machine_result = value
        self.machine_result_changed.emit(value)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        if value == STR_INSERT_ORDER_NUMBER:
            self.status_color = RED
        elif value == STR_WAIT_FOR_MACHINE_RESULT:
            self.status_color = WHITE
        else:
            self.status_color = LIGHT_SKY_BLUE
        self._status = value
        self.status_changed.emit(value)

    @property
    def status_color(self):
        return self._status_color

    @status_color.setter
    def status_color(self, value):
        self._status_color = value
        self.status_color_changed.emit(value)

    def begin_config_read(self):
        self.get_order_number()
        self.available_comport = get_serial_available_list()
        self.comport = get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1)

    def get_order_number(self):
        self.order_number = get_order_number()
