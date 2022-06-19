from PySide2.QtCore import QObject

from process_package.tools.Config import set_config_mssql, get_config_mssql
from process_package.resource.string import MSSQL_IP, MSSQL_PORT, MSSQL_ID, MSSQL_PASSWORD, MSSQL_DATABASE


class ConfigModel(QObject):

    @property
    def server_ip(self):
        return self._server_ip

    @server_ip.setter
    def server_ip(self, value):
        self._server_ip = value
        set_config_mssql(MSSQL_IP, self.ip_line_edit.text())

    @property
    def server_port(self):
        return self._server_ip

    @server_port.setter
    def server_port(self, value):
        self._server_port = value
        set_config_mssql(MSSQL_PORT, self.port_line_edit.text())

    @property
    def server_id(self):
        return self._server_id

    @server_id.setter
    def server_id(self, value):
        self._server_id = value
        set_config_mssql(MSSQL_ID, self.id_line_edit.text())

    @property
    def server_password(self):
        return self._server_id

    @server_password.setter
    def server_password(self, value):
        self._server_password = value
        set_config_mssql(MSSQL_PASSWORD, self.password_line_edit.text())

    @property
    def server_database(self):
        return self._server_id

    @server_database.setter
    def server_database(self, value):
        self._server_database = value
        set_config_mssql(MSSQL_DATABASE, self.database_line_edit.text())

    def __init__(self):
        super(ConfigModel, self).__init__()
        get_config_mssql(MSSQL_IP)
        get_config_mssql(MSSQL_PORT)
        get_config_mssql(MSSQL_ID)
        get_config_mssql(MSSQL_PASSWORD)
        get_config_mssql(MSSQL_DATABASE)