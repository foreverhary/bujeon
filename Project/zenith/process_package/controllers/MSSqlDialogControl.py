from PySide2.QtCore import QObject, Slot


class MSSqlDialogControl(QObject):
    def __init__(self, model):
        super(MSSqlDialogControl, self).__init__()
        self._model = model

    @Slot(str)
    def change_ip(self, value):
        self._model.mssql_ip = value

    @Slot(str)
    def change_port(self, value):
        self._model.mssql_port = value

    @Slot(str)
    def change_id(self, value):
        self._model.mssql_id = value

    @Slot(int)
    def change_password(self, value):
        self._model.mssql_password = value

    @Slot(int)
    def change_database(self, value):
        self._model.mssql_database = value
