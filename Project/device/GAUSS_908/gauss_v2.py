import PySimpleGUI as sg
from serial import Serial
import os
import re
import threading
import pyautogui

sg.theme('DarkBlack1')

ser_1 = Serial()
ser_1.port = '/dev/ttyACM0'
ser_1.baudrate = 115200
ser_1.stopbits = 1
ser_1.bytesize = 8
ser_1.parity = 'N'

ser_2 = Serial()
ser_2.port = '/dev/ttyACM1'
ser_2.baudrate = 115200
ser_2.stopbits = 1
ser_2.bytesize = 8
ser_2.parity = 'N'

ser_3 = Serial()
ser_3.port = '/dev/ttyACM2'
ser_3.baudrate = 115200
ser_3.stopbits = 1
ser_3.bytesize = 8
ser_3.parity = 'N'

ser_4 = Serial()
ser_4.port = '/dev/ttyACM3'
ser_4.baudrate = 115200
ser_4.stopbits = 1
ser_4.bytesize = 8
ser_4.parity = 'N'

Main_layout = [[sg.Text('')],
               [sg.Button('Start Test', size=(840, None), font=('Helvetica', 120), key='start_test')],
               [sg.Text('')],
               [sg.Button('Ch Select', size=(840, None), font=('Helvetica', 120), key='channel_select')]]

column1 = [[sg.Text('')],
           [sg.Text('', size=(18, None), justification='center', font=('Helvetica', 26), key='ch1_thd',
                    relief=sg.RELIEF_RIDGE)],
           [sg.Text('', size=(8, None), justification='center', font=('Helvetica', 38), key='top_left',
                    relief=sg.RELIEF_RIDGE),
            sg.Text('', size=(4, None), justification='center', font=('Helvetica', 37), key='ch1_result',
                    relief=sg.RELIEF_RIDGE)]]
column2 = [[sg.Text('')],
           [sg.Text('', size=(18, None), justification='center', font=('Helvetica', 26), key='ch2_thd',
                    relief=sg.RELIEF_RIDGE)],
           [sg.Text('', size=(8, None), justification='center', font=('Helvetica', 38), key='top_right',
                    relief=sg.RELIEF_RIDGE),
            sg.Text('', size=(4, None), justification='center', font=('Helvetica', 37), key='ch2_result',
                    relief=sg.RELIEF_RIDGE)]]
column3 = [[sg.Text('')],
           [sg.Text('', size=(18, None), justification='center', font=('Helvetica', 26), key='ch3_thd',
                    relief=sg.RELIEF_RIDGE)],
           [sg.Text('', size=(8, None), justification='center', font=('Helvetica', 38), key='bottom_left',
                    relief=sg.RELIEF_RIDGE),
            sg.Text('', size=(4, None), justification='center', font=('Helvetica', 37), key='ch3_result',
                    relief=sg.RELIEF_RIDGE)]]
column4 = [[sg.Text('')],
           [sg.Text('', size=(18, None), justification='center', font=('Helvetica', 26), key='ch4_thd',
                    relief=sg.RELIEF_RIDGE)],
           [sg.Text('', size=(8, None), justification='center', font=('Helvetica', 38), key='bottom_right',
                    relief=sg.RELIEF_RIDGE),
            sg.Text('', size=(4, None), justification='center', font=('Helvetica', 37), key='ch4_result',
                    relief=sg.RELIEF_RIDGE)]]
column5 = [[sg.Button('Main menu', size=(48, None), font=('Helvetica', 20))]]

Start_layout = [[sg.Frame('', [[sg.Column(column1, size=(360, 180))]]),
                 sg.Frame('', [[sg.Column(column2, size=(360, 180))]])],
                [sg.Frame('', [[sg.Column(column3, size=(360, 180))]]),
                 sg.Frame('', [[sg.Column(column4, size=(360, 180))]])],
                [sg.Frame('', [[sg.Column(column5, size=(800, 50))]])]]

Ch_layout = [[sg.Button('Channel 1', size=(840, None), font=('Helvetica', 50), key='ch_1')],
             [sg.Button('Channel 2', size=(840, None), font=('Helvetica', 50), key='ch_2')],
             [sg.Button('Channel 3', size=(840, None), font=('Helvetica', 50), key='ch_3')],
             [sg.Button('Channel 4', size=(840, None), font=('Helvetica', 50), key='ch_4')],
             [sg.Button('EXIT', size=(840, None), font=('Helvetica', 50))]]

ch1_layout = [[sg.Button('On', size=(840, None), button_color=('white', 'green'), font=('Helvetica', 50), key='ch1_on_off')],
              [sg.Button('Ch1 CAL: ', size=(840, None), font=('Helvetica', 50), key="-ch1_cal_-")],
              [sg.Button('SPEC MIN: ', size=(840, None), font=('Helvetica', 50), key="-ch1_min_-")],
              [sg.Button('SPEC MAX: ', size=(840, None), font=('Helvetica', 50), key="-ch1_max_-")],
              [sg.Button('SAVE & EXIT', size=(840, None), font=('Helvetica', 50), key='ch1_save_and_exit')]]
ch1_cal_layout = [[sg.Text('Channel 1', justification='center', font=('Helvetica', 50))],
                  [sg.Text('CAL: ', font=('Helvetica', 80)),
                   sg.InputText('', readonly=True, font=('Helvetica', 80), key='ch1_cal')],
                  [sg.Text('              '),
                   sg.Button(sg.SYMBOL_UP, font=('Helvetica', 135), key='ch1_cal_up'),
                   sg.Button(sg.SYMBOL_DOWN, font=('Helvetica', 135), key='ch1_cal_down'),
                   sg.Button(sg.SYMBOL_CHECK, font=('Helvetica', 135), key='ch1_cal_save_exit')]]
