import re
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject
from serial import Serial, SerialException

from process_package.defined_variable_function import logger, AIR_LEAK_ATECH, SENSOR_ATECH, AIR_LEAK_KSD, TOUCH, NG, OK


class SerialMachineSignal(QObject):
    machine_result_signal = pyqtSignal(list)
    machine_result_ksd_signal = pyqtSignal(tuple)
    machine_serial_error = pyqtSignal(object)


class SerialMachine(Serial):
    """
    Serial from Machine(Air Leak, IR Sensor)
    """

    def __init__(self, port=None, baudrate=None, timeout=None, serial_name=None):
        super(SerialMachine, self).__init__()

        self.signal = SerialMachineSignal()

        # default serial value + name
        self.port, self.baudrate, self.timeout, self.serial_name = port, baudrate, timeout, serial_name

        self.th = Thread(target=self.air_leak_read_thread, daemon=True)

    def connect_serial(self, port):
        try:
            if self.is_open:
                self.close()
            else:
                self.port = port
                self.open()
                self.flushInput()
                return True
        except SerialException:
            self.signal.machine_serial_error.emit(self)
            logger.error(f"{self.serial_name}, {self.port} : serial connect error!!!")
        return False

    def start_machine_read(self):
        if not self.th.is_alive():
            if self.serial_name == AIR_LEAK_ATECH:
                self.th = Thread(target=self.air_leak_read_thread, daemon=True)
            elif self.serial_name == AIR_LEAK_KSD:
                self.th = Thread(target=self.kds_air_leak_read_thread, daemon=True)
            elif self.serial_name == TOUCH:
                self.th = Thread(target=self.touch_read_thread, daemon=True)
            elif SENSOR_ATECH in self.serial_name:
                self.th = Thread(target=self.ir_sensor_read_thread, daemon=True)
            self.th.start()

    def touch_read_thread(self):
        self.flushInput()
        while self.is_open:
            try:
                if result := self.readline().decode():
                    if "TEST RESULT" in result:
                        if OK in result:
                            self.signal.machine_result_signal.emit([OK])
                        else:
                            self.signal.machine_result_signal.emit([NG])
            except SerialException:
                self.is_open_close()
                self.signal.machine_serial_error.emit(self)
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def ir_sensor_read_thread(self):
        self.flushInput()
        while self.is_open:
            try:
                if result := self.readline().decode().replace('\r', '').replace('\n', '').upper().split(','):
                    self.signal.machine_result_signal.emit([self.serial_name] + result)
            except SerialException:
                self.is_open_close()
                self.signal.machine_serial_error.emit(self)
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def kds_air_leak_read_thread(self):
        self.flushInput()
        while self.is_open:
            try:
                if serial_read_line := self.get_serial_readline_with_decode():
                    self.signal.machine_result_ksd_signal.emit(self.get_channel_and_result(serial_read_line))
            except SerialException:
                self.is_open_close()
                self.signal.machine_serial_error.emit(self)
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def get_channel_and_result(self, read_line):
        split_read_line = read_line.split(',')
        for index, item in enumerate(split_read_line):
            if 'CH' in item:
                return int(item[-1]), split_read_line[index + 1]

    def air_leak_read_thread(self):
        self.flushInput()
        while self.is_open:
            try:
                if result := re.search("[A-Z]{2}", self.readline().decode()):
                    logger.info(result)
                    result = [result.group(0)]
                    self.signal.machine_result_signal.emit(result)
            except SerialException:
                self.is_open_close()
                self.signal.machine_serial_error.emit(self)
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def get_serial_readline_with_decode(self):
        return self.readline().decode().replace('\r', '').replace('\n', '')

    def is_open_close(self):
        if self.is_open:
            self.close()
