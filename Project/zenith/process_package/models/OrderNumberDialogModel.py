from PySide2.QtCore import QObject, Signal

from process_package.tools.Config import get_order_number, set_order_number


class OrderNumberDialogModel(QObject):
    order_number_list_changed = Signal(list)
    material_code_changed = Signal(str)
    model_name_changed = Signal(str)
    order_number_changed = Signal(str)
    connection_changed = Signal(bool)

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value

    @property
    def order_keyword(self):
        return self._order_keyword

    @order_keyword.setter
    def order_keyword(self, value):
        self._order_keyword = value

    @property
    def material_keyword(self):
        return self._material_keyword

    @material_keyword.setter
    def material_keyword(self, value):
        self._material_keyword = value

    @property
    def model_keyword(self):
        return self._model_keyword

    @model_keyword.setter
    def model_keyword(self, value):
        self._model_keyword = value

    @property
    def order_number_list(self):
        return self._order_number_list

    @order_number_list.setter
    def order_number_list(self, value):
        self._order_number_list = value
        self.order_number_list_changed.emit([data[0] for data in value])

    @property
    def order_number_index(self):
        return self._order_number_index

    @order_number_index.setter
    def order_number_index(self, value):
        self._order_number_index = value
        print(value)
        self.order_number = self.material_code, self.model_name = self.order_number_list[value]

    @property
    def material_code(self):
        return self._material_code

    @material_code.setter
    def material_code(self, value):
        self._material_code = value
        self.material_code_changed.emit(value)

    @property
    def model_name(self):
        return self._model_name

    @model_name.setter
    def model_name(self, value):
        self._model_name = value
        self.model_name_changed.emit(value)

    @property
    def order_number(self):
        return self._order_number

    @order_number.setter
    def order_number(self, value):
        self._order_number = value
        self.order_number_changed.emit(value)

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value
        self.connection_changed.emit(value)

    def read_order_number(self):
        self.order_number = get_order_number()

    def save(self):
        set_order_number(self.order_number)

    def __init__(self):
        super(OrderNumberDialogModel, self).__init__()
        self.order_keyword = ''
        self.material_keyword = ''
        self.model_keyword = ''
        self.connection = False
