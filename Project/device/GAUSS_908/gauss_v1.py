import PySimpleGUI as sg
from serial import Serial, serialutil
import os
import threading
import configparser as cp
import platform
import pyautogui

pyautogui.FAILSAFE = False
lock = threading.Lock()

sg.theme('DarkBlack1')

ser = Serial()
if 'Window' in platform.platform():
    ser.port = 'com5'
else:
    ser.port = '/dev/ttyACM0'
ser.baudrate = 115200
ser.stopbits = 1
ser.bytesize = 8
ser.parity = 'N'

WINDOW_SIZE_WIDTH = 800
WINDOW_SIZE_HEIGHT = 480
WINDOW_SIZE = (WINDOW_SIZE_WIDTH, WINDOW_SIZE_HEIGHT)
MAIN_POT_FONT_SIZE = int(WINDOW_SIZE_WIDTH / 50)
MAIN_POT_SIZE = (17, 1)
MAIN_POT_MARGIN_SIZE = (1, 2)
MAIN_POT_VALUE_FONT_SIZE = int(MAIN_POT_FONT_SIZE * 1.75)
MAIN_POT_VALUE_SIZE = (7, 1)
MAIN_POT_PASS_FONT_SIZE = int(MAIN_POT_FONT_SIZE * 1.75)
MAIN_POT_PASS_SIZE = (4, 1)
MAIN_POT_RESULT_FONT_SIZE = int(MAIN_POT_FONT_SIZE * 3.5)
MAIN_POT_EACH_SIZE = (int(WINDOW_SIZE_WIDTH / 3.4), int(WINDOW_SIZE_HEIGHT / 2.6))
CALIBRATION_BUTTON_SIZE = (int(MAIN_POT_FONT_SIZE * 2), 1)
CALIBRATION_FONT_SIZE = MAIN_POT_FONT_SIZE * 2

MENU_FONT_SIZE = 200
MENU_SIZE = (WINDOW_SIZE_WIDTH, 1)

POT_FONT_SIZE = 48

CAL_POT_FONT_SIZE = 30
CAL_VALUE_FONT_SIZE = 40
CAL_SYMBOL_FONT_SIZE = 100

MIN_MAX_NUM_BUTTON_FONT_SIZE = 70

CONFIG_ON_OFF = 'on_off'

CONFIG_FILE_NAME = 'config.ini'

MENU_KEY = [f"POT {index}" for index in range(1, 6)]
MENU_KEY += ["EXIT"]

POT_MENU = list()
for pot_num in range(1, 6):
    POT_MENU.append([f"POT{pot_num}", 'CALIBRATION', 'SPEC MIN', 'SPEC MAX', 'SAVE & EXIT'])


def init_config():
    config = cp.ConfigParser()
    config.optionxform = lambda option: option
    for index in range(1, 6):
        pot_key = f"pot{index}"
        config.add_section(pot_key)
        config[pot_key][CONFIG_ON_OFF] = 'on'
        config[pot_key]['calibration'] = '0'
        config[pot_key]['min'] = '-100'
        config[pot_key]['max'] = '-900'
    with open(CONFIG_FILE_NAME, 'w') as configfile:
        config.write(configfile)


def read_config():
    if not os.path.exists(CONFIG_FILE_NAME):
        init_config()
    config = cp.ConfigParser()
    config.read(CONFIG_FILE_NAME, encoding='utf-8')
    return config


def read_config_value(section, option):
    config = read_config()
    return config[section][option]


def write_config(section, option, value):
    config = cp.ConfigParser()
    config.read(CONFIG_FILE_NAME, encoding='utf-8')
    config[section][option] = value
    with open(CONFIG_FILE_NAME, 'w') as configfile:
        config.write(configfile)


def convertValueToStr(value):
    if type(value) == int:
        return f"{('S', 'N')[value > 0]}{abs(value)}"
    elif type(value) == str:
        return f"{('S', 'N')[int(value) > 0]}{abs(int(value))}"


def convertStrToValue(string):
    return (-1, 1)[string[0] == 'N'] * int(string[1:])


def make_probe_layout():
    r_value = list()
    config = read_config()
    for index in range(1, 6):
        r_value.append([[sg.Text(
            f"POT{index} {convertValueToStr(config[f'pot{index}']['min'])} ~ {convertValueToStr(config[f'pot{index}']['max'])}",
            size=MAIN_POT_SIZE, font=('Helvetica', MAIN_POT_FONT_SIZE), key=f'probe_{index}_thd')],
            [sg.Text('', size=MAIN_POT_MARGIN_SIZE)],
            [sg.Text('', size=MAIN_POT_VALUE_SIZE, font=('Helvetica', MAIN_POT_VALUE_FONT_SIZE),
                     key=f'probe_{index}'),
             sg.Text('', size=MAIN_POT_PASS_SIZE, font=('Helvetica', MAIN_POT_PASS_FONT_SIZE),
                     key=f'probe_{index}_result')],
            [sg.Text('')]
        ])
    return r_value


