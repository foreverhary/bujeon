import sys

from PySide2.QtCore import QRegExp
from PySide2.QtGui import QIntValidator, QRegExpValidator
from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout, QApplication, QComboBox

import pymcprotocol
import socket

from component.CustomComponent import Widget, Label, LineEdit, Button
from tools.CommonFunction import logger


def debug_log(func):
    def inner(*args, **kwargs):
        logger.debug(func.__name__)
        try:
            logger.debug(f"{func.__name__} : {func(*args, **kwargs)}")
        except Exception as e:
            logger.debug(f"{type(e)} : {e}")

    return inner


class MCTester(Widget):
    def __init__(self):
        super(MCTester, self).__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(ip_setter := QGroupBox("IP Setting"))
        ip_layout = QGridLayout(ip_setter)
        ip_layout.addWidget(Label('IP'), 0, 0)
        ip_layout.addWidget(Label('PORT'), 1, 0)
        ip_layout.addWidget(Label('Mode'), 2, 0)
        ip_layout.addWidget(ip := LineEdit(), 0, 1)
        ip_layout.addWidget(port := LineEdit(), 1, 1)
        ip_layout.addWidget(mode := QComboBox(), 2, 1)

        layout.addWidget(send_write := QGroupBox("Test Send Write"))
        test_layout = QGridLayout(send_write)
        test_layout.addWidget(Label('ADDRESS'), 0, 0)
        test_layout.addWidget(Label('VALUE'), 1, 0)
        test_layout.addWidget(Label('RESULT'), 2, 0)
        test_layout.addWidget(addr := QComboBox(), 0, 1)
        test_layout.addWidget(value := QComboBox(), 1, 1)
        test_layout.addWidget(result := LineEdit(), 2, 1)
        test_layout.addWidget(read := Button('READ'), 3, 0)
        test_layout.addWidget(write := Button('WRITE'), 3, 1)

        # option
        ip_range = "(?:[0-1]?[0-9]?[0-9]|2[0-4][0-9]|25[0-5])"
        ip_regex = QRegExp("^" + ip_range + "\\." + ip_range + "\\." + ip_range + "\\." + ip_range + "$")
        ip_validator = QRegExpValidator(ip_regex, self)
        ip.setValidator(ip_validator)
        port.setValidator(QIntValidator())
        port.setMaxLength(5)
        mode.addItems(['binary', 'ascii'])
        addr.addItems(['B20', 'B21', 'B22', 'B2A', 'B2B', 'B2C'])
        value.addItems(['0', '1'])
        write.setDisabled(True)
        result.setDisabled(True)

        ip.setText('192.168.0.1')
        port.setText('4001')

        # assign
        self.ip = ip
        self.port = port
        self.addr = addr
        self.value = value
        self.mode = mode
        self.value = value
        self.result = result
        self.read_button = read
        self.write_button = write

        # event
        read.clicked.connect(self._read)
        write.clicked.connect(self._write)
        addr.currentIndexChanged.connect(self._change_addr)

        self.show()

        self.pymc3e = pymcprotocol.Type3E()

    def _connect(self):
        self.pymc3e.setaccessopt(commtype=self.mode.currentText())
        self.pymc3e.connect(self.ip.text(), int(self.port.text()))

    @debug_log
    def _read(self):
        try:
            self._connect()
            value = self.pymc3e.batchread_bitunits(headdevice=self.addr.currentText(), readsize=1)
            self.result.setText(str(value[0]))
        except Exception as e:
            self.result.setText(str(type(e)))
        self.pymc3e.close()

    @debug_log
    def _write(self):
        try:
            self._connect()
            self.pymc3e.batchwrite_bitunits(headdevice=self.addr.currentText(), values=[int(self.value.currentText())])
            self.result.setText(f"{self.addr.currentText()}, {self.value.currentText()} : write ok")
        except Exception as e:
            self.result.setText(str(type(e)))
        self.pymc3e.close()

    def _change_addr(self, index):
        if self.addr.currentText() == 'B20':
            self.read_button.setEnabled(True)
            self.write_button.setDisabled(True)
        else:
            self.read_button.setDisabled(True)
            self.write_button.setEnabled(True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MCTester()
    sys.exit(app.exec_())
