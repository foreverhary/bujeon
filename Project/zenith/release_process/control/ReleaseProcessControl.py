from PySide2.QtCore import QObject, Signal, Slot

from process_package.resource.string import STR_NFC, STR_DATA_MATRIX, PROCESS_OK_RESULTS, PROCESS_NAMES, STR_FUN, \
    STR_MISS, PROCESS_FULL_NAMES, STR_NG
from process_package.tools.CommonFunction import logger, read_beep
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.SerialPort import SerialPort