def make_menu_layout():
    r_value = list()
    for item in MENU_KEY:
        r_value.append([sg.RButton(f"{item}", key=f"{item}", font=('Helvetica', MENU_FONT_SIZE), size=MENU_SIZE)])
    return r_value


def make_pot_menu_layout():
    r_value = list()
    for index, items in enumerate(POT_MENU):
        pot = [[sg.B(f"{item}", key=f"{item.lower()}_{index + 1}", font=('Helvetica', POT_FONT_SIZE), size=MENU_SIZE)]
               for item in items]
        r_value.append(pot)
    return r_value


probe_result_layout = [
    [sg.Text('', font=('Helvetica', MAIN_POT_RESULT_FONT_SIZE), justification='center', key='probe_result')]]
probe_layout = make_probe_layout()
main_layout = [[sg.Text('')],
               [sg.Frame('', [[sg.Column(probe_layout[0], size=MAIN_POT_EACH_SIZE, key='column1')]]),
                sg.Frame('', [[sg.Column(probe_layout[1], size=MAIN_POT_EACH_SIZE, key='column2')]]),
                sg.Frame('', [[sg.Column(probe_result_layout, size=MAIN_POT_EACH_SIZE)]])],
               # sg.Frame('', layout=probe_result_layout)],

               [sg.Frame('', [[sg.Column(probe_layout[2], size=MAIN_POT_EACH_SIZE, key='column3')]]),
                sg.Frame('', [[sg.Column(probe_layout[3], size=MAIN_POT_EACH_SIZE, key='column4')]]),
                sg.Frame('', [[sg.Column(probe_layout[4], size=MAIN_POT_EACH_SIZE, key='column5')]])],
               [sg.B('CALIBRATION', size=CALIBRATION_BUTTON_SIZE, font=('Helvetica', CALIBRATION_FONT_SIZE),
                     visible=False)]]

cal_layout = [[sg.Text('POT', size=(WINDOW_SIZE_WIDTH, None), justification='center',
                       font=('Helvetica', CAL_POT_FONT_SIZE), key='cal_pot_num')],
              [sg.Text('CAL: ', font=('Helvetica', CAL_VALUE_FONT_SIZE)),
               sg.InputText('', readonly=True, font=('Helvetica', CAL_VALUE_FONT_SIZE), key='cal')],
              [sg.Text('              '),
               sg.Button(sg.SYMBOL_UP, font=('Helvetica', CAL_SYMBOL_FONT_SIZE), key='cal_up'),
               sg.Button(sg.SYMBOL_DOWN, font=('Helvetica', CAL_SYMBOL_FONT_SIZE), key='cal_down'),
               sg.Button(sg.SYMBOL_CHECK, font=('Helvetica', CAL_SYMBOL_FONT_SIZE), key='cal_save_exit')]]

