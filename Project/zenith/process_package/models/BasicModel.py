from PySide2.QtCore import QObject, Signal

from process_package.resource.color import BACK_GROUND_COLOR
from process_package.tools.Config import set_config_mssql, get_config_mssql, set_order_number, get_order_number
from process_package.resource.string import MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE


class BasicModel(QObject):
    order_number_changed = Signal(str)

    data_matrix_changed = Signal(str)
    data_matrix_background_color_changed = Signal(str)

    machine_result_changed = Signal(str)
    machine_result_background_color_changed = Signal(str)

    status_changed = Signal(str)
    status_color_changed = Signal(str)

    @property
    def order_number(self):
        if not hasattr(self, '_order_number'):
            self._order_number = ''
        return self._order_number

    @order_number.setter
    def order_number(self, value):
        self._order_number = value
        self.order_number_changed.emit(value)
        set_order_number(value)

    @property
    def data_matrix(self):
        if not hasattr(self, '_data_matrix'):
            self._data_matrix = ''
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(value)

    @property
    def data_matrix_background_color(self):
        if not hasattr(self, '_data_matrix_color'):
            self._data_matrix_color = ''
        return self._data_matrix_color

    @data_matrix_background_color.setter
    def data_matrix_background_color(self, value):
        self._data_matrix_color = value
        self.data_matrix_background_color_changed.emit(value)

    @property
    def machine_result(self):
        if not hasattr(self, '_machine_result'):
            self._machine_result = ''
        return self._machine_result

    @machine_result.setter
    def machine_result(self, value):
        self._machine_result = value
        self.machine_result_changed.emit(value)

    @property
    def machine_result_background_color(self):
        if not hasattr(self, 'machine_result_background_color'):
            self._machine_result_background_color = BACK_GROUND_COLOR
        return self._machine_result_background_color

    @machine_result_background_color.setter
    def machine_result_background_color(self, value):
        self._machine_result_background_color = value
        self.machine_result_background_color_changed.emit(value)

    @property
    def status(self):
        if not hasattr(self, '_status'):
            self._status = ''
        return self._status

    @status.setter
    def status(self, value):
        self._status = value
        self.status_changed.emit(value)

    @property
    def status_color(self):
        return self._status_color

    @status_color.setter
    def status_color(self, value):
        self._status_color = value
        self.status_color_changed.emit(value)

    def __init__(self):
        super(BasicModel, self).__init__()
        self.order_number = get_order_number()
