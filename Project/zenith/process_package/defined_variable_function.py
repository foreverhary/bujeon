import time
from functools import wraps
from threading import Lock

import qdarkstyle
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import QDesktopWidget

from process_package.logger import get_logger
from process_package.style.style import STYLE

# thread lock
lock = Lock()

logger = get_logger("My Logger")

# Time
CHECK_DB_TIME = 60000
CHECK_DB_UPDATE_TIME = 600000

# size
DM_FONT_SIZE = 25
DM_LABEL_WIDTH_SIZE = 250

QR_PREVIOUS_PROCESS_TEXT_SIZE = 80
QR_DM_MINIMUM_WIDTH_SIZE = 1000
QR_DM_TEXT_SIZE = 170
QR_STATUS_TEXT_SIZE = 50

AIR_LEAK_DM_UNIT_SIZE = 550
AIR_LEAK_RESULT_SIZE = 300
AIR_LEAK_DM_UNIT_FONT_SIZE = 50
AIR_LEAK_RESULT_FONT_SIZE = 100

DEFAULT_FONT_SIZE = 30
PREVIOUS_PROCESS_TEXT_SIZE = 80
RELEASE_GRADE_TEXT_SIZE = 400

SENSOR_RESULT_HEIGHT_SIZE = 350
SENSOR_RESULT_TEXT_SIZE = 100

AUDIO_BUS_GRADE_EDIT_MIN_WIDTH = 130

# config string
POP_SECTION = 'pop'
MSSQL_SECTION = 'mssql'
COMPORT_SECTION = 'com_port'
AUDIO_BUS_SECTION = 'audio_bus'

MSSQL_IP = 'ip'
MSSQL_PORT = 'port'
MSSQL_ID = 'id'
MSSQL_PASSWORD = 'password'
MSSQL_DATABASE = 'database'

NFC_COMPORT_1 = 'nfc_comport_1'
NFC_COMPORT_2 = 'nfc_comport_2'
MACHINE_COMPORT_1 = 'machine_comport_1'
MACHINE_COMPORT_2 = 'machine_comport_2'

ORDER_NUMBER = 'order_number'

GRADE_FILE_PATH = 'grade_file_path'
SUMMARY_FILE_PATH = 'summary_file_path'
A_GRADE_MIN = 'a_min'
A_GRADE_MAX = 'a_max'
B_GRADE_MIN = 'b_min'
B_GRADE_MAX = 'b_max'
C_GRADE_MIN = 'c_min'
C_GRADE_MAX = 'c_max'

# color
WHITE = 'white'
BLUE = 'blue'
RED = 'red'
YELLOW = 'yellow'
GREEN = 'green'
LIGHT_SKY_BLUE = 'lightskyblue'
LIGHT_YELLOW = 'lightyellow'

# string
DATA_MATRIX = "DATA MATRIX"
PREVIOUS_PROCESS = "PREVIOUS PROCESS"
PREVIOUS_PROCESS_OK = "PREVIOUS PROCESS OK"
PREVIOUS_PROCESS_NG = "PREVIOUS PROCESS NG"
TRY_NEXT_QR_SCAN = "TRY NEXT QR SCAN"
WRITE_DONE = "WRITE DONE"
TAG_NFC_ZIG = "TAG NFC ZIG"
READY_TO_QR_SCAN = "READY TO QR SCAN!!"
CHECK_NFC_RESTART_PROGRAM = "CHECK NFC & RESTART PROGRAM!!"

GRADE = "GRADE"

STATUS = 'STATUS'
READY = 'READY'
RESULT = 'RESULT'
OK = 'OK'
NG = 'NG'
A = 'A'
B = 'B'
C = 'C'
WRITE = 'WRITE'
UNIT = 'UNIT'
DONE = 'DONE'
PASS = "PASS"
FAIL = 'FAIL'

NULL = 'NULL'

AIR_LEAK_PROCESS = 'AIR'
MIC_PROCESS = 'MIC'
FUNCTION_PROCESS = 'FUN'
SENSOR_PROCESS = 'SEN'

AIR_LEAK_PREPROCESS = ()
MIC_PREPROCESS = (AIR_LEAK_PROCESS)
FUNCTION_PREPROCESS = (AIR_LEAK_PROCESS, MIC_PROCESS)
SENSOR_PREPROCESS = (AIR_LEAK_PROCESS, MIC_PROCESS, FUNCTION_PROCESS)

PROCESS_SEQUENCE = [AIR_LEAK_PROCESS,
                    MIC_PROCESS,
                    FUNCTION_PROCESS]
PROCESS_RESULTS = (OK, NG, A, B, C)
PROCESS_OK_RESULTS = (OK, A, B, C)
PROCESS_NAMES = (AIR_LEAK_PROCESS, MIC_PROCESS, FUNCTION_PROCESS, SENSOR_PROCESS)
PROCESS_FULL_NAMES = {
    AIR_LEAK_PROCESS: 'AIR LEAK',
    MIC_PROCESS: 'MIC',
    FUNCTION_PROCESS: 'FUNCTION',
    SENSOR_PROCESS: 'SENSOR'
}

AIR_LEAK_ATECH = 'atech_air_leak'
AIR_LEAK_KSD = 'ksd_air_leak'
SENSOR_ATECH = 'sensor'

NFC_IN = 'NFCIN'
NFC = 'NFC'

# file name
CONFIG_FILE_NAME = 'config.ini'
SAVE_DB_FILE_NAME = './log/save_db.log'
SAVE_DB_RETRY_FILE_NAME = './log/save_db_retry.log'

# touch
TOUCH = 'TOUCH'

# AIR LEAK
AIR_LEAK_UNIT_COUNT = 4
AIR_LEAK = 'AIR LEAK'

# MIC
MIC = 'MIC'

# AUDIO BUS
VALID_GRADE = (A, B, C)
FUNCTION = 'FUNCTION'
SPL = 'SPL'
THD = 'THD'
IMP = 'IMP'
MIC_FRF = 'MIC FRF'
RUB_BUZ = 'R&B'
HOHD = 'HOHD'
POLARITY = 'POLARITY'
AUD = 'AUD'

# SENSOR
SENSOR = 'SENSOR'
CON_OS = 'CON O/S'
POGO_OS = 'POGO O/S'
VBAT_ID = 'VBAT ID'
C_TEST = 'C TEST'
LED = 'LED'
PCM = 'PCM'
PROX_TEST = 'PROX TEST'
BATTERY = 'BATTERY'
MIC = 'MIC'
Hall_IC = 'Hall IC'

# Beep
FREQ = 2500
DUR = 200


def window_center(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())


def window_bottom_left(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().bottomLeft()
    qr.moveBottomLeft(cp)
    window.move(qr.topLeft())


def window_right(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().bottomRight()
    qr.moveBottomRight(cp)
    window.move(qr.topLeft())


def window_top_left(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().topLeft()
    qr.moveTopLeft(cp)
    window.move(qr.topLeft())


def style_sheet_setting(app):
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f'{func.__name__}({args!r}, {kwargs!r}')
        result = func(*args, **kwargs)
        logger.debug(f'{func.__name__} -> {result!r}')
        return result

    return wrapper