min_max_layout = [[sg.Text('POT', size=(WINDOW_SIZE_WIDTH, None), justification='center',
                           font=('Helvetica', CAL_POT_FONT_SIZE), key='min_max_pot_num')],
                  [sg.Text('MIN: ', size=(6, None), font=('Helvetica', CAL_VALUE_FONT_SIZE), key='min_max_label'),
                   sg.InputText('', size=(13, None), readonly=True, font=('Helvetica', CAL_VALUE_FONT_SIZE),
                                key='min_max_value')],
                  [sg.Button('N', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('1', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('2', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('3', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('4', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('5', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('CLR', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE))],
                  [sg.Button('S', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('6', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('7', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('8', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('9', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('0', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE)),
                   sg.Button('EXT', font=('Helvetica', MIN_MAX_NUM_BUTTON_FONT_SIZE))]]

layout = [[sg.Column(main_layout, key='-MAIN-', visible=True)]]
layout[0] += [sg.Column(make_menu_layout(), key='-MENU-', visible=False)]
for pot_num, item in enumerate(make_pot_menu_layout()):
    layout[0] += [sg.Column(item, key=f"-POT {pot_num + 1}-", visible=False)]
layout[0] += [sg.Column(cal_layout, key='-CAL-', visible=False)]
layout[0] += [sg.Column(min_max_layout, key='-MINMAX-', visible=False)]

window = sg.Window('', layout, size=WINDOW_SIZE, no_titlebar=True, location=(0, 0), keep_on_top=True,
                   use_default_focus=False).Finalize()
window.Maximize()
window.set_cursor('none')
for index in range(1, 6):
    window[f"column{index}"].bind('<Enter>', '')
running = True
cal_running = False
cal_value = 0


def layout_unvisible_all():
    for index in range(1, 6):
        window.Element(f"-POT {index}-").Update(visible=False)
    window.Element('-MAIN-').Update(visible=False)
    window.Element('-MENU-').Update(visible=False)
    window.Element('-CAL-').Update(visible=False)
    window.Element('-MINMAX-').Update(visible=False)


def calibration_layout_update(button):
    global cal_running, cal_value
    pot_num = int(button[-1])
    cal_running = True
    config = read_config()
    cal_value = int(config[f'pot{pot_num}']['calibration'])
    window.Element('cal_pot_num').Update(f"POT {pot_num}")
    window.Element('-CAL-').Update(visible=True)


def min_max_layout_update(button):
    pot_num = int(button[-1])
    min_max_label = 'MIN:' if 'min' in button else 'MAX:'

    window.Element('min_max_pot_num').Update(f"POT {pot_num}")
    window.Element('min_max_label').Update(min_max_label)
    window.Element('min_max_value').Update(
        convertValueToStr(read_config_value(f"pot{pot_num}", ('max', 'min')['MIN' in min_max_label])))
    window.Element('-MINMAX-').Update(visible=True)


def pot_layout_update(button):
    # print('pot_layout', button)
    pot_num = int(button[-1])
    config = read_config()
    onoff = config[f'pot{pot_num}'][CONFIG_ON_OFF]
    button_color = ('red', 'blue')[onoff == 'on']
    window.Element(f"pot{pot_num}_{pot_num}").Update(f"POT{pot_num} [{onoff}]", button_color=('white', button_color))
    window.Element(f"calibration_{pot_num}").Update(f"CALIBRATION [{config[f'pot{pot_num}']['calibration']}]")
    window.Element(f"spec min_{pot_num}").Update(f"SPEC MIN [{convertValueToStr(config[f'pot{pot_num}']['min'])}]")
    window.Element(f"spec max_{pot_num}").Update(f"SPEC MAX [{convertValueToStr(config[f'pot{pot_num}']['max'])}]")


def layout_visivility(button):
    global cal_running, running
    global cal_value
    layout_unvisible_all()
    pyautogui.moveTo(0, 0)
    if button == '-MAIN-':
        running = True
        window.Element('-MAIN-').Update(visible=True)
    elif button == '-MENU-':
        window.Element('-MENU-').Update(visible=True)
    elif "POT" in button:
        pot_layout_update(button)
        window.Element(f"-{button}-").Update(visible=True)
    elif "save & exit" in button:
        layout_visivility('-MAIN-')
    elif 'calibration' in button:
        calibration_layout_update(button)
    elif 'min' in button or 'max' in button:
        min_max_layout_update(button)
    elif 'cal_save_exit' in button:
        cal_running = False
        pot_num = int(window.Element('cal_pot_num').Get()[-1])
        write_config(f"pot{pot_num}", 'calibration', str(cal_value))
        layout_visivility(f"POT {pot_num}")
    elif 'EXT' in button:
        pot_num = int(window.Element('min_max_pot_num').Get()[-1])
        minmax = window.Element('min_max_label').Get()
        if 'MIN' in minmax:
            write_config(f"pot{pot_num}", 'min', str(convertStrToValue(window.Element('min_max_value').Get())))
        else:
            write_config(f"pot{pot_num}", 'max', str(convertStrToValue(window.Element('min_max_value').Get())))
        layout_visivility(f"POT {pot_num}")


def min_max_button(button):
    # print('minmax_button', button)
    key = 'min_max_value'
    value = window.Element(key).Get()
    if button == 'CLR':
        value = ''
        window.Element(key).Update('')
    elif button == 'N' or button == 'S':
        if len(value) == 0:
            value += button
    else:
        if len(value):
            value += button

    window.Element(key).Update(value)


def cal_updown_key(button):
    global cal_value
    lock.acquire()
    if 'up' in button:
        cal_value += 1
    else:
        cal_value -= 1
    lock.release()
    # print(cal_value)


def pot_key(button):
    pot_num = int(button[-1])
    onoff = 'on' if read_config_value(f"pot{pot_num}", CONFIG_ON_OFF) == 'off' else 'off'
    button_color = ('red', 'blue')[onoff == 'on']
    write_config(f"pot{pot_num}", CONFIG_ON_OFF, onoff)
    window.Element(f"pot{pot_num}_{pot_num}").Update(f"POT{pot_num} [{onoff}]", button_color=('white', button_color))


def pole_change(value):
    return (-1, 1)[value[0] == 'N'] * int(value[1:])


def read_probe():
    global running, ser
    try:
        if not ser.isOpen():
            ser.open()
        config = read_config()
        ser.readline()
        read_val_from_plobe = ser.readline().decode().split(",")
        read_values = list(map(int, map(float, read_val_from_plobe)))
        read_values = [read_values[3], read_values[1], read_values[4], read_values[2], read_values[0]]
        ser.flushInput()
        for index, read_value in enumerate(read_values):
            if config[f"pot{index + 1}"][CONFIG_ON_OFF] == 'on':
                min_value = int(float(config[f"pot{index + 1}"]['min']))
                max_value = int(float(config[f"pot{index + 1}"]['max']))
                read_value += int(config[f"pot{index + 1}"]['calibration'])
                if read_value > 0:
                    input_value = f'N{abs(int(read_value))}G'
                else:
                    input_value = f'S{abs(int(read_value))}G'
                window.Element(f"probe_{index + 1}").Update(input_value)
                if min_value < 0 and max_value < 0:
                    onf = ('NG', 'OK')[max_value <= read_value <= min_value]
                else:
                    onf = ('NG', 'OK')[min_value <= read_value <= max_value]
                window.Element(f"probe_{index + 1}_result").Update(onf, text_color=('red', 'blue')[onf == 'OK'])
            else:
                window.Element(f"probe_{index + 1}").Update('OFF')
                window.Element(f"probe_{index + 1}_result").Update('')

        pass_fail = True

        for index in range(1, 6):
            if window.Element(f"probe_{index}_result").Get() == 'NG':
                pass_fail = False
                break

        window.Element('probe_result').Update(('FAIL', 'PASS')[pass_fail], text_color=('red', 'blue')[pass_fail])
    except serialutil.SerialException as e:
        print(e)
        if running:
            os._exit(1)
    except Exception as e:
        print("type error: " + str(e))

    # if not running:
    #     if ser.isOpen():
    #         ser.close()


def read_probe_cal():
    global cal_value, cal_running, ser
    try:
        if not ser.isOpen():
            ser.open()
        pot_num = int(window.Element('cal_pot_num').Get()[-1])
        ser.readline()
        read_val_from_plobe = ser.readline().decode().split(",")
        ser.flushInput()
        read_values = list(map(int, map(float, read_val_from_plobe)))
        read_values = [read_values[3], read_values[1], read_values[4], read_values[2], read_values[0]]
        read_value = read_values[pot_num - 1] + + cal_value
        if read_value > 0:
            window.Element('cal').Update(f'N{abs(read_value)}G')
        else:
            window.Element('cal').Update(f'S{abs(read_value)}G')
    except serialutil.SerialException as e:
        print(e)
        if cal_running:
            os._exit(1)
    except Exception as e:
        print("type error: " + str(e))
    # if not cal_running:
    #     if ser.isOpen():
    #         ser.close()


def thread_run():
    read_probe_thread = threading.Thread(target=read_probe)
    read_probe_thread.start()


def cal_thread_run():
    cal_read_probe_thread = threading.Thread(target=read_probe_cal)
    cal_read_probe_thread.start()


while True:
    button, values = window.read(timeout=200)
    if button in (sg.WINDOW_CLOSED, "-ESCAPE-"):
        os._exit(1)
        break

    if not '__TIMEOUT__' in button:
        print(button, values)

    if running:
        thread_run()

    if cal_running:
        cal_thread_run()

    if button == "CALIBRATION":
        running = False
        layout_visivility('-MENU-')
    elif button == 'EXIT':
        layout_visivility('-MAIN-')
    elif "POT" in button \
            or "save & exit" in button \
            or 'calibration' in button \
            or 'min' in button \
            or 'max' in button \
            or 'cal_save_exit' in button:
        layout_visivility(button)
    elif 'EXT' in button:
        pyautogui.moveTo(0, 0)
        if window.Element('min_max_value').Get():
            layout_visivility(button)
    elif button in ['N', 'S', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'CLR']:
        pyautogui.moveTo(0, 0)
        min_max_button(button)
    elif button in ['cal_up', 'cal_down']:
        pyautogui.moveTo(0, 0)
        cal_updown_key(button)
    elif 'pot' in button:
        pyautogui.moveTo(0, 0)
        pot_key(button)
    elif 'column' in button:
        running = False
        layout_visivility(f'POT {button[-1]}')

window.close()
