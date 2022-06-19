from PySide2.QtCore import Slot, Signal, QIODevice
from PySide2.QtSerialPort import QSerialPort


class SerialPort(QSerialPort):
    line_out_signal = Signal(str)

    def __init__(self, name):
        super(SerialPort, self).__init__()
        self.name = name
        self.readyRead.connect(self.receive)
        self.errorOccurred.connect(self.receive_error)

    def set_port_baudrate(self, port, baudrate):
        self.setPortName(port)
        self.setBaudRate(baudrate)

    @Slot()
    def receive_error(self, e):
        if e in [QSerialPort.SerialPortError.PermissionError,
                 QSerialPort.SerialPortError.DeviceNotFoundError]:
            self.close()
            self.line_out_signal.emit("error")

    @Slot()
    def receive(self):
        while self.canReadLine():
            self.line_out_signal.emit(
                self.readLine().data().decode().replace('\r', '').replace('\n', '')
            )

    def write(self, text):
        super().write(text.encode())

    def open(self):
        return super().open(QIODevice.ReadWrite)

    def reset_dtr(self):
        self.setDataTerminalReady(False)
        self.setDataTerminalReady(True)

    def connect_toggle(self):
        return self.close() if self.isOpen() else self.open()
