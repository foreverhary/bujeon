from PySide2.QtCore import QObject, Slot

from process_package.mssql_connect import select_order_number_with_date_material_model


class OrderNumberDialogControl(QObject):
    def __init__(self, model):
        super(OrderNumberDialogControl, self).__init__()
        self._model = model

    @Slot(object)
    def change_date(self, value):
        date = list(map(lambda x: f"{x}".zfill(2), value.getDate()))
        self._model.date = ''.join(date)

    @Slot(str)
    def change_order_keyword(self, value):
        self._mode.order_keyword = value

    @Slot(str)
    def change_material_keyword(self, value):
        self._mode.material_keyword = value

    @Slot(str)
    def change_model_keyword(self, value):
        self._mode.model_keyword = value

    @Slot(int)
    def change_order_number_index(self, value):
        self._model.order_number_index = value

    @Slot(int)
    def change_order_number(self, value):
        self._model.order_number = value

    @Slot()
    def get_order_list(self):
        self._model.order_number_list = select_order_number_with_date_material_model(
            self._model.date,
            self._model.order_keyword,
            self._model.material_keyword,
            self._model.model_keyword
        )
