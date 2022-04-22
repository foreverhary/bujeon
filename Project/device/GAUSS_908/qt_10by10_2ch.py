import sys
from threading import Thread, Lock

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QDesktopWidget
from serial import Serial, SerialException

#com1 = 'com8'
#com2 = 'com10'
com1 = '/dev/ttyUSB0'
com2 = '/dev/ttyUSB1'

lock = Lock()


class ArrayDisplay(QWidget):
    signalNumberDisplay = pyqtSignal(int)

    def __init__(self):
        super(ArrayDisplay, self).__init__()

        try:
            self.ser1 = Serial()
            self.ser2 = Serial()
            self.ser1.port = com1
            self.ser2.port = com2
            self.ser1.baudrate = 115200
            self.ser2.baudrate = 115200
            self.ser1.timeout = 2
            self.ser2.timeout = 2
        except SerialException as e:
            print(e)
            sys.exit()

        self.values = ['' for _ in range(100)]
        self.buttons = [QPushButton('') for _ in range(100)]
        list(map(lambda x: x.setFixedSize(80, 80), self.buttons))
        self.signalNumberDisplay.connect(self.displayButton)
        self.initUI()
        self.startReadThead()

    def displayButton(self, index):
        self.buttons[index].setText(self.values[index])
        try:
            self.buttons[index].setStyleSheet(f"background-color: {('red', 'blue')[int(self.values[index]) < 10000]};"
                                              f"color: white;"
                                              f"font-weight: bold")
        except ValueError:
            print(type(index), index)

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
        self.serialThread1.start()
        self.serialThread2 = Thread(target=self._read, args=(self.ser2,))
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
                    pass
                elif character == '':
                    ser.close()
                else:
                    continue
                ser.flushInput()
            except Exception as e:
                print(e)

    def inputDataParsing(self, character, index, ser):
        number = ''
        while character != '\n':
            if character == ',':
                if number:
                    #self.values[index] = str(int(int(number)/256))
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
        #self.values[index] = str(int(int(number)/256))
        self.values[index] = number
        self.signalNumberDisplay.emit(index)

    def closeEvent(self, event):
        self.serialTimer.cancel()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArrayDisplay()
    sys.exit(app.exec_())
