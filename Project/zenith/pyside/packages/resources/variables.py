from PySide2.QtSerialPort import QSerialPortInfo

from packages.views.logger import get_logger

MANUAL_AIR_LEAK_UNIT_COUNT = 4

# serial baudrate

BAUDRATE_9600 = 9600
BAUDRATE_115200 = 115200

# get instance
logger = get_logger("My Logger")


# functions
def get_serial_available_list():
    return [port.portName() for port in QSerialPortInfo.availablePorts() if not port.isBusy()]
