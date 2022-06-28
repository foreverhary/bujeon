from PySide2.QtCore import QObject, Slot
from PySide2.QtWidgets import QDialog

from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.sqlite3_connect import sqlite_init, select_pprd_with_data_matrix


class SearchDataMatrixLocal(QDialog):
    def __init__(self):
        super(SearchDataMatrixLocal, self).__init__()
        self._model = SearchDataMatrixLocalModel()
        self._control = SearchDataMatrixLocalControl(self._model)



        self.showModal()

    def showModal(self):
        return super().exec_()




class SearchDataMatrixLocalControl(QObject):
    def __init__(self, model):
        super(SearchDataMatrixLocalControl, self).__init__()
        self._model = model
        sqlite_init()

        self.keyboard_listener = LineReadKeyboard()

        # controller event connect
        self.keyboard_listener.keyboard_input_signal.connect(self.input_keyboard_line)

    @Slot(str)
    def input_keyboard_line(self, value):
        if data := select_pprd_with_data_matrix(value):




class SearchDataMatrixLocalModel(QObject):
    def __init__(self):
        super(SearchDataMatrixLocalModel, self).__init__()