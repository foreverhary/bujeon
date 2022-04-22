import PySimpleGUI as sg
from serial import Serial
import os
import re
import threading

sg.theme('DarkBlack1')

ser = Serial()
ser.port = '/dev/cu.usbmodem114301'
ser.baudrate = 115200
ser.stopbits = 1
ser.bytesize = 8
ser.parity = 'N'

probe_1_layout = [[sg.Text('POT1 S1000 ~ S1000', size=(17, 1), font=('Helvetica', 22), key='probe_1_thd')],
                  [sg.Text('', size=(1, 2))],
                  [sg.Text('', size=(7, 1), font=('Helvetica', 38), key='probe_1'),
                   sg.Text('OK', size=(4, 1), font=('Helvetica', 37), key='probe_1_result')],
                  [sg.Text('')]]
probe_2_layout = [[sg.Text('POT2 S1000 ~ S1000', size=(17, 1), font=('Helvetica', 22), key='probe_2_thd')],
                  [sg.Text('', size=(1, 2))],
                  [sg.Text('', size=(7, 1), font=('Helvetica', 38), key='probe_2'),
                   sg.Text('OK', size=(4, 1), font=('Helvetica', 37), key='probe_2_result')],
                  [sg.Text('')]]
probe_3_layout = [[sg.Text('POT3 S1000 ~ S1000', size=(17, 1), font=('Helvetica', 22), key='probe_3_thd')],
                  [sg.Text('', size=(1, 2))],
                  [sg.Text('', size=(7, 1), font=('Helvetica', 38), key='probe_3'),
                   sg.Text('OK', size=(4, 1), font=('Helvetica', 37), key='probe_3_result')],
                  [sg.Text('')]]
probe_4_layout = [[sg.Text('POT4 S1000 ~ S1000', size=(17, 1), font=('Helvetica', 22), key='probe_4_thd')],
                  [sg.Text('', size=(1, 2))],
                  [sg.Text('', size=(7, 1), font=('Helvetica', 38), key='probe_4'),
                   sg.Text('OK', size=(4, 1), font=('Helvetica', 37), key='probe_4_result')],
                  [sg.Text('')]]
probe_5_layout = [[sg.Text('POT5 S1000 ~ S1000', size=(17, 1), font=('Helvetica', 22), key='probe_5_thd')],
                  [sg.Text('', size=(1, 2))],
                  [sg.Text('', size=(7, 1), font=('Helvetica', 38), key='probe_5'),
                   sg.Text('OK', size=(4, 1), font=('Helvetica', 37), key='probe_5_result')],
                  [sg.Text('')]]
probe_result_layout = [[sg.Text('', font=('Helvetica', 70), key='probe_result')]]

main_layout = [[sg.Frame('', [[sg.Column(probe_1_layout, size=(240, 180))]]),
                sg.Frame('', [[sg.Column(probe_2_layout, size=(240, 180))]]),
                sg.Frame('', [[sg.Column(probe_result_layout, size=(240, 180))]])],
               [sg.Frame('', [[sg.Column(probe_3_layout, size=(240, 180))]]),
                sg.Frame('', [[sg.Column(probe_4_layout, size=(240, 180))]]),
                sg.Frame('', [[sg.Column(probe_5_layout, size=(240, 180))]])],
               [[sg.B('CALIBRATION', size=(33, 1), font=('Helvetica', 40))]]]

window = sg.Window('', main_layout, size=(800, 480)).Finalize()
running = 0


def read_probe():
    try:
        while True:
            read_val_from_plobe = ser.readline().decode().split(",")
            if float(read_val_from_plobe[0]) > 0:
                window.Element('probe_1').Update(f'N{abs(int(float(read_val_from_plobe[0])))}G')
            else:
                window.Element('probe_1').Update(f'S{abs(int(float(read_val_from_plobe[0])))}G')

            if float(read_val_from_plobe[1]) > 0:
                window.Element('probe_2').Update(f'N{abs(int(float(read_val_from_plobe[1])))}G')
            else:
                window.Element('probe_2').Update(f'S{abs(int(float(read_val_from_plobe[1])))}G')

            if float(read_val_from_plobe[2]) > 0:
                window.Element('probe_3').Update(f'N{abs(int(float(read_val_from_plobe[2])))}G')
            else:
                window.Element('probe_3').Update(f'S{abs(int(float(read_val_from_plobe[2])))}G')

            if float(read_val_from_plobe[3]) > 0:
                window.Element('probe_4').Update(f'N{abs(int(float(read_val_from_plobe[3])))}G')
            else:
                window.Element('probe_4').Update(f'S{abs(int(float(read_val_from_plobe[3])))}G')

            if float(read_val_from_plobe[4]) > 0:
                window.Element('probe_5').Update(f'N{abs(int(float(read_val_from_plobe[4])))}G')
            else:
                window.Element('probe_5').Update(f'S{abs(int(float(read_val_from_plobe[4])))}G')

    except Exception as e:
        print("type error: " + str(e))


while True:
    button, values = window.read(timeout=1000)
    print(button)
    if button in (sg.WINDOW_CLOSED, "-ESCAPE-"):
        os._exit(1)
        break

    if running == 0:
        ser.open()
        running = 1
        read_probe_thread = threading.Thread(target=read_probe)
        read_probe_thread.start()
    
    if button == "CALIBRATION":
        ser.close()


window.close()
print("test")