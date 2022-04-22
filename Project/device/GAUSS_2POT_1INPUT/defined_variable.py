CONFIG_FILE_NAME = '/home/pi/config.ini'
BUTTON_POT = 'POT'
BUTTON_CAL = 'CALIBRATION'
BUTTON_MIN = 'MIN'
BUTTON_MAX = 'MAX'
BUTTON_EXIT = 'SAVE && EXIT'
BUTTON_MENU = [BUTTON_POT, BUTTON_CAL, BUTTON_MAX, BUTTON_MAX, BUTTON_EXIT]

CONFIG_ON_OFF = 'on_off'
CONFIG_CAL = 'calibration'
CONFIG_MIN = 'min'
CONFIG_MAX = 'max'

ON = 'on'
OFF = 'off'

MAIN_PAGE = '-main-'
MENU_PAGE = '-menu-'
CAL_PAGE = '-cal-'
MINMAX_PAGE = '-minmax-'


def convertValueToStr(value):
    return f"{('S', 'N')[value>0]}{abs(value)}"


def convertStrToValue(string):
    return (-1, 1)[string[0] == 'N']*int(string[1:])


def make_pot_name(pot_num):
    return f"pot{pot_num}"
