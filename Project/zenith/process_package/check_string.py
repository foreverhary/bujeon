import re

from PyQt5.QtCore import Qt


# Qt key값 ascii 인지 확인
def check_char(char):
    return Qt.Key_Space <= char <= Qt.Key_QuoteLeft


# os keyboard event로 들어오는 키값 확인
def keyboard_event_check_char(char):
    return (
            not '0' <= char <= '9'
            and not 'A' <= char <= 'Z'
            and not 'a' <= char <= 'z'
    )


# NFC UID 확인
def check_nfc_uid(string):
    if re.match('UID: ' + '0x[0-9A-F]{2} ?' * 7, string) \
            or re.match('UID: ' + '0x[0-9A-F]{2} ?' * 4, string):
        return string
    return ''


# DM 값 체크
def check_dm(string):
    if re.match('[A-Z]{2}[0-9][A-Z][0-9]{10}$', string) \
            or re.match('[VG][A-Z][1-9][0-9A-Z]{5}$', string) \
            or re.match('[VGAB][A-Z][1-9][1-9][0-9A-Z]{5}$', string):
        return string
    return ''


def check_result_ir_sensor(string):
    if return_value := re.search('[LR]' + ',[oO][kK]' * 9, string):
        return return_value.group(0)
    return False


def check_nfc_result_2_char(string):
    if return_value := re.search('\w{2}', string):
        return return_value.group(0)
    return False


def check_nfc_write_result(string):
    if return_value := re.search("write successed", string):
        return return_value.group(0)
    return False
