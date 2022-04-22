import sys
import time
from random import choice
from threading import Thread

import serial
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton
from serial import Serial

from process_package.style.style import STYLE


class SendOK(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(layout := QHBoxLayout())
        layout.addWidget(button := QPushButton('OK'))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')
        layout.addWidget(button := QPushButton('NG'))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')
        layout.addWidget(button := QPushButton('AU'))
        button.clicked.connect(self.send)
        button.setStyleSheet('font-size: 200px')

        self.ser = Serial()
        self.ser.port = 'com5'
        self.ser.baudrate = 9600
        self.setLayout(layout)
        self.show()

    def send(self):
        text = self.sender().text()
        try:
            if not self.ser.isOpen():
                self.ser.open()
            if 'AU' in text:
                if hasattr(self, 'serialThread') and self.serialThread.is_alive():
                    self.ser.close()
                else:
                    self.threadStart()
            else:
                self.ser.write(f'x:({("<06>:(NG):-  0.1 Pa/s", "<06>:(OK):-  0.1 Pa/s")[text == "OK"]})\n'.encode())
        except serial.SerialException as e:
            print(e)
            sys.exit(self.close())

    def threadStart(self):
        self.serialThread = Thread(target=self.autoSend)
        self.serialThread.start()

    def autoSend(self):
        print('start auto send')
        try:
            while True:
                read_line = self.ser.readline()
                print(read_line)
                time.sleep(5)
                self.ser.write(f"x:({choice(['NG', 'OK'])})\n".encode())

        except Exception as e:
            print(e)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SendOK()
    app.setStyleSheet(STYLE)
    sys.exit(app.exec_())
