from PySide2.QtCore import QObject, Slot

from process_package.tools.mssql_connect import MSSQL
from process_package.resource.string import STR_TOUCH


class OrderNumberDialogControl(QObject):
    def __init__(self, model):
        super(OrderNumberDialogControl, self).__init__()
        self._model = model
        self._mssql = MSSQL(STR_TOUCH)
        self._mssql.order_list_changed.connect(self.change_order_number_list)
        self._mssql.connection_status_changed.connect(self.change_connection_status)
        # self._mssql.start_query_thread(self._mssql.get_mssql_conn)

    @Slot(object)
    def change_date(self, value):
        date = list(map(lambda x: f"{x}".zfill(2), value.getDate()))
        self._model.date = ''.join(date)

    @Slot(str)
    def change_order_keyword(self, value):
        self._mode.order_keyword = value

    @Slot(str)
    def change_material_keyword(self, value):
        self._model.material_keyword = value

    @Slot(str)
    def change_model_keyword(self, value):
        self._model.model_keyword = value

    @Slot(int)
    def change_order_number_index(self, value):
        self._model.order_number_index = value

    @Slot(int)
    def change_order_number(self, value):
        self._model.order_number = value

    @Slot()
    def get_order_list(self):
        # if self._mssql.con:
        self._mssql.start_query_thread(self._mssql.select_order_number_with_date_material_model,
                                       self._model.date,
                                       self._model.order_keyword,
                                       self._model.material_keyword,
                                       self._model.model_keyword)

    @Slot(bool)
    def change_connection_status(self, connection):
        self._model.connection = connection

    @Slot(list)
    def change_order_number_list(self, order_list):
        self._model.order_number_list = order_list
