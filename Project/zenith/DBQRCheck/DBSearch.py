import datetime
import sys

from PySide2.QtCore import QObject, Slot, Signal, Qt
from PySide2.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QHBoxLayout, QHeaderView, \
    QApplication

from process_package.check_string import check_dm
from process_package.component.CustomComponent import Label, LineEdit, Widget, style_sheet_setting
from process_package.models.BasicModel import DataMatrixModel
from process_package.tools.CommonFunction import logger
from process_package.tools.LineReadKeyboard import LineReadKeyboard
from process_package.tools.mssql_connect import MSSQL


class DBSearch(Widget):
    def __init__(self):
        super(DBSearch, self).__init__()

        # class
        self._model = DBSearchModel()
        self._control = DBSearchControl(self._model)

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(search_layout := QHBoxLayout())
        search_layout.addWidget(Label('Search : '))
        search_layout.addWidget(search := LineEdit())
        layout.addWidget(table := QTableWidget())

        self.setWindowTitle('DB Check')

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

        self.show()

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
                if isinstance(item, datetime.datetime):
                    item = str(item)
                self.table.setItem(x, index, widget_item := QTableWidgetItem(item))
                widget_item.setFlags(widget_item.flags() ^ Qt.ItemIsEditable)

    def closeEvent(self, e):
        self._parent_control.keyboard_disabled = False


class DBSearchControl(QObject):
    def __init__(self, model):
        super(DBSearchControl, self).__init__()
        self._model = model
        self._mssql = MSSQL()

        self.keyboard_listener = LineReadKeyboard(self.input_keyboard_line)

    @Slot(str)
    def input_keyboard_line(self, value):
        if not (data_matrix := check_dm(value)):
            return

        self._model.data_matrix = data_matrix

        self._model.pprd_list = self._mssql(self._mssql.select_pprd_with_data_matrix, data_matrix)


class DBSearchModel(DataMatrixModel):
    pprd_list_changed = Signal(list)

    def __init__(self):
        super(DBSearchModel, self).__init__()

    @property
    def pprd_list(self):
        return self._pprd_list

    @pprd_list.setter
    def pprd_list(self, value):
        self._pprd_list = value
        self.pprd_list_changed.emit(value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = DBSearch()
    sys.exit(app.exec_())
