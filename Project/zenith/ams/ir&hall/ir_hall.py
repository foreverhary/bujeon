import csv
import time
import PySimpleGUI as sg
from serial import Serial, SerialException
import serial.tools.list_ports as sp
import os
import threading

FONT_SIZE = 50
SETTING_FILE = 'config.csv'

sg.theme('DarkBlack1')

layout = [[sg.Button("RESET", key='RESET', size=(20, 1), font=('Helvetica', FONT_SIZE))],
          [sg.Text("        IR", key="IR", size=(10, 1), font=('Helvetica', FONT_SIZE)),
           sg.Text("      HALL", key="HALL", size=(10, 1), font=('Helvetica', FONT_SIZE))],
          [sg.Input(key='-IR-', size=(10, 1), font=('Helvetica', FONT_SIZE)),
           sg.Input(key='-HALL-', size=(10, 1), font=('Helvetica', FONT_SIZE))]]

window = sg.Window('IR : 100 ~ 6000, HALL : -6000 ~ -100', layout).Finalize()
hall = []

ir_min = 100
ir_max = 6000
hall_min = -6000
hall_max = -100


def init_cfg():
    global ir_min, ir_max, hall_min, hall_max
    with open(SETTING_FILE, 'w') as f:
        wr = csv.writer(f)
        wr.writerow(['IR', ir_min, ir_max])
        wr.writerow(['HALL', hall_min, hall_max])


def read_cfg():
    global ir_min, ir_max, hall_min, hall_max
    if not os.path.isfile(SETTING_FILE):
        init_cfg()
        return

    with open(SETTING_FILE, 'r') as f:
        rd = csv.reader(f)

        for line in rd:
            if not line:
                continue
            if line[0] == 'IR':
                ir_min, ir_max = list(map(int, line[1:3]))
            if line[0] == 'HALL':
                hall_min, hall_max = list(map(int, line[1:3]))


def dtr_brige(ser):
    ser.dtr = True
    thread = threading.Timer(1.5, read_ir_hall, args=(ser,))
    thread.daemon = True
    thread.start()


def read_ir_hall(ser):
    ser.readline()
    input_display_color = 'white'
    count = 0
    while True:
        try:
            raw_data = str(ser.readline().decode('utf-8'))
            if not raw_data:
                ser.dtr = False
                # print("dtr false")
                thread = threading.Timer(0.5, dtr_brige, args=(ser,))
                thread.daemon = True
                thread.start()
                break
            if count > 20:
                count = 0
                if input_display_color == 'yellow':
                    input_display_color = 'lightskyblue'
                else:
                    input_display_color = 'yellow'
            count += 1
            window['IR'].update(text_color=input_display_color)
            window['HALL'].update(text_color=input_display_color)
            # print(raw_data)
            raw_data = raw_data.rstrip()
            raw_data = raw_data.split(",")
            ir_display(int(raw_data[0][3:]))
            hall_background_color(int(raw_data[1][5:]))
        except SerialException as e:
            print(e)
            # window.close()
            # os._exit(1)
        except Exception as e:
            print(e)


def ir_display(value):
    global ir_min, ir_max
    if ir_min < value < ir_max:
        result = 'OK'
        color = 'lightskyblue'
    elif value == 65535:
        result = 'OPEN'
        color = 'gray'
    else:
        result = 'NG'
        color = 'red'

    window['-IR-'].update(result, background_color=color)


def hall_background_color(value):
    global hall_min, hall_max
    hall.insert(0, value)
    if len(hall) > 10:
        hall.pop()

    if any(l for l in hall if l != -1):
        if hall_min < hall[0] < hall_max:
            window['-HALL-'].update('OK', background_color='lightskyblue')
        else:
            window['-HALL-'].update('NG', background_color='red')
    else:
        window['-HALL-'].update('OPEN', background_color='gray')


def make_serial(com):
    try:
        return Serial(com, 115200, timeout=0.3)
    except:
        return None


# read_cfg()

count = 0
ser_list = []
for port in sp.comports():
    count += 1
    if s := make_serial(port.device):
        ser_list.append(s)
        thread = threading.Timer(1.5, read_ir_hall, args=(s,))
        thread.daemon = True
        thread.start()
        # threading.Thread(target=read_ir_hall, args=(s,), daemon=True).start()

if not count:
    os._exit(1)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        os._exit(1)
        break
    if event == 'RESET':
        for ser in ser_list:
            ser.dtr = False
        time.sleep(0.5)
        for ser in ser_list:
            ser.dtr = True
