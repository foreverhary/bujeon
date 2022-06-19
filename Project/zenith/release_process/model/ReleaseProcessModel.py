from PySide2.QtCore import QObject, Signal

from process_package.check_string import check_dm


class ReleaseProcessModel(QObject):
    previous_process_changed = Signal(str)
    data_matrix_changed = Signal(str)

    @property
    def previous_process(self):
        return self._previous_process

    @previous_process.setter
    def previous_process(self, value):
        self._previous_process = value
        self.previous_process_changed.emit(value)

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''
        self.data_matrix_changed.emit(self._data_matrix)


