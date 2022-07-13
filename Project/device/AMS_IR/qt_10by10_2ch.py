import sys
from threading import Thread

import serial.tools.list_ports
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QDesktopWidget
from serial import Serial, SerialException

# com1 = 'com8'
# com2 = 'com10'
from package.logger import make_logger

com1 = '/dev/ttyUSB0'
com2 = '/dev/ttyUSB1'


class ArrayDisplay(QWidget):
    signalNumberDisplay = pyqtSignal(int)

    def __init__(self):
        super(ArrayDisplay, self).__init__()
        self.logger = make_logger('real_log')
        try:
            self.ser1 = Serial()
            self.ser2 = Serial()
            self.ser1.baudrate = 115200
            self.ser2.baudrate = 115200
            self.ser1.timeout = 2
            self.ser2.timeout = 2
        except SerialException as e:
            self.logger.error(e)
            sys.exit()

        self.values = ['' for _ in range(100)]
        self.buttons = [QPushButton('') for _ in range(100)]
        list(map(lambda x: x.setFixedSize(80, 80), self.buttons))
        self.signalNumberDisplay.connect(self.displayButton)
        self.initUI()
        # self.check_serials()
        # self.startReadThead()

    def check_serial(self, port):
        try:
            ser = Serial(port, 115200, timeout=1)
            ser.readline()
            check_bytes = ser.readline().decode()
            if ser.isOpen():
                ser.close()
            if 'L' in check_bytes:
                self.ser1.port = port
            elif 'R' in check_bytes:
                self.ser2.port = port
        except SerialException:
            self.logger.error('serial Error')

    def check_serials(self):
        while True:
            thread_list = list()
            for s in serial.tools.list_ports.comports():
                th = Thread(target=self.check_serial, args=(s.device,))
                th.start()
                thread_list.append(th)

            for thread in thread_list:
                thread.join()

            if self.ser1.port and self.ser2.port:
                for index in range(100):
                    self.buttons[index].setStyleSheet(f"background-color: gray;"
                                                      f"color: white;"
                                                      f"font-weight: bold")
                return

    def displayButton(self, index):
        self.buttons[index].setText(self.values[index])
        try:
            self.buttons[index].setStyleSheet(f"background-color: {('red', 'blue')[int(self.values[index]) < 1000]};"
                                              f"color: white;"
                                              f"font-weight: bold")
        except ValueError:
            self.logger.error(type(index), index)

    def initUI(self):

        layout = QGridLayout()
        for index, button in enumerate(self.buttons):
            layout.addWidget(button, int(index / 10), int(index % 10))
        self.setLayout(layout)
        self.setWindowTitle('10X10')
        self.show()

        # center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def startReadThead(self):
        self.serialThread1 = Thread(target=self._read, args=(self.ser1,))
        self.serialThread1.daemon = True
        self.serialThread1.start()
        self.serialThread2 = Thread(target=self._read, args=(self.ser2,))
        self.serialThread2.daemon = True
        self.serialThread2.start()

    def _read(self, ser):
        while True:
            try:
                if not ser.isOpen():
                    ser.open()
                character = ser.read().decode()
                if character == 'L':
                    index = -1
                    self.inputDataParsing(character, index, ser)
                elif character == 'R':
                    index = 49
                    self.inputDataParsing(character, index, ser)
                elif character == '':
                    ser.close()
                else:
                    continue
                ser.flushInput()
            except Exception as e:
                self.logger.error(e)

    def inputDataParsing(self, character, index, ser):
        number = ''
        while character != '\n':
            if character == ',':
                if number:
                    self.values[index] = number
                    self.signalNumberDisplay.emit(index)
                number = ''
                index += 1
            elif character.isdigit():
                number += character
            elif character == '':
                ser.close()
                raise SerialException
            character = ser.read().decode()
        self.values[index] = number
        self.signalNumberDisplay.emit(index)

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
ex = ArrayDisplay()
sys.exit(app.exec_())
