import time
import PySimpleGUI as sg
from serial import Serial, SerialException
import serial.tools.list_ports as sp
import os
import threading

FONT_SIZE = 30

sg.theme('DarkBlack1')

layout = [[sg.Button("RESET", key='RESET', size=(20, 1), font=('Helvetica', FONT_SIZE))],
          [sg.Text("        IR", key="IR", size=(10, 1), font=('Helvetica', FONT_SIZE)),
           sg.Text("      HALL", key="HALL", size=(10, 1), font=('Helvetica', FONT_SIZE))],
          [sg.Input(key='-IR-', size=(10, 1), font=('Helvetica', FONT_SIZE)),
           sg.Input(key='-HALL-', size=(10, 1), font=('Helvetica', FONT_SIZE))]]

window = sg.Window('IR & HALL', layout).Finalize()
hall = []


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
            window.close()
            os._exit(1)


def ir_display(value):
    if 140 < value < 4500:
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
    hall.insert(0, value)
    if len(hall) > 10:
        hall.pop()

    if any(l for l in hall if l != -1):
        if -5000 < hall[0] < -1000:
            window['-HALL-'].update('OK', background_color='lightskyblue')
        else:
            window['-HALL-'].update(f'NG({hall[0]})', background_color='red')
    else:
        window['-HALL-'].update('OPEN', background_color='gray')


def make_serial(com):
    try:
        return Serial(com, 115200, timeout=0.3)
    except:
        return None


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
