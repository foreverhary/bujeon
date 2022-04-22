from threading import Thread

from PyQt5.QtCore import QObject, pyqtSignal
from serial import Serial, SerialException


class SerialSignal(QObject):
    probe_signal = pyqtSignal(object)
    stop_signal = pyqtSignal()


class SerialGauss(Serial):

    def __init__(self, port=None, baudrate=None, serial_name=None):
        super(SerialGauss, self).__init__()
        self.port, self.baudrate, self.serial_name = port, baudrate, serial_name
        self.timeout = 0.5
        self.signal = SerialSignal()
        self.thread = Thread(target=self.read_each_thread, daemon=True)
        self.thread_stop = False

    def start_thread(self):
        if not self.thread.is_alive():
            self.thread_stop = False
            self.thread = Thread(target=self.read_each_thread, daemon=True)
            self.thread.start()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if isinstance(value, list):
            self._value = [int(value[0]), int(float(value[1]))]
            self.signal.probe_signal.emit(self)

    def read_each_thread(self):
        while True:
            try:
                if not self.readline().decode():
                    break
                if value := self.readline().decode().split(':'):
                    self.value = value
                if self.thread_stop:
                    break
            except SerialException:
                print('serial each error', self.serial_name)
                self.signal.stop_signal.emit()
            except Exception as e:
                print(e)


def p(object):
    print(object)


if __name__ == '__main__':
    s = SerialGauss(port='com6', baudrate=115200, serial_name=1)
    # s.signal.connect(p)
    while True:
        pass
