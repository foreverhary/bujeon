
import PySimpleGUI as sg
from serial import Serial, SerialException
import serial.tools.list_ports as sp
import os
import threading

sg.theme('DarkBlack1')

layout = [[sg.Text("        IR", size=(10, 1), font=('Helvetica', 50)),
           sg.Text("      HALL", size=(10, 1), font=('Helvetica', 50), )],
          [sg.Input(key='-IR-', size=(10, 1), font=('Helvetica', 50)),
           sg.Input(key='-HALL-', size=(10, 1), font=('Helvetica', 50))]]

window = sg.Window('IR & HALL', layout).Finalize()
hall = []


def read_ir_hall(ser):
    ser.readline()
    while True:
        try:
            raw_data = str(ser.readline().decode('utf-8'))
            if not raw_data:
                ser.close()
                break
            raw_data = raw_data.rstrip()
            raw_data = raw_data.split(",")
            ir_display(int(raw_data[0][3:]))
            hall_background_color(int(raw_data[1][5:]))
        except SerialException:
            window.close()
            os._exit(1)
        except:
            pass


def ir_display(value):
    result = 'OK' if 140 < value < 4500 else 'NG'
    window['-IR-'].update(result, background_color=('red', 'lightskyblue')[result == 'OK'])


def hall_background_color(value):
    hall.insert(0, value)
    if len(hall) > 10:
        hall.pop()

    if any([l for l in hall if l != -1]):
        window['-HALL-'].update('OK', background_color='lightskyblue')
    else:
        window['-HALL-'].update('NG', background_color='red')


def make_serial(com):
    try:
        return Serial(com, 115200, timeout=3)
    except:
        return None


count = 0

for port in sp.comports():
    count += 1
    if s := make_serial(port.device):
        threading.Thread(target=read_ir_hall, args=(s,), daemon=True).start()

if not count:
    os._exit(1)


while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        os._exit(1)
        break
