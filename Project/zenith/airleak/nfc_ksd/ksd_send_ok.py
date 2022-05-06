import sys
import time
from random import choice
from threading import Thread

import serial
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
from serial import Serial

from process_package.defined_variable_function import OK, NG
from process_package.style.style import STYLE

NFC_COUNT = 4


class SendOK(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(layout := QHBoxLayout())
        layout.addWidget(button := QPushButton(OK))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')
        layout.addWidget(button := QPushButton(NG))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')
        layout.addWidget(button := QPushButton('ODD'))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')
        layout.addWidget(button := QPushButton('EVEN'))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')

        self.ser = Serial()
        self.ser.port = 'com5'
        self.ser.baudrate = 38400
        self.setLayout(layout)
        self.show()

    def send(self):
        text = self.sender().text()
        try:
            if not self.ser.isOpen():
                self.ser.open()
            if OK in text:
                result = ['OK' for _ in range(NFC_COUNT)]
            elif NG in text:
                result = ['NG' for _ in range(NFC_COUNT)]
            elif 'ODD' in text:
                result = []
                for i in range(NFC_COUNT):
                    if i % 2:
                        result.append(NG)
                    else:
                        result.append(OK)
            elif 'EVEN' in text:
                result = []
                for i in range(NFC_COUNT):
                    if i % 2 == 0:
                        result.append(NG)
                    else:
                        result.append(OK)
            msg = ''.join(
                f"dslkfjds,CH{index+1},{value},ksdfoiwejf,weaoifjisj\r\n"
                for index, value in enumerate(result)
            )

            self.ser.write(msg.encode())
        except serial.SerialException as e:
            print(e)
            sys.exit(self.close())

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SendOK()
    app.setStyleSheet(STYLE)
    sys.exit(app.exec_())
