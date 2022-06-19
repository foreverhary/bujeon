import time
from functools import wraps
from threading import Lock

import qdarkstyle
from PySide2.QtGui import QFontDatabase, QFont
from PySide2.QtWidgets import QDesktopWidget, QMessageBox

from process_package.resource.style import STYLE

# thread lock
lock = Lock()




# size
DM_FONT_SIZE = 25
DM_LABEL_WIDTH_SIZE = 250

QR_PREVIOUS_PROCESS_TEXT_SIZE = 80
QR_DM_MINIMUM_WIDTH_SIZE = 1000
QR_DM_TEXT_SIZE = 170
QR_STATUS_TEXT_SIZE = 50

AIR_LEAK_DM_UNIT_WIDTH_SIZE = 600
AIR_LEAK_DM_UNIT_HEIGHT_SIZE = 500
AIR_LEAK_RESULT_SIZE = 300
AIR_LEAK_DM_UNIT_FONT_SIZE = 50
AIR_LEAK_RESULT_FONT_SIZE = 100

PREVIOUS_PROCESS_TEXT_SIZE = 80
RELEASE_GRADE_TEXT_SIZE = 250

SENSOR_RESULT_HEIGHT_SIZE = 350
SENSOR_RESULT_TEXT_SIZE = 100

AUDIO_BUS_GRADE_EDIT_MIN_WIDTH = 130


# string
DATA_MATRIX = "DATA MATRIX"
PREVIOUS_PROCESS = "PREVIOUS PROCESS"
PREVIOUS_PROCESS_OK = "PREVIOUS PROCESS OK"
PREVIOUS_PROCESS_NG = "PREVIOUS PROCESS NG"
TRY_NEXT_QR_SCAN = "TRY NEXT QR SCAN"
WRITE_DONE = "WRITE DONE"
TAG_NFC_JIG = "TAG NFC JIG"
READY_TO_QR_SCAN = "READY TO QR SCAN!!"
CHECK_NFC_RESTART_PROGRAM = "CHECK NFC & RESTART PROGRAM!!"


AIR_LEAK_PROCESS = 'AIR'
MIC_PROCESS = 'MIC'
FUNCTION_PROCESS = 'FUN'
SENSOR_PROCESS = 'SEN'

AIR_LEAK_PREVIOUS_PROCESS = ()
MIC_PREVIOUS_PROCESS = (AIR_LEAK_PROCESS)
FUNCTION_PREVIOUS_PROCESS = (AIR_LEAK_PROCESS, MIC_PROCESS)
SENSOR_PREVIOUS_PROCESS = (AIR_LEAK_PROCESS, MIC_PROCESS, FUNCTION_PROCESS)

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

AIR_LEAK_KSD = 'ksd_air_leak'
SENSOR_ATECH = 'sensor'

NFC_IN = 'NFCIN'
NFC = 'NFC'
NFCIN1 = 'NFCIN1'
NFCIN2 = 'NFCIN2'
NFC1 = 'NFC1'
NFC2 = 'NFC2'
NFC3 = 'NFC3'
NFC4 = 'NFC4'
NFC5 = 'NFC5'
NFC6 = 'NFC6'
NFC7 = 'NFC7'
NFC8 = 'NFC8'
AUDIO_BUS_NFC = (NFCIN1, NFC1, NFC2)

# file name


# AIR LEAK
AIR_LEAK_UNIT_COUNT = 4


# MIC


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

