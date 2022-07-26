import sys
import time
from threading import Thread

import pymcprotocol
from PySide2.QtCore import QRegExp, Signal
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout, QApplication, QComboBox

from component.CustomComponent import Widget, Label, LineEdit, Button
from tools.CommonFunction import logger


def debug_log(func):
    def inner(*args, **kwargs):
        logger.debug(func.__name__)
        try:
            re_value = func(*args, **kwargs)
            logger.debug(f"{func.__name__} : {re_value}")
        except Exception as e:
            logger.debug(f"{type(e)} : {e}")
        return re_value
    return inner


class MCTester(Widget):
    status_changed = Signal(str)

    def __init__(self):
        super(MCTester, self).__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(ip_setter := QGroupBox("IP Setting"))
        ip_layout = QGridLayout(ip_setter)
        ip_layout.addWidget(Label('IP'), 0, 0)
        ip_layout.addWidget(Label('PORT'), 1, 0)
        ip_layout.addWidget(Label('Grade'), 2, 0)
        ip_layout.addWidget(ip := LineEdit(), 0, 1)
        ip_layout.addWidget(port := LineEdit(), 1, 1)
        ip_layout.addWidget(grade := QComboBox(), 2, 1)

        layout.addWidget(send_write := QGroupBox("Test Send Write"))
        test_layout = QGridLayout(send_write)
        test_layout.addWidget(Label('STATUS'), 0, 0)
        test_layout.addWidget(status := LineEdit(), 0, 1)
        test_layout.addWidget(start := Button('START'), 3, 0)
        test_layout.addWidget(stop := Button('STOP'), 3, 1)

        # option
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_validator = QRegExpValidator(ip_regex, self)
        ip.setValidator(ip_validator)
        port.setValidator(QIntValidator())
        port.setMaxLength(5)
        grade.addItems(['A', 'B', 'C'])
        status.setDisabled(True)

        ip.setText('192.168.0.1')
        port.setText('4001')

        # assign
        self.ip = ip
        self.port = port
        self.grade = grade
        self.result = status
        self.read_button = start
        self.write_button = stop

        # event
        start.clicked.connect(self._start_plc)
        stop.clicked.connect(self._stop_plc)

        self.status_changed.connect(self.result.setText)
        self.run_plc = False

        self.show()

        self.pymc3e = pymcprotocol.Type3E()

    def _start_plc(self):
        self.run_plc = True
        Thread(target=self._plc_process, daemon=True).start()

    def _stop_plc(self):
        self.run_plc = False

    def _connect(self):
        self.pymc3e.setaccessopt(commtype='binary')
        self.pymc3e.connect(self.ip.text(), int(self.port.text()))

    def _plc_process(self):
        while self.run_plc:
            while not self._read('B20')[0]:
                if not self.run_plc:
                    break
                time.sleep(0.1)

            self._write('B21', [1])
            time.sleep(0.2)
            self._write('B21', [0])

            self._write('B22', [1])
            self._write(f'B2{self.grade.currentText()}', [1])
            while not self._read('B23')[0]:
                if not self.run_plc:
                    break
                time.sleep(0.1)

            self._write('B22', [0])
            self._write(f'B2{self.grade.currentText()}', [0])

    # @debug_log
    def _read(self, addr):
        try:
            self._connect()
            value = self.pymc3e.batchread_bitunits(headdevice=addr, readsize=1)
            self.pymc3e.close()
            self.status_changed.emit(f"read : {addr}")
            return value
        except Exception as e:
            print(e)
            return [0]

    # @debug_log
    def _write(self, addr, value):
        try:
            self._connect()
            self.pymc3e.batchwrite_bitunits(headdevice=addr, values=value)
            self.pymc3e.close()
            self.status_changed.emit(f"write : {addr}, {value}")
        except Exception as e:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MCTester()
    sys.exit(app.exec_())
