import sys

import pymssql
import qdarkstyle
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication
from pynput import keyboard
from pynput.keyboard import Key

from RegisterUI import RegisterUI
from process_package.Config import Config
from process_package.check_string import keyboard_event_check_char
from process_package.defined_variable_function import POP_SECTION, ORDER_NUMBER
from process_package.order_number_dialog import OderNumberDialog
from process_package.logger import get_logger
from process_package.mssql_connect import *
from process_package.style.style import STYLE


class Register(RegisterUI):
    key_enter_input_signal = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Register, self).__init__()
        self.msg = ''
        self.logger = get_logger()

        # config
        self.config = Config('config.ini')
        self.input_aufnr()

        self.config_window = OderNumberDialog()

        # connect Event
        self.aufnrButton.clicked.connect(self.aufrn_button_clicked)
        self.config_window.orderNumberSendSignal.connect(self.input_aufnr)
        self.key_enter_input_signal.connect(self.key_enter_process)

        self.show()

    def aufrn_button_clicked(self):
        self.config_window.showModal()

    def input_aufnr(self):
        try:
            self.aufnrLineEdit.setText(self.config.getValue(POP_SECTION, ORDER_NUMBER))
        except KeyError:
            self.logger.error('Need Config')

    def on_press(self, key):
        print(key)
        try:
            if keyboard_event_check_char(key.char):
                raise TypeError
            self.msg += key.char
        except TypeError:
            pass
        except AttributeError:
            if key == Key.enter:
                self.key_enter_input_signal.emit()
            elif key == Key.space:
                self.msg += ' '

    def key_enter_process(self):
        if 'RESET' in self.msg:
            self.dmInput.setText('')
            self.jigInput.setText('')
        elif 'REGISTER' in self.msg:
            self.saveSql()
        else:
            self.dmInput.setText(self.msg)
            # if not self.dmInput.text():
            #     self.dmInput.setText(self.msg)
            # elif not self.jigInput.text():
            #     self.jigInput.setText(self.msg)
        self.msg = ''

    def saveSql(self):
        if order := self.config.getValue(POP_SECTION, ORDER_NUMBER):
            if dm := self.dmInput.text():
                try:
                    insertOut(order, dm)
                except pymssql.IntegrityError:
                    self.logger.error('pymssql error!!')

                # if jig := self.jigInput.text():
                #     try:
                #         self.mssql.insertOut(order, dm, jig)
                #     except pymssql.IntegrityError:
                #         self.logger.error('DB Error!!!')
                #         pass

    def on_release(self, key):
        pass

    def keyPressEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Register()
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
    # ex.mainLayout.orderInput.setBackgroundColor('yellow')
    listener = keyboard.Listener(
        on_press=ex.on_press,
        on_release=ex.on_release
    )
    listener.start()
    sys.exit(app.exec_())
