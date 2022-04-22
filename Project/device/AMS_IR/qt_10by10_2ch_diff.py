import sys
from threading import Thread, Lock, Timer

import numpy as np
from PyQt5.QtCore import pyqtSignal, QThreadPool, QCoreApplication
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QDesktopWidget
from serial import Serial, SerialException
import serial.tools.list_ports

from logger import make_logger

com1 = 'com5'
com2 = 'com9'
com3 = 'com6'
# com1 = '/dev/ttyUSB0'
# com2 = '/dev/ttyUSB1'
# com3 = '/dev/ttyUSB2'

lock = Lock()


class ArrayDisplay(QWidget):
    signalDisplay = pyqtSignal()
    signalRealTimeDisplay = pyqtSignal(list)
    serSwitchThread: QThreadPool

    def __init__(self):
        super(ArrayDisplay, self).__init__()

        self.logger = make_logger('diff_log')
        self.ser1 = Serial()
        self.ser2 = Serial()
        self.ser_switch = Serial()
        self.ser1.baudrate = 115200
        self.ser2.baudrate = 115200
        self.ser_switch.baudrate = 115200
        self.ser1.timeout = 2
        self.ser2.timeout = 2
        self.ser_switch.timeout = 2

        self.switch_value = 0
        self.buttons = [QPushButton('') for _ in range(100)]
        list(map(lambda x: x.setFixedSize(80, 80), self.buttons))

        self.left_array = list()
        self.right_array = list()
        self.signalDisplay.connect(self.displayDiff)
        self.signalRealTimeDisplay.connect(self.displayRealTime)
        self.initUI()

        self.check_serials()
        self.serSwitchThread = Thread(target=self._switch_read)
        self.serSwitchThread.daemon = True
        self.serSwitchThread.start()

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
            elif not check_bytes:
                pass
            else:
                if check_bytes.split('\r\n')[0] == '0' or check_bytes.split('\r\n')[0] == '1':
                    self.ser_switch.port = port
                    self.logger.debug(port)
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

            if self.ser1.port and self.ser2.port and self.ser_switch.port:
                for index in range(100):
                    self.buttons[index].setStyleSheet(f"background-color: gray;"
                                                      f"color: white;"
                                                      f"font-weight: bold")
                return

    def _read_serial(self, side, v):
        arrays = list()
        ser = self.__getattribute__(f'ser{side + 1}')
        while arrays.__len__() != 10:

            if not ser.isOpen():
                ser.open()
                ser.flushInput()

            while True:
                try:
                    array = ser.readline().decode().replace('\r\n', '').split(',')
                    if array.__len__ == 0:
                        ser.close()
                    if array.__len__() != 51:
                        continue
                    break
                except UnicodeDecodeError as e:
                    self.logger.error(e)
                except Exception as e:
                    self.logger.error(e)
            sideText = array[0]
            self.signalRealTimeDisplay.emit(array)
            array = list(map(int, array[1:]))

            arrays.append(array)
        if ser.isOpen():
            ser.close()
        arrays = np.array(arrays)
        arrays = arrays.mean(axis=0)
        if sideText == 'L':
            self.left_array = list(map(int, arrays.tolist()))
        elif sideText == 'R':
            self.right_array = list(map(int, arrays.tolist()))

    def displayRealTime(self, array):
        if array[0] == 'L':
            for index, value in zip(range(50), array[1:]):
                self.displayButton(index, value, 'blue')
        elif array[0] == 'R':
            for index, value in zip(range(50, 100), array[1:]):
                self.displayButton(index, value, 'blue')

    def displayDiff(self):
        if self.switch_value == 1:
            arrays = list(map(str, self.close_arrays))
            for index, value in enumerate(arrays):
                self.displayButton(index, value, 'green')
        elif self.switch_value == 0:
            for index in range(100):
                self.displayButtonResult(index)

    def displayButton(self, index, value, color):
        self.buttons[index].setText(value)
        try:
            self.buttons[index].setStyleSheet(f"background-color: {color};"
                                              f"color: white;"
                                              f"font-weight: bold")
        except ValueError:
            self.logger.error(type(index), index)

    def displayButtonResult(self, index):
        self.buttons[index].setText(f"O: {self.open_arrays[index]}\n"
                                    f"D: {self.diff_arrays[index]}")
        if (120 <= int(self.open_arrays[index]) <= 3500) and (600 <= int(self.diff_arrays[index]) <= 4000):
            result_color = 'blue'
        else:
            result_color = 'red'
        try:
            self.buttons[index].setStyleSheet(f"background-color: {result_color};"
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

    def _switch_read(self):
        while True:
            try:
                if not self.ser_switch.isOpen():
                    self.ser_switch.open()
                self.ser_switch.flushInput()
                if self.ser_switch.readline() == b'':
                    self.ser_switch.close()
                    continue
                readLineTmp = self.ser_switch.readline()
                if readLineTmp != b'1\r\n' and readLineTmp != b'0\r\n':
                    continue
                switch = int(readLineTmp.decode().split('\r\n')[0])
                if switch != 0 and switch != 1:
                    self.logger.debug('serial close')
                    self.ser_switch.close()
                    continue
                if switch != self.switch_value:
                    self.logger.debug(f"{switch}, {self.switch_value}")
                    try:
                        if self.left_thread.is_alive() or self.right_thread.is_alive():
                            continue
                    except Exception as e:
                        self.logger.error(e)
                    self.switch_value = switch
                    self.left_thread = Thread(target=self._read_serial, args=(0, self.switch_value))
                    self.left_thread.start()
                    self.right_thread = Thread(target=self._read_serial, args=(1, self.switch_value))
                    self.right_thread.start()
                    self.left_thread.join()
                    self.right_thread.join()

                    arrays = self.left_array + self.right_array
                    if self.switch_value == 1:
                        self.close_arrays = arrays
                    else:
                        self.open_arrays = arrays
                        arrays = np.array(self.close_arrays) - np.array(self.open_arrays)
                        self.diff_arrays = list(map(str, arrays.tolist()))
                        self.open_arrays = list(map(str, self.open_arrays))

                    self.signalDisplay.emit()
            except Exception as e:
                self.logger.error(e)

    def closeEvent(self, event):
        print('shutdown')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArrayDisplay()
    sys.exit(app.exec_())
