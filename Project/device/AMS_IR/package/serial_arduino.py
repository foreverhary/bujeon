from threading import Thread, Timer

from PySide2.QtCore import QTimer, Signal
from PySide2.QtWidgets import QPushButton
from serial import Serial, SerialException

from package.logger import logger


class SerialArduinoButton(QPushButton):
    out_data = Signal(str)
    connection_signal = Signal(bool)

    def __init__(self, port, baudrate):
        super(SerialArduinoButton, self).__init__()
        self.serial = Serial(port, baudrate)
        self.serial.timeout = 0.2
        self.setText(port)
        self.start_serial_thread()
        self.background_color = ''
        # self.thread = Thread(target=self.read_serial, daemon=True)
        # self.thread.start()
        # self.open_timer = QTimer(self)
        # self.open_timer.start(50)
        # self.open_timer.timeout.connect(self.open)
        # self.timer = QTimer(self)
        # self.timer.timeout.connect(self.start_serial_thread)

    def start_serial_thread(self):
        self.thread = Timer(1.5, self.read_serial)
        self.thread.daemon = True
        self.thread.start()
        # self.timer.stop()
        # self.thread = Thread(target=self.read_serial, daemon=True)
        # self.thread.start()

    def toggle_background_color(self):
        if self.background_color == 'lightskyblue':
            self.set_background_color('yellow')
        else:
            self.set_background_color('lightskyblue')

    def set_background_color(self, color):
        self.background_color = color
        self.setStyleSheet(f"background-color: {color};")

    def is_open(self):
        if self.serial.is_open:
            self.set_background_color('lightskyblue')
            if not self.thread.is_alive():
                self.timer.start(2000)
                # self.thread = Thread(target=self.read_serial, daemon=True)
                # self.thread.start()
        else:
            self.set_background_color('red')
            try:
                self.serial.open()
                if not self.thread.is_alive():
                    self.timer.start(2000)
            except:
                pass

        self.connection_signal.emit(self.serial.isOpen)

    def set_port(self, value):
        self.serial.port = value

    def get_port(self):
        return self.seril.port

    def open(self):
        try:
            if not self.serial.is_open:
                self.serial.open()
        except:
            pass
        self.is_open()

    def dtr_bridge(self):
        self.serial.dtr = True
        self.start_serial_thread()

    def read_serial(self):
        while True:
            try:
                if not (line_data := self.serial.readline().decode().replace('\n', '').replace('\r', '')):
                    self.serial.dtr = False
                    thread = Timer(0.5, self.dtr_bridge)
                    thread.daemon = True
                    thread.start()
                    break
                if line_data[0] not in ['L', 'R', '1', '0']:
                    raise UnicodeDecodeError
                if line_data:
                    self.out_data.emit(line_data)
            except UnicodeDecodeError:
                continue
            except TypeError as e:
                logger.debug(type(e))
            except SerialException as e:
                logger.debug(f"{type(e)} : {e}")
                if self.serial.is_open:
                    self.serial.close()
                break
            except Exception as e:
                logger.debug(f"{type(e)} : {e}")
                continue
