from serial import Serial


class SerialMachine(Serial):
    def __init__(self, port=None, baudrate=None, timeout=None, serial_name=None):
        super(SerialMachine, self).__init__()
        self.port, self.baudrate, self.timeout, self.serial_name = port, baudrate, timeout, serial_name

        