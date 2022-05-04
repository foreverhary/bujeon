import re
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject
from serial import Serial, SerialException

from process_package.defined_variable_function import logger, AIR_LEAK_ATECH, SENSOR_ATECH, AIR_LEAK_KSD


class SerialMachineSignal(QObject):
    machine_result_signal = pyqtSignal(list)


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

    def connect_with_button_color(self, port, button):
        try:
            if self.is_open:
                self.close()
                button.set_clicked('red')
            else:
                self.port = port
                self.open()
                button.set_clicked('blue')
                self.flushInput()
                return True
        except SerialException:
            button.set_clicked('red')
            logger.error(f"{self.serial_name}, {self.port} : serial connect error!!!")
        return False

    def start_machine_read(self):
        if not self.th.is_alive():
            if self.serial_name == AIR_LEAK_ATECH:
                self.th = Thread(target=self.air_leak_read_thread, daemon=True)
            elif self.serial_name == AIR_LEAK_KSD:
                self.th = Thread(target=self.air_leak_read_thread, daemon=True)
            elif SENSOR_ATECH in self.serial_name:
                self.th = Thread(target=self.ir_sensor_read_thread, daemon=True)
            self.th.start()

    def ir_sensor_read_thread(self):
        self.flushInput()
        while True:
            try:
                if result := self.readline().decode().replace('\r', '').replace('\n', '').upper().split(','):
                    self.signal.machine_result_signal.emit(result)
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def kds_air_leak_read_thread(self):
        self.flushInput()
        while True:
            if result := self.readline().decode().replace('\r', '').replace('\n', ''):
                logger.debug(result)


    def air_leak_read_thread(self):
        self.flushInput()
        while True:
            try:
                if result := re.search("[A-Z]{2}", self.readline().decode()):
                    logger.info(result)
                    result = [result.group(0)]
                    self.signal.machine_result_signal.emit(result)
            except SerialException:
                self.is_open_close()
                break

    def is_open_close(self):
        if self.is_open:
            self.close()
