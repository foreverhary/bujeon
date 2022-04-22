import sys

import pymssql
import qdarkstyle
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QApplication, QDesktopWidget
from pynput import keyboard
from pynput.keyboard import Key

from process_package.check_string import keyboard_event_check_char
from process_package.logger import get_logger
from process_package.mssql_connect import *
from release_process_ui import ReleaseProcessUI
from process_package.style.style import STYLE


class ReleaseProcess(ReleaseProcessUI):
    key_enter_input_signal = pyqtSignal()

    def __init__(self):
        super(ReleaseProcess, self).__init__()

        # set logger
        self.logger = get_logger('LOG')

        # init variable
        self.msg = ''
        self.key_enter_input_signal.connect(self.key_enter_process)

        self.show()

        # center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def on_press(self, key):
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
        self.dmInputLabel.setText(self.msg)
        self.check_db_ok_ng()
        self.msg = ''

    def check_db_ok_ng(self):
        dm = self.dmInputLabel.text()
        try:
            results = check_all_ok(dm)
            if results:
                upperResults = list(map(lambda x: x.upper(), results))
                if 'NG' in upperResults or 'FAIL' in upperResults:
                    self.set_result_display('NG')
                else:
                    self.set_result_display('OK')
                    self.update_out('OK', dm)
            else:
                self.set_result_display('NG')
        except AttributeError as e:
            self.logger.warning(f"Data is None or just Error, {e}")
            self.set_result_display('NG')
        except pymssql.InterfaceError as e:
            self.logger.error(f"DB InterFaceError, {e}")
        except pymssql.DatabaseError as e:
            self.logger.error(f"DatabaseError, {e}")

    def set_result_display(self, result='NG'):
        self.resultInputLabel.setText(result)
        self.resultInputLabel.set_text_property(color=('red', 'blue')[result != 'NG'])

    def keyPressEvent(self, event):
        pass

    def on_release(self, key):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ReleaseProcess()
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
    # ex.orderInput.setBackgroundColor('yellow')
    listener = keyboard.Listener(
        on_press=ex.on_press,
        on_release=ex.on_release
    )
    listener.start()
    sys.exit(app.exec_())
