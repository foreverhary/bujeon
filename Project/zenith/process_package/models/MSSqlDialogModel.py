from PySide2.QtCore import QObject, Signal

from process_package.models.Config import get_config_value, get_config_mssql, set_config_mssql
from process_package.mssql_connect import select_order_number_with_date_material_model
from process_package.resource.string import CONFIG_FILE_NAME, MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, \
    MSSQL_DATABASE


class MSSqlDialogModel(QObject):
    change_ip = Signal(str)
    change_port = Signal(str)
    change_id = Signal(str)
    change_password = Signal(str)
    change_database = Signal(str)

    @property
    def mssql_ip(self):
        return self._mssql_ip

    @mssql_ip.setter
    def mssql_ip(self, value):
        self._mssql_ip = value
        self.change_ip.emit(value)

    @property
    def mssql_port(self):
        return self._mssql_port

    @mssql_port.setter
    def mssql_port(self, value):
        self._mssql_port = value
        self.change_port.emit(value)

    @property
    def mssql_id(self):
        return self._mssql_id

    @mssql_id.setter
    def mssql_id(self, value):
        self._mssql_id = value
        self.change_id.emit(value)

    @property
    def mssql_password(self):
        return self._mssql_password

    @mssql_password.setter
    def mssql_password(self, value):
        self._mssql_password = value
        self.change_password.emit(value)

    @property
    def mssql_database(self):
        return self._mssql_database

    @mssql_database.setter
    def mssql_database(self, value):
        self._mssql_database = value
        self.change_database.emit(value)

    def read_mssql_config(self):
        self.mssql_ip = get_config_mssql(MSSQL_IP)
        self.mssql_port = get_config_mssql(MSSQL_PORT)
        self.mssql_id = get_config_mssql(MSSQL_ID)
        self.mssql_password = get_config_mssql(MSSQL_PASSWORD)
        self.mssql_database = get_config_mssql(MSSQL_DATABASE)

    def save(self):
        set_config_mssql(MSSQL_IP, self.mssql_ip)
        set_config_mssql(MSSQL_PORT, self.mssql_port)
        set_config_mssql(MSSQL_ID, self.mssql_id)
        set_config_mssql(MSSQL_PASSWORD, self.mssql_password)
        set_config_mssql(MSSQL_DATABASE, self.mssql_database)

    def __init__(self):
        super(MSSqlDialogModel, self).__init__()

