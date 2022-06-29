from PySide2.QtCore import QObject, Slot
from PySide2.QtWidgets import QFileDialog


class FunctionConfigControl(QObject):

    def __init__(self, model):
        super(FunctionConfigControl, self).__init__()
        self._model = model

    @Slot(str)
    def set_grade_path(self, value):
        self._model.grade_path = value

    @Slot(str)
    def set_summary_path(self, value):
        self._model.summary_path = value

    @Slot(str)
    def set_a_min(self, value):
        self._model.a_min = value

    @Slot(str)
    def set_a_max(self, value):
        self._model.a_max = value

    @Slot(str)
    def set_b_min(self, value):
        self._model.b_min = value

    @Slot(str)
    def set_b_max(self, value):
        self._model.b_max = value

    @Slot(str)
    def set_c_min(self, value):
        self._model.c_min = value

    @Slot(str)
    def set_c_max(self, value):
        self._model.c_max = value

    @Slot()
    def open_set_directory_grade_path(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self._model.grade_path)):
            self._model.grade_path = path

    def open_set_directory_summary_path(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self._model.summary_path)):
            self._model.summary_path = path
