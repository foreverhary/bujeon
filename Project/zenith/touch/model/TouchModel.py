from PySide2.QtCore import Signal

from process_package.models.BasicModel import BasicModel


class TouchModel(BasicModel):
    data_matrix_waiting_changed = Signal(str)

    def __init__(self):
        super(TouchModel, self).__init__()

    @property
    def data_matrix_waiting(self):
        if not hasattr(self, '_data_matrix_waiting'):
            self._data_matrix_waiting = ''
        return self._data_matrix_waiting

    @data_matrix_waiting.setter
    def data_matrix_waiting(self, value):
        self._data_matrix_waiting = value
        self.data_matrix_waiting_changed.emit(value)
