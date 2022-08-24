from PySide2.QtCore import QObject, Slot, Signal, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView

from process_package.check_string import check_dm
from process_package.component.CustomComponent import Label, LineEdit
from process_package.tools.CommonFunction import logger
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.sqlite3_connect import sqlite_init, select_pprd_with_data_matrix


class SearchDataMatrixLocal(QDialog):
    def __init__(self, parent_control):
        super(SearchDataMatrixLocal, self).__init__()

        # class
        self._parent_control = parent_control
        self._model = SearchDataMatrixLocalModel()
        self._control = SearchDataMatrixLocalControl(self._model)

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(search_layout := QHBoxLayout())
        search_layout.addWidget(Label('Search : '))
        search_layout.addWidget(search := LineEdit())
        layout.addWidget(table := QTableWidget())

        self.setWindowTitle('Local Search')

        # size
        search.setMinimumWidth(200)
        self.setMinimumSize(700, 400)

        # assign
        self.table = table
        self.search = search

        # setting
        self.search.setDisabled(True)

        self.init_event()

        # set Table
        self.init_table()

        self.showModal()

    def init_event(self):
        self._model.data_matrix_changed.connect(self.search.setText)
        self._model.pprd_list_changed.connect(self.set_tables)

    def init_table(self):
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['Data Matrix', 'Time', 'Result', 'PCODE', 'ECODE', 'IP'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    @Slot(list)
    def set_tables(self, rows):
        logger.debug(rows)
        self.table.setRowCount(len(rows))

        for x, row in enumerate(rows):
            for index, item in enumerate(row):
                self.table.setItem(x, index, widget_item := QTableWidgetItem(item))
                widget_item.setFlags(widget_item.flags() ^ Qt.ItemIsEditable)

    def closeEvent(self, e):
        self._parent_control.keyboard_disabled = False

    def showModal(self):
        return super().exec_()


class SearchDataMatrixLocalControl(QObject):
    def __init__(self, model):
        super(SearchDataMatrixLocalControl, self).__init__()
        self._model = model
        sqlite_init()

        self.keyboard_listener = LineReadKeyboard(self.input_keyboard_line)

    @Slot(str)
    def input_keyboard_line(self, value):
        if not (data_matrix := check_dm(value)):
            return

        self._model.data_matrix = data_matrix

        self._model.pprd_list = select_pprd_with_data_matrix(data_matrix)


class SearchDataMatrixLocalModel(QObject):
    data_matrix_changed = Signal(str)
    pprd_list_changed = Signal(list)

    def __init__(self):
        super(SearchDataMatrixLocalModel, self).__init__()

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(value)

    @property
    def pprd_list(self):
        return self._pprd_list

    @pprd_list.setter
    def pprd_list(self, value):
        self._pprd_list = value
        self.pprd_list_changed.emit(value)
