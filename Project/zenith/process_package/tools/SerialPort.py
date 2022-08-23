from threading import Thread

from PySide2.QtCore import Signal, QObject
from serial import Serial, SerialException

from process_package.tools.CommonFunction import logger


class SerialPort(QObject):
    line_out_signal = Signal(str)
    line_out_without_decode_signal = Signal(bytes)
    serial_connection_signal = Signal(bool)

    def set_port(self, port):
        self.port = port

    def set_baudrate(self, value):
        self.baudrate = value

    def open(self):
        self._serial.open()
        if not self.thread.is_alive():
            self.thread = Thread(target=self.read_line_data, daemon=True)
            self.thread.start()
        self.serial_connection_signal.emit(True)

    def write(self, value):
        if self._serial.is_open:
            if isinstance(value, str):
                self._serial.write(value.encode())
            if isinstance(value, bytes):
                self._serial.write(value)

    def connect_toggle(self):
        if self._serial.is_open:
            self._serial.close()
        else:
            try:
                self.open()
            except SerialException:
                self.is_open_close()
        return self.is_open

    def set_dtr(self, value):
        if not value:
            self.write('\x27')
        self._serial.dtr = value

    def get_dtr(self):
        return self._serial.dtr

    def __init__(self):
        super(SerialPort, self).__init__()
        self._serial = Serial()
        self.thread = Thread(target=self.read_line_data, daemon=True)
        self.out = ''

    @property
    def is_open(self):
        return self._serial.is_open

    @is_open.setter
    def is_open(self, value):
        self._serial.is_open = value

    @property
    def port(self):
        return self._serial.port

    @port.setter
    def port(self, value):
        self._serial.port = value

    @property
    def baudrate(self):
        return self._serial.baudrate

    @baudrate.setter
    def baudrate(self, value):
        self._serial.baudrate = value

    def read_line_data(self):
        while True:
            try:
                tmp_data = self._serial.readline().replace(b'\r', b'').replace(b'\n', b'').replace(b'\x00', b'').replace(
                        b'\x02', b'')
                if self.out != tmp_data:
                    logger.debug(f"{self._serial.port} : {tmp_data}")
                self.out = tmp_data
                self.line_out_signal.emit(self.out.decode())
            except UnicodeDecodeError:
                self.line_out_without_decode_signal.emit(self.out)
            except Exception as e:
                logger.error(f"{self._serial.port}, {type(e)} : {e}")
                self.is_open_close()
                break

    def is_open_close(self):
        if self._serial.is_open:
            self.serial_connection_signal.emit(False)
            self._serial.close()
#
# class SerialaPort(QSerialPort):
#     line_out_signal = Signal(str)
#
#     def __init__(self, name):
#         super(SerialPort, self).__init__()
#         self.name = name
#         self.readyRead.connect(self.receive)
#         self.errorOccurred.connect(self.receive_error)
#
#     def set_port_baudrate(self, port, baudrate):
#         self.setPortName(port)
#         self.setBaudRate(baudrate)
#
#     @Slot()
#     def receive_error(self, e):
#         if e in [QSerialPort.SerialPortError.PermissionError,
#                  QSerialPort.SerialPortError.DeviceNotFoundError]:
#             self.close()
#             self.line_out_signal.emit("error")
#
#     @Slot()
#     def receive(self):
#         while self.canReadLine():
#             self.line_out_signal.emit(
#                 self.readLine().data().decode().replace('\r', '').replace('\n', '')
#             )
#
#     def write(self, text):
#         super().write(text.encode())
#
#     def open(self):
#         return super().open(QIODevice.ReadWrite)
#
#     def reset_dtr(self):
#         self.setDataTerminalReady(False)
#         self.setDataTerminalReady(True)
#
#     def connect_toggle(self):
#         return self.close() if self.isOpen() else self.open()
