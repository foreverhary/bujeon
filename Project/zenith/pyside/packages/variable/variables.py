from serial import Serial, SerialException

from packages.component.logger import get_logger
import serial.tools.list_ports

MANUAL_AIR_LEAK_UNIT_COUNT = 4

# serial baudrate

BAUDRATE_9600 = 9600
BAUDRATE_115200 = 115200

# get instance
logger = get_logger("My Logger")


# functions
def get_serial_available_list():
    serial_ports = [s.device for s in serial.tools.list_ports.comports()]
    available_serial_list = []
    for port in serial_ports:
        try:
            s = Serial(port)
            available_serial_list.append(port)
            s.close()
        except SerialException:
            pass
    return available_serial_list
