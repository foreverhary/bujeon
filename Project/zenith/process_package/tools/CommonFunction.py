from PySide2.QtSerialPort import QSerialPortInfo
from winsound import Beep

from process_package.resource.string import PROCESS_NAMES_WITHOUT_AIR_LEAK
from process_package.tools.logger import get_logger

logger = get_logger("My Logger")


def get_serial_available_list():
    return [port.portName()
            for port in QSerialPortInfo.availablePorts()
            if not port.isBusy()]


def read_beep():
    Beep(2500, 200)


def write_beep():
    Beep(3500, 200)


def is_bit_in_one_byte(one_byte, num, bit):
    return not (bool((one_byte or 0x80) & (1 << num)) ^ bit)


def input_bit_in_one_byte(one_byte, num, value) -> bytes:
    return (((one_byte or 0x80) & (0xff - (1 << num))) | (value << num)).to_bytes(1, byteorder='little')


def get_bit_in_one_byte(one_byte, num) -> bool:
    return bool((one_byte or 0x80) & (1 << num))


def is_result_in_nfc(obj, byte, bit):
    return is_bit_in_one_byte(byte, PROCESS_NAMES_WITHOUT_AIR_LEAK.index(obj.process_name), bit)


def get_write_result_in_nfc(obj, byte, bit):
    return input_bit_in_one_byte(byte, PROCESS_NAMES_WITHOUT_AIR_LEAK.index(obj.process_name), bit)