ch1_min_layout = [[sg.Text('Channel 1', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MIN: ', size=(4, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(11, None), readonly=True, font=('Helvetica', 80), key='ch1_min')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]
ch1_max_layout = [[sg.Text('Channel 1', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MAX: ', size=(5, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(10, None), readonly=True, font=('Helvetica', 80), key='ch1_max')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]

ch2_layout = [[sg.Button('On', size=(840, None), button_color=('white', 'green'), font=('Helvetica', 50), key='ch2_on_off')],
              [sg.Button('Ch2 CAL: ', size=(840, None), font=('Helvetica', 50), key="-ch2_cal_-")],
              [sg.Button('SPEC MIN: ', size=(840, None), font=('Helvetica', 50), key="-ch2_min_-")],
              [sg.Button('SPEC MAX: ', size=(840, None), font=('Helvetica', 50), key="-ch2_max_-")],
              [sg.Button('SAVE & EXIT', size=(840, None), font=('Helvetica', 50), key='ch2_save_and_exit')]]
ch2_cal_layout = [[sg.Text('Channel 2', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('CAL: ', font=('Helvetica', 80)),
                   sg.InputText('', readonly=True, font=('Helvetica', 80), key='ch2_cal')],
                  [sg.Text('              '),
                   sg.Button(sg.SYMBOL_UP, font=('Helvetica', 135), key='ch2_cal_up'),
                   sg.Button(sg.SYMBOL_DOWN, font=('Helvetica', 135), key='ch2_cal_down'),
                   sg.Button(sg.SYMBOL_CHECK, font=('Helvetica', 135), key='ch2_cal_save_exit')]]
ch2_min_layout = [[sg.Text('Channel 2', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MIN: ', size=(4, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(11, None), readonly=True, font=('Helvetica', 80), key='ch2_min')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]
ch2_max_layout = [[sg.Text('Channel 2', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MAX: ', size=(5, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(10, None), readonly=True, font=('Helvetica', 80), key='ch2_max')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]

ch3_layout = [[sg.Button('On', size=(840, None), button_color=('white', 'green'), font=('Helvetica', 50), key='ch3_on_off')],
              [sg.Button('Ch3 CAL: ', size=(840, None), font=('Helvetica', 50), key="-ch3_cal_-")],
              [sg.Button('SPEC MIN: ', size=(840, None), font=('Helvetica', 50), key="-ch3_min_-")],
              [sg.Button('SPEC MAX: ', size=(840, None), font=('Helvetica', 50), key="-ch3_max_-")],
              [sg.Button('SAVE & EXIT', size=(840, None), font=('Helvetica', 50), key='ch3_save_and_exit')]]
ch3_cal_layout = [[sg.Text('Channel 3', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('CAL: ', font=('Helvetica', 80)),
                   sg.InputText('', readonly=True, font=('Helvetica', 80), key='ch3_cal')],
                  [sg.Text('              '),
                   sg.Button(sg.SYMBOL_UP, font=('Helvetica', 135), key='ch3_cal_up'),
                   sg.Button(sg.SYMBOL_DOWN, font=('Helvetica', 135), key='ch3_cal_down'),
                   sg.Button(sg.SYMBOL_CHECK, font=('Helvetica', 135), key='ch3_cal_save_exit')]]
ch3_min_layout = [[sg.Text('Channel 3', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MIN: ', size=(4, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(11, None), readonly=True, font=('Helvetica', 80), key='ch3_min')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]
ch3_max_layout = [[sg.Text('Channel 3', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MAX: ', size=(5, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(10, None), readonly=True, font=('Helvetica', 80), key='ch3_max')],Tj
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]

ch4_layout = [[sg.Button('On', size=(840, None), button_color=('white', 'green'), font=('Helvetica', 50), key='ch4_on_off')],
              [sg.Button('Ch4 CAL: ', size=(840, None), font=('Helvetica', 50), key="-ch4_cal_-")],
              [sg.Button('SPEC MIN: ', size=(840, None), font=('Helvetica', 50), key="-ch4_min_-")],
              [sg.Button('SPEC MAX: ', size=(840, None), font=('Helvetica', 50), key="-ch4_max_-")],
              [sg.Button('SAVE & EXIT', size=(840, None), font=('Helvetica', 50), key='ch4_save_and_exit')]]
ch4_cal_layout = [[sg.Text('Channel 4', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('CAL: ', font=('Helvetica', 80)),
                   sg.InputText('', readonly=True, font=('Helvetica', 80), key='ch4_cal')],
                  [sg.Text('              '),
                   sg.Button(sg.SYMBOL_UP, font=('Helvetica', 135), key='ch4_cal_up'),
                   sg.Button(sg.SYMBOL_DOWN, font=('Helvetica', 135), key='ch4_cal_down'),
                   sg.Button(sg.SYMBOL_CHECK, font=('Helvetica', 135), key='ch4_cal_save_exit')]]
ch4_min_layout = [[sg.Text('Channel 4', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MIN: ', size=(4, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(11, None), readonly=True, font=('Helvetica', 80), key='ch4_min')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]
ch4_max_layout = [[sg.Text('Channel 4', size=(840, None), justification='center', font=('Helvetica', 50))],
                  [sg.Text('MAX: ', size=(5, None), font=('Helvetica', 80)),
                   sg.InputText('', size=(10, None), readonly=True, font=('Helvetica', 80), key='ch4_max')],
                  [sg.Button('N', font=('Helvetica', 72)), sg.Button('1', font=('Helvetica', 72)),
                   sg.Button('2', font=('Helvetica', 72)), sg.Button('3', font=('Helvetica', 72)),
                   sg.Button('4', font=('Helvetica', 72)), sg.Button('5', font=('Helvetica', 72)),
                   sg.Button('CLR', font=('Helvetica', 72))],
                  [sg.Button('S', font=('Helvetica', 72)), sg.Button('6', font=('Helvetica', 72)),
                   sg.Button('7', font=('Helvetica', 72)), sg.Button('8', font=('Helvetica', 72)),
                   sg.Button('9', font=('Helvetica', 72)), sg.Button('0', font=('Helvetica', 72)),
                   sg.Button('EXT', font=('Helvetica', 72))]]

layout = [[sg.Column(Main_layout, key='-main-'),
           sg.Column(Start_layout, visible=False, key='-start-'),
           sg.Column(Ch_layout, visible=False, key='-ch-'),
           sg.Column(ch1_layout, visible=False, key='-ch1-'),
           sg.Column(ch2_layout, visible=False, key='-ch2-'),
           sg.Column(ch3_layout, visible=False, key='-ch3-'),
           sg.Column(ch4_layout, visible=False, key='-ch4-'),
           sg.Column(ch1_cal_layout, visible=False, key='-ch1_cal-'),
           sg.Column(ch2_cal_layout, visible=False, key='-ch2_cal-'),
           sg.Column(ch3_cal_layout, visible=False, key='-ch3_cal-'),
           sg.Column(ch4_cal_layout, visible=False, key='-ch4_cal-'),
           sg.Column(ch1_min_layout, visible=False, key='-ch1_min-'),
           sg.Column(ch1_max_layout, visible=False, key='-ch1_max-'),
           sg.Column(ch2_min_layout, visible=False, key='-ch2_min-'),
           sg.Column(ch2_max_layout, visible=False, key='-ch2_max-'),
           sg.Column(ch3_min_layout, visible=False, key='-ch3_min-'),
           sg.Column(ch3_max_layout, visible=False, key='-ch3_max-'),
           sg.Column(ch4_min_layout, visible=False, key='-ch4_min-'),
           sg.Column(ch4_max_layout, visible=False, key='-ch4_max-')]]

# window = sg.Window('', layout, size=(800, 480), keep_on_top=True, finalize=True)
window = sg.Window('', layout, no_titlebar=True, location=(0, 0), size=(800, 480), keep_on_top=True, use_default_focus=False).Finalize()
window.Maximize()
window.bind("<Escape>", "-ESCAPE-")  # for Dev on RPi LCD
window.set_cursor('none')  # for Servicecd

def read_1():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
                ch1_min_ = ch1_min_f.read()
                ch1_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
                ch1_max_ = ch1_max_f.read()
                ch1_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch1_cal.csv", "r") as ch1_cal_f:
                ch1_cal_val = ch1_cal_f.read()
                ch1_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_cal_val, flags=re.DOTALL)
            if float(ser_1.readline().decode()) > 0:
                window.Element('top_left').Update(f'N{abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val)}G')
                if int(ch1_min_[1:]) <= abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val) <= int(
                        ch1_max_[1:]) and ch1_min_[
                    0] != "S" and ch1_max_[0] != "S":
                    window.Element('ch1_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch1_result').Update("NG", text_color='red')
            else:
                window.Element('top_left').Update(f'S{abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val)}G')
                if int(ch1_min_[1:]) <= abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val) \
                        <= int(ch1_max_[1:]) and ch1_min_[
                    0] != "N" and ch1_max_[0] != "N":
                    window.Element('ch1_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch1_result').Update("NG", text_color='red')
    except Exception as e:
        print("type error: " + str(e))


def read_cal1():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch1_cal.csv", "r") as ch1_cal_f:
                ch1_cal_val = ch1_cal_f.read()
                ch1_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_cal_val, flags=re.DOTALL)
            if float(ser_1.readline().decode()) > 0:
                window.Element('ch1_cal').Update(f'N{abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val)}G')
            else:
                window.Element('ch1_cal').Update(f'S{abs(int(float(ser_1.readline().decode()))) + int(ch1_cal_val)}G')
    except Exception as e:
        print("type error: " + str(e))


def read_2():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
                ch2_min_ = ch2_min_f.read()
                ch2_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
                ch2_max_ = ch2_max_f.read()
                ch2_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch2_cal.csv", "r") as ch2_cal_f:
                ch2_cal_val = ch2_cal_f.read()
                ch2_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_cal_val, flags=re.DOTALL)
            if float(ser_2.readline().decode()) > 0:
                window.Element('top_right').Update(f'N{abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val)}G')
                if int(ch2_min_[1:]) <= abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val) <= int(
                        ch2_max_[1:]) and ch2_min_[
                    0] != "S" and ch2_max_[0] != "S":
                    window.Element('ch2_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch2_result').Update("NG", text_color='red')
            else:
                window.Element('top_right').Update(f'S{abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val)}G')
                if int(ch2_min_[1:]) <= abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val) \
                        <= int(ch2_max_[1:]) and ch2_min_[
                    0] != "N" and ch2_max_[0] != "N":
                    window.Element('ch2_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch2_result').Update("NG", text_color='red')
    except Exception as e:
        print("type error: " + str(e))


def read_cal2():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch2_cal.csv", "r") as ch2_cal_f:
                ch2_cal_val = ch2_cal_f.read()
                ch2_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_cal_val, flags=re.DOTALL)
            if float(ser_2.readline().decode()) > 0:
                window.Element('ch2_cal').Update(f'N{abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val)}G')
            else:
                window.Element('ch2_cal').Update(f'S{abs(int(float(ser_2.readline().decode()))) + int(ch2_cal_val)}G')
    except Exception as e:
        print("type error: " + str(e))


def read_3():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
                ch3_min_ = ch3_min_f.read()
                ch3_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
                ch3_max_ = ch3_max_f.read()
                ch3_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch3_cal.csv", "r") as ch3_cal_f:
                ch3_cal_val = ch3_cal_f.read()
                ch3_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_cal_val, flags=re.DOTALL)
            if float(ser_3.readline().decode()) > 0:
                window.Element('bottom_left').Update(
                    f'N{abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val)}G')
                if int(ch3_min_[1:]) <= abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val) <= int(
                        ch3_max_[1:]) and ch3_min_[
                    0] != "S" and ch3_max_[0] != "S":
                    window.Element('ch3_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch3_result').Update("NG", text_color='red')
            else:
                window.Element('bottom_left').Update(
                    f'S{abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val)}G')
                if int(ch3_min_[1:]) <= abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val) \
                        <= int(ch3_max_[1:]) and ch3_min_[
                    0] != "N" and ch3_max_[0] != "N":
                    window.Element('ch3_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch3_result').Update("NG", text_color='red')
    except Exception as e:
        print("type error: " + str(e))


def read_cal3():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch3_cal.csv", "r") as ch3_cal_f:
                ch3_cal_val = ch3_cal_f.read()
                ch3_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_cal_val, flags=re.DOTALL)
            if float(ser_3.readline().decode()) > 0:
                window.Element('ch3_cal').Update(f'N{abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val)}G')
            else:
                window.Element('ch3_cal').Update(f'S{abs(int(float(ser_3.readline().decode()))) + int(ch3_cal_val)}G')
    except Exception as e:
        print("type error: " + str(e))


def read_4():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
                ch4_min_ = ch4_min_f.read()
                ch4_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
                ch4_max_ = ch4_max_f.read()
                ch4_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_, flags=re.DOTALL)
            with open("/home/pi/Desktop/config/ch4_cal.csv", "r") as ch4_cal_f:
                ch4_cal_val = ch4_cal_f.read()
                ch4_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_cal_val, flags=re.DOTALL)
            if float(ser_4.readline().decode()) > 0:
                window.Element('bottom_right').Update(
                    f'N{abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val)}G')
                if int(ch4_min_[1:]) <= abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val) <= int(
                        ch4_max_[1:]) and ch4_min_[
                    0] != "S" and ch4_max_[0] != "S":
                    window.Element('ch4_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch4_result').Update("NG", text_color='red')
            else:
                window.Element('bottom_right').Update(
                    f'S{abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val)}G')
                if int(ch4_min_[1:]) <= abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val) \
                        <= int(ch4_max_[1:]) and ch4_min_[
                    0] != "N" and ch4_max_[0] != "N":
                    window.Element('ch4_result').Update("OK", text_color='blue')
                else:
                    window.Element('ch4_result').Update("NG", text_color='red')
    except Exception as e:
        print("type error: " + str(e))


def read_cal4():
    try:
        while True:
            with open("/home/pi/Desktop/config/ch4_cal.csv", "r") as ch4_cal_f:
                ch4_cal_val = ch4_cal_f.read()
                ch4_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_cal_val, flags=re.DOTALL)
            if float(ser_4.readline().decode()) > 0:
                window.Element('ch4_cal').Update(f'N{abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val)}G')
            else:
                window.Element('ch4_cal').Update(f'S{abs(int(float(ser_4.readline().decode()))) + int(ch4_cal_val)}G')
    except Exception as e:
        print("type error: " + str(e))


while True:
    event, values = window.read()
    print(event)
    pyautogui.moveTo(0,0)
    if event in (sg.WINDOW_CLOSED, "-ESCAPE-"):
        os._exit(1)
        break

    if event == 'start_test':
        with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
            ch1_min_ = ch1_min_f.read()
            ch1_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_, flags=re.DOTALL)
        with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
            ch1_max_ = ch1_max_f.read()
            ch1_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_, flags=re.DOTALL)
        window['ch1_thd'].update(f'CH1 {ch1_min_} ~ {ch1_max_}')
        with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
            ch2_min_ = ch2_min_f.read()
            ch2_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_, flags=re.DOTALL)
        with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
            ch2_max_ = ch2_max_f.read()
            ch2_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_, flags=re.DOTALL)
        window['ch2_thd'].update(f'CH2 {ch2_min_} ~ {ch2_max_}')
        with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
            ch3_min_ = ch3_min_f.read()
            ch3_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_, flags=re.DOTALL)
        with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
            ch3_max_ = ch3_max_f.read()
            ch3_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_, flags=re.DOTALL)
        window['ch3_thd'].update(f'CH3 {ch3_min_} ~ {ch3_max_}')
        with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
            ch4_min_ = ch4_min_f.read()
            ch4_min_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_, flags=re.DOTALL)
        with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
            ch4_max_ = ch4_max_f.read()
            ch4_max_ = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_, flags=re.DOTALL)
        window['ch4_thd'].update(f'CH4 {ch4_min_} ~ {ch4_max_}')
        window['-main-'].update(visible=False)
        window['-ch-'].update(visible=False)
        with open("/home/pi/Desktop/config/ch1_on_off_.csv", "r") as file:
            ch1_onof = file.read()
            ch1_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_onof, flags=re.DOTALL)
        if eval(ch1_onof):
            ser_1.open()
            ch1_thread = threading.Thread(target=read_1)
            ch1_thread.start()
        else:
            window['ch1_thd'].update('')
            window['top_left'].update('')
            window['ch1_result'].update('')
        with open("/home/pi/Desktop/config/ch2_on_off_.csv", "r") as file:
            ch2_onof = file.read()
            ch2_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_onof, flags=re.DOTALL)
        if eval(ch2_onof):
            ser_2.open()
            ch2_thread = threading.Thread(target=read_2)
            ch2_thread.start()
        else:
            window['ch2_thd'].update('')
            window['top_right'].update('')
            window['ch2_result'].update('')
        with open("/home/pi/Desktop/config/ch3_on_off_.csv", "r") as file:
            ch3_onof = file.read()
            ch3_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_onof, flags=re.DOTALL)
        if eval(ch3_onof):
            ser_3.open()
            ch3_thread = threading.Thread(target=read_3)
            ch3_thread.start()
        else:
            window['ch3_thd'].update('')
            window['bottom_left'].update('')
            window['ch3_result'].update('')
        with open("/home/pi/Desktop/config/ch4_on_off_.csv", "r") as file:
            ch4_onof = file.read()
            ch4_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_onof, flags=re.DOTALL)
        if eval(ch4_onof):
            ser_4.open()
            ch4_thread = threading.Thread(target=read_4)
            ch4_thread.start()
        else:
            window['ch4_thd'].update('')
            window['bottom_right'].update('')
            window['ch4_result'].update('')
        window['-start-'].update(visible=True)

    elif event == 'channel_select':
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=True)

    elif event == 'Main menu':
        if ser_1.isOpen():
            ser_1.close()
        if ser_2.isOpen():
            ser_2.close()
        if ser_3.isOpen():
            ser_3.close()
        if ser_4.isOpen():
            ser_4.close()
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=True)

    elif event == 'ch_1':
        with open("/home/pi/Desktop/config/ch1_on_off_.csv", "r") as file:
            ch1_onof = file.read()
            ch1_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_onof, flags=re.DOTALL)
        window.Element('ch1_on_off').Update(('Off', 'On')[eval(ch1_onof)],
                                            button_color=(('white', ('red', 'green')[eval(ch1_onof)])))
        with open("/home/pi/Desktop/config/ch1_cal.csv", "r") as ch1_cal_f:
            ch1_cal_val = ch1_cal_f.read()
            ch1_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_cal_val, flags=re.DOTALL)
        window['-ch1_cal_-'].update(f'Ch1 CAL: {ch1_cal_val}')
        with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
            ch1_min_val = ch1_min_f.read()
            ch1_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_val, flags=re.DOTALL)
        window['-ch1_min_-'].update(f'SPEC MIN: {ch1_min_val}')
        with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
            ch1_max_val = ch1_max_f.read()
            ch1_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_val, flags=re.DOTALL)
        window['-ch1_max_-'].update(f'SPEC MAX: {ch1_max_val}')
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1-'].update(visible=True)
    elif event == 'ch1_on_off':
        with open("/home/pi/Desktop/config/ch1_on_off_.csv", "r") as file:
            ch1_onof = file.read()
            ch1_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_onof, flags=re.DOTALL)
        ch1_value = not eval(ch1_onof)
        window.Element('ch1_on_off').Update(('Off', 'On')[ch1_value],
                                            button_color=(('white', ('red', 'green')[ch1_value])))
        with open('/home/pi/Desktop/config/ch1_on_off_.csv', 'w') as write_config_f:
            write_config_f.write(str(ch1_value))
    elif event == '-ch1_cal_-':
        ser_1.open()
        ch1_cal_thread = threading.Thread(target=read_cal1)
        ch1_cal_thread.start()
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch1_cal-'].update(visible=True)
    elif event in ['ch1_cal_up', 'ch1_cal_down', 'ch1_cal_save_exit']:
        with open("/home/pi/Desktop/config/ch1_cal.csv", "r") as ch1_cal_f:
            ch1_cal_val = ch1_cal_f.read()
            ch1_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_cal_val, flags=re.DOTALL)
        if event == 'ch1_cal_up':
            with open('/home/pi/Desktop/config/ch1_cal.csv', 'w') as ch1_cal_f:
                ch1_cal_f.write(str(int(ch1_cal_val) + 1))
        elif event == 'ch1_cal_down':
            with open('/home/pi/Desktop/config/ch1_cal.csv', 'w') as ch1_cal_f:
                ch1_cal_f.write(str(int(ch1_cal_val) - 1))
        elif event == 'ch1_cal_save_exit':
            if ser_1.isOpen():
                ser_1.close()
            with open("/home/pi/Desktop/config/ch1_cal.csv", "r") as ch1_cal_f:
                ch1_cal_val = ch1_cal_f.read()
                ch1_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_cal_val, flags=re.DOTALL)
            window['-ch1_cal_-'].update(f'Ch1 CAL: {ch1_cal_val}')
            with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
                ch1_min_val = ch1_min_f.read()
                ch1_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_val, flags=re.DOTALL)
            window['-ch1_min_-'].update(f'SPEC MIN: {ch1_min_val}')
            with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
                ch1_max_val = ch1_max_f.read()
                ch1_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_val, flags=re.DOTALL)
            window['-ch1_max_-'].update(f'SPEC MAX: {ch1_max_val}')
            window['-main-'].update(visible=False)
            window['-start-'].update(visible=False)
            window['-ch-'].update(visible=False)
            window['-ch2-'].update(visible=False)
            window['-ch3-'].update(visible=False)
            window['-ch4-'].update(visible=False)
            window['-ch1_cal-'].update(visible=False)
            window['-ch2_cal-'].update(visible=False)
            window['-ch3_cal-'].update(visible=False)
            window['-ch4_cal-'].update(visible=False)
            window['-ch1_min-'].update(visible=False)
            window['-ch1_max-'].update(visible=False)
            window['-ch2_min-'].update(visible=False)
            window['-ch2_max-'].update(visible=False)
            window['-ch3_min-'].update(visible=False)
            window['-ch3_max-'].update(visible=False)
            window['-ch4_min-'].update(visible=False)
            window['-ch4_max-'].update(visible=False)
            window['-ch1-'].update(visible=True)
    elif event == '-ch1_min_-':
        with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
            get_cal_val = ch1_min_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch1_min'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch1_min-'].update(visible=True)
    elif event in ['N', '1', '2', '3', '4', '5', 'S', '6', '7', '8', '9', '0']:
        pre_ch1_min = window['ch1_min'].get()
        curr_ch1_min = f'{pre_ch1_min}{event[0]}'
        window['ch1_min'].update(value=curr_ch1_min)
    elif event == 'CLR':
        window['ch1_min'].update("")
    elif event == 'EXT':
        with open('/home/pi/Desktop/config/ch1_min.csv', 'w') as ch1_min_f:
            ch1_min_f.write(window.Element('ch1_min').Get())
        with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
            ch1_min_val = ch1_min_f.read()
            ch1_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_val, flags=re.DOTALL)
        window['-ch1_min_-'].update(f'SPEC MIN: {ch1_min_val}')
        with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
            ch1_max_val = ch1_max_f.read()
            ch1_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_val, flags=re.DOTALL)
        window['-ch1_max_-'].update(f'SPEC MAX: {ch1_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch1-'].update(visible=True)
    elif event == '-ch1_max_-':
        with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
            get_cal_val = ch1_max_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch1_max'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch1_max-'].update(visible=True)
    elif event in ['N0', '11', '22', '33', '44', '55', 'S7', '68', '79', '810', '911', '012']:
        pre_ch1_max = window['ch1_max'].get()
        curr_ch1_max = f'{pre_ch1_max}{event[0]}'
        window['ch1_max'].update(value=curr_ch1_max)
    elif event == 'CLR6':
        window['ch1_max'].update("")
    elif event == 'EXT13':
        with open('/home/pi/Desktop/config/ch1_max.csv', 'w') as ch1_max_f:
            ch1_max_f.write(window.Element('ch1_max').Get())
        with open("/home/pi/Desktop/config/ch1_min.csv", "r") as ch1_min_f:
            ch1_min_val = ch1_min_f.read()
            ch1_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_min_val, flags=re.DOTALL)
        window['-ch1_min_-'].update(f'SPEC MIN: {ch1_min_val}')
        with open("/home/pi/Desktop/config/ch1_max.csv", "r") as ch1_max_f:
            ch1_max_val = ch1_max_f.read()
            ch1_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch1_max_val, flags=re.DOTALL)
        window['-ch1_max_-'].update(f'SPEC MAX: {ch1_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch1-'].update(visible=True)
    elif event == 'ch1_save_and_exit':
        window['-start-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch-'].update(visible=True)


    elif event == 'ch_2':
        with open("/home/pi/Desktop/config/ch2_on_off_.csv", "r") as file:
            ch2_onof = file.read()
            ch2_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_onof, flags=re.DOTALL)
        window.Element('ch2_on_off').Update(('Off', 'On')[eval(ch2_onof)],
                                            button_color=(('white', ('red', 'green')[eval(ch2_onof)])))
        with open("/home/pi/Desktop/config/ch2_cal.csv", "r") as ch2_cal_f:
            ch2_cal_val = ch2_cal_f.read()
            ch2_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_cal_val, flags=re.DOTALL)
        window['-ch2_cal_-'].update(f'Ch2 CAL: {ch2_cal_val}')
        with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
            ch2_min_val = ch2_min_f.read()
            ch2_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_val, flags=re.DOTALL)
        window['-ch2_min_-'].update(f'SPEC MIN: {ch2_min_val}')
        with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
            ch2_max_val = ch2_max_f.read()
            ch2_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_val, flags=re.DOTALL)
        window['-ch2_max_-'].update(f'SPEC MAX: {ch2_max_val}')
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch2-'].update(visible=True)
    elif event == 'ch2_on_off':
        with open("/home/pi/Desktop/config/ch2_on_off_.csv", "r") as file:
            ch2_onof = file.read()
            ch2_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_onof, flags=re.DOTALL)
        ch2_value = not eval(ch2_onof)
        window.Element('ch2_on_off').Update(('Off', 'On')[ch2_value],
                                            button_color=(('white', ('red', 'green')[ch2_value])))
        with open('/home/pi/Desktop/config/ch2_on_off_.csv', 'w') as write_config_f:
            write_config_f.write(str(ch2_value))
    elif event == '-ch2_cal_-':
        ser_2.open()
        ch2_cal_thread = threading.Thread(target=read_cal2)
        ch2_cal_thread.start()
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch2_cal-'].update(visible=True)
    elif event in ['ch2_cal_up', 'ch2_cal_down', 'ch2_cal_save_exit']:
        with open("/home/pi/Desktop/config/ch2_cal.csv", "r") as ch2_cal_f:
            ch2_cal_val = ch2_cal_f.read()
            ch2_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_cal_val, flags=re.DOTALL)
        if event == 'ch2_cal_up':
            with open('/home/pi/Desktop/config/ch2_cal.csv', 'w') as ch2_cal_f:
                ch2_cal_f.write(str(int(ch2_cal_val) + 1))
        elif event == 'ch2_cal_down':
            with open('/home/pi/Desktop/config/ch2_cal.csv', 'w') as ch2_cal_f:
                ch2_cal_f.write(str(int(ch2_cal_val) - 1))
        elif event == 'ch2_cal_save_exit':
            if ser_2.isOpen():
                ser_2.close()
            with open("/home/pi/Desktop/config/ch2_cal.csv", "r") as ch2_cal_f:
                ch2_cal_val = ch2_cal_f.read()
                ch2_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_cal_val, flags=re.DOTALL)
            window['-ch2_cal_-'].update(f'Ch2 CAL: {ch2_cal_val}')
            with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
                ch2_min_val = ch2_min_f.read()
                ch2_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_val, flags=re.DOTALL)
            window['-ch2_min_-'].update(f'SPEC MIN: {ch2_min_val}')
            with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
                ch2_max_val = ch2_max_f.read()
                ch2_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_val, flags=re.DOTALL)
            window['-ch2_max_-'].update(f'SPEC MAX: {ch2_max_val}')
            window['-main-'].update(visible=False)
            window['-start-'].update(visible=False)
            window['-ch-'].update(visible=False)
            window['-ch1-'].update(visible=False)
            window['-ch3-'].update(visible=False)
            window['-ch4-'].update(visible=False)
            window['-ch1_cal-'].update(visible=False)
            window['-ch2_cal-'].update(visible=False)
            window['-ch3_cal-'].update(visible=False)
            window['-ch4_cal-'].update(visible=False)
            window['-ch1_min-'].update(visible=False)
            window['-ch1_max-'].update(visible=False)
            window['-ch2_min-'].update(visible=False)
            window['-ch2_max-'].update(visible=False)
            window['-ch3_min-'].update(visible=False)
            window['-ch3_max-'].update(visible=False)
            window['-ch4_min-'].update(visible=False)
            window['-ch4_max-'].update(visible=False)
            window['-ch2-'].update(visible=True)
    elif event == '-ch2_min_-':
        with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
            get_cal_val = ch2_min_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch2_min'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=True)
    elif event in ['N14', '115', '216', '317', '418', '519', 'S21', '622', '723', '824', '925', '026']:
        pre_ch2_min = window['ch2_min'].get()
        curr_ch2_min = f'{pre_ch2_min}{event[0]}'
        window['ch2_min'].update(value=curr_ch2_min)
    elif event == 'CLR20':
        window['ch2_min'].update("")
    elif event == 'EXT27':
        with open('/home/pi/Desktop/config/ch2_min.csv', 'w') as ch2_min_f:
            ch2_min_f.write(window.Element('ch2_min').Get())
        with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
            ch2_min_val = ch2_min_f.read()
            ch2_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_val, flags=re.DOTALL)
        window['-ch2_min_-'].update(f'SPEC MIN: {ch2_min_val}')
        with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
            ch2_max_val = ch2_max_f.read()
            ch2_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_val, flags=re.DOTALL)
        window['-ch2_max_-'].update(f'SPEC MAX: {ch2_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch2-'].update(visible=True)
    elif event == '-ch2_max_-':
        with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
            get_cal_val = ch2_max_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch2_max'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch2_max-'].update(visible=True)
    elif event in ['N28', '129', '230', '331', '432', '533', 'S35', '636', '737', '838', '939', '040']:
        pre_ch2_max = window['ch2_max'].get()
        curr_ch2_max = f'{pre_ch2_max}{event[0]}'
        window['ch2_max'].update(value=curr_ch2_max)
    elif event == 'CLR34':
        window['ch2_max'].update("")
    elif event == 'EXT41':
        with open('/home/pi/Desktop/config/ch2_max.csv', 'w') as ch2_max_f:
            ch2_max_f.write(window.Element('ch2_max').Get())
        with open("/home/pi/Desktop/config/ch2_min.csv", "r") as ch2_min_f:
            ch2_min_val = ch2_min_f.read()
            ch2_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_min_val, flags=re.DOTALL)
        window['-ch2_min_-'].update(f'SPEC MIN: {ch2_min_val}')
        with open("/home/pi/Desktop/config/ch2_max.csv", "r") as ch2_max_f:
            ch2_max_val = ch2_max_f.read()
            ch2_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch2_max_val, flags=re.DOTALL)
        window['-ch2_max_-'].update(f'SPEC MAX: {ch2_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch2-'].update(visible=True)
    elif event == 'ch2_save_and_exit':
        window['-start-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch-'].update(visible=True)



    elif event == 'ch_3':
        with open("/home/pi/Desktop/config/ch3_on_off_.csv", "r") as file:
            ch3_onof = file.read()
            ch3_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_onof, flags=re.DOTALL)
        window.Element('ch3_on_off').Update(('Off', 'On')[eval(ch3_onof)],
                                            button_color=(('white', ('red', 'green')[eval(ch3_onof)])))
        with open("/home/pi/Desktop/config/ch3_cal.csv", "r") as ch3_cal_f:
            ch3_cal_val = ch3_cal_f.read()
            ch3_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_cal_val, flags=re.DOTALL)
        window['-ch3_cal_-'].update(f'Ch3 CAL: {ch3_cal_val}')
        with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
            ch3_min_val = ch3_min_f.read()
            ch3_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_val, flags=re.DOTALL)
        window['-ch3_min_-'].update(f'SPEC MIN: {ch3_min_val}')
        with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
            ch3_max_val = ch3_max_f.read()
            ch3_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_val, flags=re.DOTALL)
        window['-ch3_max_-'].update(f'SPEC MAX: {ch3_max_val}')
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch3-'].update(visible=True)
    elif event == 'ch3_on_off':
        with open("/home/pi/Desktop/config/ch3_on_off_.csv", "r") as file:
            ch3_onof = file.read()
            ch3_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_onof, flags=re.DOTALL)
        ch3_value = not eval(ch3_onof)
        window.Element('ch3_on_off').Update(('Off', 'On')[ch3_value],
                                            button_color=(('white', ('red', 'green')[ch3_value])))
        with open('/home/pi/Desktop/config/ch3_on_off_.csv', 'w') as write_config_f:
            write_config_f.write(str(ch3_value))
    elif event == '-ch3_cal_-':
        ser_3.open()
        ch3_cal_thread = threading.Thread(target=read_cal3)
        ch3_cal_thread.start()
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch3_cal-'].update(visible=True)
    elif event in ['ch3_cal_up', 'ch3_cal_down', 'ch3_cal_save_exit']:
        with open("/home/pi/Desktop/config/ch3_cal.csv", "r") as ch3_cal_f:
            ch3_cal_val = ch3_cal_f.read()
            ch3_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_cal_val, flags=re.DOTALL)
        if event == 'ch3_cal_up':
            with open('/home/pi/Desktop/config/ch3_cal.csv', 'w') as ch3_cal_f:
                ch3_cal_f.write(str(int(ch3_cal_val) + 1))
        elif event == 'ch3_cal_down':
            with open('/home/pi/Desktop/config/ch3_cal.csv', 'w') as ch3_cal_f:
                ch3_cal_f.write(str(int(ch3_cal_val) - 1))
        elif event == 'ch3_cal_save_exit':
            if ser_3.isOpen():
                ser_3.close()
            with open("/home/pi/Desktop/config/ch3_cal.csv", "r") as ch3_cal_f:
                ch3_cal_val = ch3_cal_f.read()
                ch3_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_cal_val, flags=re.DOTALL)
            window['-ch3_cal_-'].update(f'Ch3 CAL: {ch3_cal_val}')
            with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
                ch3_min_val = ch3_min_f.read()
                ch3_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_val, flags=re.DOTALL)
            window['-ch3_min_-'].update(f'SPEC MIN: {ch3_min_val}')
            with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
                ch3_max_val = ch3_max_f.read()
                ch3_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_val, flags=re.DOTALL)
            window['-ch3_max_-'].update(f'SPEC MAX: {ch3_max_val}')
            window['-main-'].update(visible=False)
            window['-start-'].update(visible=False)
            window['-ch-'].update(visible=False)
            window['-ch1-'].update(visible=False)
            window['-ch2-'].update(visible=False)
            window['-ch4-'].update(visible=False)
            window['-ch1_cal-'].update(visible=False)
            window['-ch2_cal-'].update(visible=False)
            window['-ch3_cal-'].update(visible=False)
            window['-ch4_cal-'].update(visible=False)
            window['-ch1_min-'].update(visible=False)
            window['-ch1_max-'].update(visible=False)
            window['-ch2_min-'].update(visible=False)
            window['-ch2_max-'].update(visible=False)
            window['-ch3_min-'].update(visible=False)
            window['-ch3_max-'].update(visible=False)
            window['-ch4_min-'].update(visible=False)
            window['-ch4_max-'].update(visible=False)
            window['-ch3-'].update(visible=True)
    elif event == '-ch3_min_-':
        with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
            get_cal_val = ch3_min_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch3_min'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=True)
    elif event in ['N42', '143', '244', '345', '446', '547', 'S49', '650', '751', '852', '953', '054']:
        pre_ch3_min = window['ch3_min'].get()
        curr_ch3_min = f'{pre_ch3_min}{event[0]}'
        window['ch3_min'].update(value=curr_ch3_min)
    elif event == 'CLR48':
        window['ch3_min'].update("")
    elif event == 'EXT55':
        with open('/home/pi/Desktop/config/ch3_min.csv', 'w') as ch3_min_f:
            ch3_min_f.write(window.Element('ch3_min').Get())
        with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
            ch3_min_val = ch3_min_f.read()
            ch3_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_val, flags=re.DOTALL)
        window['-ch3_min_-'].update(f'SPEC MIN: {ch3_min_val}')
        with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
            ch3_max_val = ch3_max_f.read()
            ch3_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_val, flags=re.DOTALL)
        window['-ch3_max_-'].update(f'SPEC MAX: {ch3_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch3-'].update(visible=True)
    elif event == '-ch3_max_-':
        with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
            get_cal_val = ch3_max_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch3_max'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch3_max-'].update(visible=True)
    elif event in ['N56', '157', '258', '359', '460', '561', 'S63', '664', '765', '866', '967', '068']:
        pre_ch3_max = window['ch3_max'].get()
        curr_ch3_max = f'{pre_ch3_max}{event[0]}'
        window['ch3_max'].update(value=curr_ch3_max)
    elif event == 'CLR62':
        window['ch3_max'].update("")
    elif event == 'EXT69':
        with open('/home/pi/Desktop/config/ch3_max.csv', 'w') as ch3_max_f:
            ch3_max_f.write(window.Element('ch3_max').Get())
        with open("/home/pi/Desktop/config/ch3_min.csv", "r") as ch3_min_f:
            ch3_min_val = ch3_min_f.read()
            ch3_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_min_val, flags=re.DOTALL)
        window['-ch3_min_-'].update(f'SPEC MIN: {ch3_min_val}')
        with open("/home/pi/Desktop/config/ch3_max.csv", "r") as ch3_max_f:
            ch3_max_val = ch3_max_f.read()
            ch3_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch3_max_val, flags=re.DOTALL)
        window['-ch3_max_-'].update(f'SPEC MAX: {ch3_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch3-'].update(visible=True)
    elif event == 'ch3_save_and_exit':
        window['-start-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch-'].update(visible=True)



    elif event == 'ch_4':
        with open("/home/pi/Desktop/config/ch4_on_off_.csv", "r") as file:
            ch4_onof = file.read()
            ch4_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_onof, flags=re.DOTALL)
        window.Element('ch4_on_off').Update(('Off', 'On')[eval(ch4_onof)],
                                            button_color=(('white', ('red', 'green')[eval(ch4_onof)])))
        with open("/home/pi/Desktop/config/ch4_cal.csv", "r") as ch4_cal_f:
            ch4_cal_val = ch4_cal_f.read()
            ch4_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_cal_val, flags=re.DOTALL)
        window['-ch4_cal_-'].update(f'Ch4 CAL: {ch4_cal_val}')
        with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
            ch4_min_val = ch4_min_f.read()
            ch4_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_val, flags=re.DOTALL)
        window['-ch4_min_-'].update(f'SPEC MIN: {ch4_min_val}')
        with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
            ch4_max_val = ch4_max_f.read()
            ch4_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_val, flags=re.DOTALL)
        window['-ch4_max_-'].update(f'SPEC MAX: {ch4_max_val}')
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=True)
    elif event == 'ch4_on_off':
        with open("/home/pi/Desktop/config/ch4_on_off_.csv", "r") as file:
            ch4_onof = file.read()
            ch4_onof = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_onof, flags=re.DOTALL)
        ch4_value = not eval(ch4_onof)
        window.Element('ch4_on_off').Update(('Off', 'On')[ch4_value],
                                            button_color=(('white', ('red', 'green')[ch4_value])))
        with open('/home/pi/Desktop/config/ch4_on_off_.csv', 'w') as write_config_f:
            write_config_f.write(str(ch4_value))
    elif event == '-ch4_cal_-':
        ser_4.open()
        ch4_cal_thread = threading.Thread(target=read_cal4)
        ch4_cal_thread.start()
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch4_cal-'].update(visible=True)
    elif event in ['ch4_cal_up', 'ch4_cal_down', 'ch4_cal_save_exit']:
        with open("/home/pi/Desktop/config/ch4_cal.csv", "r") as ch4_cal_f:
            ch4_cal_val = ch4_cal_f.read()
            ch4_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_cal_val, flags=re.DOTALL)
        if event == 'ch4_cal_up':
            with open('/home/pi/Desktop/config/ch4_cal.csv', 'w') as ch4_cal_f:
                ch4_cal_f.write(str(int(ch4_cal_val) + 1))
        elif event == 'ch4_cal_down':
            with open('/home/pi/Desktop/config/ch4_cal.csv', 'w') as ch4_cal_f:
                ch4_cal_f.write(str(int(ch4_cal_val) - 1))
        elif event == 'ch4_cal_save_exit':
            if ser_4.isOpen():
                ser_4.close()
            with open("/home/pi/Desktop/config/ch4_cal.csv", "r") as ch4_cal_f:
                ch4_cal_val = ch4_cal_f.read()
                ch4_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_cal_val, flags=re.DOTALL)
            window['-ch4_cal_-'].update(f'Ch4 CAL: {ch4_cal_val}')
            with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
                ch4_min_val = ch4_min_f.read()
                ch4_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_val, flags=re.DOTALL)
            window['-ch4_min_-'].update(f'SPEC MIN: {ch4_min_val}')
            with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
                ch4_max_val = ch4_max_f.read()
                ch4_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_val, flags=re.DOTALL)
            window['-ch4_max_-'].update(f'SPEC MAX: {ch4_max_val}')
            window['-main-'].update(visible=False)
            window['-start-'].update(visible=False)
            window['-ch-'].update(visible=False)
            window['-ch1-'].update(visible=False)
            window['-ch2-'].update(visible=False)
            window['-ch3-'].update(visible=False)
            window['-ch1_cal-'].update(visible=False)
            window['-ch2_cal-'].update(visible=False)
            window['-ch3_cal-'].update(visible=False)
            window['-ch4_cal-'].update(visible=False)
            window['-ch1_min-'].update(visible=False)
            window['-ch1_max-'].update(visible=False)
            window['-ch2_min-'].update(visible=False)
            window['-ch2_max-'].update(visible=False)
            window['-ch3_min-'].update(visible=False)
            window['-ch3_max-'].update(visible=False)
            window['-ch4_min-'].update(visible=False)
            window['-ch4_max-'].update(visible=False)
            window['-ch4-'].update(visible=True)
    elif event == '-ch4_min_-':
        with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
            get_cal_val = ch4_min_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch4_min'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=True)
    elif event in ['N70', '171', '272', '373', '474', '575', 'S77', '678', '779', '880', '981', '082']:
        pre_ch4_min = window['ch4_min'].get()
        curr_ch4_min = f'{pre_ch4_min}{event[0]}'
        window['ch4_min'].update(value=curr_ch4_min)
    elif event == 'CLR76':
        window['ch4_min'].update("")
    elif event == 'EXT83':
        with open('/home/pi/Desktop/config/ch4_min.csv', 'w') as ch4_min_f:
            ch4_min_f.write(window.Element('ch4_min').Get())
        with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
            ch4_min_val = ch4_min_f.read()
            ch4_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_val, flags=re.DOTALL)
        window['-ch4_min_-'].update(f'SPEC MIN: {ch4_min_val}')
        with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
            ch4_max_val = ch4_max_f.read()
            ch4_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_val, flags=re.DOTALL)
        window['-ch4_max_-'].update(f'SPEC MAX: {ch4_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch4-'].update(visible=True)
    elif event == '-ch4_max_-':
        with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
            get_cal_val = ch4_max_f.read()
            get_cal_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', get_cal_val, flags=re.DOTALL)
        window['ch4_max'].update(get_cal_val)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=True)
    elif event in ['N84','185','286','387','488','589','S91','692','793','894','995','096']:
        pre_ch4_max = window['ch4_max'].get()
        curr_ch4_max = f'{pre_ch4_max}{event[0]}'
        window['ch4_max'].update(value=curr_ch4_max)
    elif event == 'CLR90':
        window['ch4_max'].update("")
    elif event == 'EXT97':
        with open('/home/pi/Desktop/config/ch4_max.csv', 'w') as ch4_max_f:
            ch4_max_f.write(window.Element('ch4_max').Get())
        with open("/home/pi/Desktop/config/ch4_min.csv", "r") as ch4_min_f:
            ch4_min_val = ch4_min_f.read()
            ch4_min_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_min_val, flags=re.DOTALL)
        window['-ch4_min_-'].update(f'SPEC MIN: {ch4_min_val}')
        with open("/home/pi/Desktop/config/ch4_max.csv", "r") as ch4_max_f:
            ch4_max_val = ch4_max_f.read()
            ch4_max_val = re.sub(r'(\n\[)(.*?)(\[]\n)', '', ch4_max_val, flags=re.DOTALL)
        window['-ch4_max_-'].update(f'SPEC MAX: {ch4_max_val}')
        window['-main-'].update(visible=False)
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch1_min-'].update(visible=False)
        window['-ch1_max-'].update(visible=False)
        window['-ch2_min-'].update(visible=False)
        window['-ch2_max-'].update(visible=False)
        window['-ch3_min-'].update(visible=False)
        window['-ch3_max-'].update(visible=False)
        window['-ch4_min-'].update(visible=False)
        window['-ch4_max-'].update(visible=False)
        window['-ch4-'].update(visible=True)
    elif event == 'ch4_save_and_exit':
        window['-start-'].update(visible=False)
        window['-main-'].update(visible=False)
        window['-ch1-'].update(visible=False)
        window['-ch2-'].update(visible=False)
        window['-ch3-'].update(visible=False)
        window['-ch4-'].update(visible=False)
        window['-ch-'].update(visible=True)

    elif event == 'EXIT':
        window['-start-'].update(visible=False)
        window['-ch-'].update(visible=False)
        window['-main-'].update(visible=True)

window.close()
