# path
from process_package.resource.color import WHITE, YELLOW, GREEN

CONFIG_FILE_NAME = 'config.ini'
SAVE_DB_FILE_NAME = './log/save_db.log'
SAVE_DB_RETRY_FILE_NAME = './log/save_db_retry.log'

# simple string upper

STR_MATCHING = "MATCHING"
STR_MIC: str = 'MIC'
STR_TOUCH = "TOUCH"
STR_AIR = "AIR"
STR_FUN = "FUN"
STR_FUNCTION = "FUNCTION"
STR_SEN = "SEN"
STR_AIR_LEAK = 'AIR LEAK'
STR_RELEASE = 'RELEASE'
STR_AUTO_AIR_LEAK = "AUTO AIR LEAK"
STR_SENSOR = "SENSOR"
STR_NFC = "NFC"
STR_NFC1 = "NFC1"
STR_NFC2 = "NFC2"
STR_NFCIN = "NFCIN"
STR_NFCIN1 = "NFCIN1"

STR_GRADE = "GRADE"
STR_MISS = 'MISS'

STR_STATUS = 'STATUS'
STR_READY = 'READY'
STR_RESULT = 'RESULT'
STR_OK = 'OK'
STR_NG = 'NG'
STR_A = 'A'
STR_B = 'B'
STR_C = 'C'
STR_UNIT = 'UNIT'
STR_DONE = 'DONE'

STR_PASS = "PASS"
STR_FAIL = 'FAIL'

STR_NULL = 'NULL'

STR_UID = "UID"

STR_SPL = 'SPL'
STR_THD = 'THD'
STR_IMP = 'IMP'
STR_MIC_FRF = 'MIC FRF'
STR_RUB_BUZ = 'R&B'
STR_HOHD = 'HOHD'
STR_POLARITY = 'POLARITY'
STR_AUD = "AUD"

STR_F0 = 'F0'
STR_R_AND_B = 'R&B'
STR_CURRENT = 'CURRENT'
STR_SNR = 'SNR'
STR_NOISE_LEVEL = 'NOISE LEVEL'
STR_FRF = 'FRF'

STR_SENSOR = 'SENSOR'
STR_CON_OS = 'CON O/S'
STR_POGO_OS = 'POGO O/S'
STR_VBAT_ID = 'VBAT ID'
STR_C_TEST = 'C TEST'
STR_LED = 'LED'
STR_PCM = 'PCM'
STR_PROX_TEST = 'PROX TEST'
STR_BATTERY = 'BATTERY'
STR_MIC = 'MIC'
STR_HALL_IC = 'Hall IC'

STR_MACHINE_COMPORT = "MACHINE COMPORT"
STR_ORDER_NUMBER = "ORDER NUMBER"
STR_DATA_MATRIX: str = "DATA MATRIX"
STR_DATA_MATRIX_WAITING = "DATA MATRIX WAITING"
STR_MACHINE_RESULT = "MACHINE RESULT"
STR_STATUS = "STATUS"
STR_DISCONNECT = "DISCONNECT"
STR_RECONNECT = "RECONNECT"

STR_TOUCH_PROCESS = "TOUCH PROCESS"

STR_PREVIOUS_PROCESS = "PREVIOUS PROCESS"
STR_QR_MATCHING = "QR MATCHING"

STR_WRITE_STATUS = "WRITE STATUS"

# sentence
STR_READY_TO_QR_SCAN = "READY TO QR SCAN!!"
STR_WRITE_DONE_SCAN_NEXT_QR = "WRITE DONE SCAN NEXT QR"
STR_INSERT_ORDER_NUMBER = "INSERT ORDER NUMBER"
STR_WAIT_FOR_MACHINE_RESULT = "WAIT FOR MACHINE RESULT"

STR_PREVIOUS_PROCESS_OK = "PREVIOUS PROCESS OK"
STR_PREVIOUS_PROCESS_NG = "PREVIOUS PROCESS NG"
STR_TRY_NEXT_QR_SCAN = "TRY NEXT QR SCAN"
STR_WRITE_DONE = "WRITE DONE"
STR_TAG_NFC_JIG = "TAG NFC JIG"

# config string
POP_SECTION = 'pop'
MSSQL_SECTION = 'mssql'
COMPORT_SECTION = 'com_port'
AUDIO_BUS_SECTION = 'audio_bus'
MIC_SECTION = 'mic'

FILE_PATH = 'file_path'

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

# checking string
PROCESS_NAMES = (STR_AIR, STR_MIC, STR_FUN, STR_SEN)
PROCESS_OK_RESULTS = (STR_OK, STR_A, STR_B, STR_C)
PROCESS_RESULTS = (STR_OK, STR_NG, STR_A, STR_B, STR_C)
PROCESS_FULL_NAMES = {
    STR_AIR: 'AIR LEAK',
    STR_MIC: 'MIC',
    STR_FUN: 'FUNCTION',
    STR_SEN: 'SENSOR'
}
STR_FIRST = 'FIRST'
STR_SECOND = 'SECOND'
STR_THIRD = "THIRD"
STR_FOURTH = "FOURTH"
STR_FIFTH = "FIFTH"

# number to string
NUMERAL = {
    1: STR_FIRST,
    2: STR_SECOND,
    3: STR_THIRD,
    4: STR_FOURTH,
    5: STR_FIFTH,
}

grade_colors = {
    STR_A: WHITE,
    STR_B: YELLOW,
    STR_C: GREEN
}