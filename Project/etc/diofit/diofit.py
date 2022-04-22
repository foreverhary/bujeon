import sys
from threading import Thread

import pandas as pd
import qdarkstyle
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QWidget, QApplication, QComboBox, QGridLayout, QDesktopWidget

from custom_package.LineReadKeyboard import LineReadKeyboard
from custom_package.PyQtCustomComponent import Label
from custom_package.style import STYLE


class Diofit(QWidget):
    key_enter_input_signal = pyqtSignal(str)

    def __init__(self):
        super(Diofit, self).__init__()
        self.data_input()
        self.init_ui()
        self.event_connector()
        self.start_keyboard_listener()

    def data_input(self):
        df = pd.read_excel('00 diofit_Simulation (22-04).xlsx', dtype=str)
        self.df = df.dropna(axis=0)

    def init_ui(self):
        self.setLayout(layout := QGridLayout())
        layout.addWidget(Label('Model'), 0, 0)
        layout.addWidget(Label('EAN Code'), 0, 1)
        layout.addWidget(Label('Scan EAN'), 0, 2)
        self.model_combobox = QComboBox()
        self.model_combobox.setStyleSheet('font-size: 35px')
        self.model_combobox.addItems(list(self.df.BJ_Model))
        self.qr = self.df['EAN Code'][1]
        self.select_label = Label(self.qr)
        self.scan_label = Label()
        self.select_label.setMinimumWidth(500)
        self.scan_label.setMinimumWidth(500)
        self.pass_fail = Label(font_size=200)
        self.pass_fail.setMinimumWidth(300)
        layout.addWidget(self.model_combobox, 1, 0)
        layout.addWidget(self.select_label, 1, 1)
        layout.addWidget(self.scan_label, 1, 2)
        layout.addWidget(self.pass_fail, 2, 0, 3, 3)
        self.setWindowTitle('DIOFIT')
        self.show()
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @property
    def qr(self):
        return self._qr

    @qr.setter
    def qr(self, value):
        if isinstance(value, str):
            self._qr = value

            print(self._qr)

    def select_combobox(self, index):
        self.qr = self.df['EAN Code'][index+1]
        self.select_label.setText(self.qr)

    def event_connector(self):
        self.model_combobox.currentIndexChanged.connect(self.select_combobox)
        self.key_enter_input_signal.connect(self.key_enter_process)

    def start_keyboard_listener(self):
        self.keyboard_listener = Thread(target=self.listen_keyboard, args=(LineReadKeyboard,), daemon=True)
        self.keyboard_listener.start()

    def listen_keyboard(self, func):
        listener = func()
        self.key_enter_input_signal.emit(listener.get_line())
        self.start_keyboard_listener()

    def key_enter_process(self, line_data):
        if line_data.isdigit():
            self.scan_label.setText(line_data)
            if self.qr == line_data:
                self.pass_fail.setText('OK')
                self.pass_fail.set_text_property(color='lightskyblue')
            else:
                self.pass_fail.setText('NG')
                self.pass_fail.set_text_property(color='red')
        else:
            self.pass_fail.setText('NG')
            self.pass_fail.set_text_property(color='red')


if __name__ == '__main__':
    # df = pd.read_excel('00 diofit_Simulation (22-04).xlsx', dtype=str)
    # df_drop_row = df.dropna(axis=0)
    # print(df_drop_row['EAN Code'])
    # print(df_drop_row.BJ_Model[1])

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
    ex = Diofit()
    sys.exit(app.exec_())
