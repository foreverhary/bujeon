import PySimpleGUI as sg
import ast
from serial import Serial
import numpy as np
import time
import os
import threading

ser = [Serial(), Serial()]
# ser.port = 'COM11'
# ser[0].port = '/dev/ttyUSB0'
ser[0].port = 'com8'
ser[0].baudrate = 115200
# ser[1].port = '/dev/ttyUSB1'
ser[1].port = 'com10'
ser[1].baudrate = 115200

layout = [[sg.B(f'{i + 1 + j * 10}', size=(8, 4), key=f'ir_{i + 1 + j * 10}') for i in range(0, 10)] for j in
          range(0, 10)]
window = sg.Window('10 x 10', layout).Finalize()


def read_():
    array = [index for index in range(100)]
    while True:
        arrayL = list()
        arrayR = list()
        for s in ser:
            if not s.isOpen(): s.open()
            characterSide = s.read()
            if characterSide == b'L':
                arrayL = splitData(s)
            elif characterSide == b'R':
                arrayR = splitData(s)
            else:
                continue
        array = arrayL + arrayR
        for i, value in enumerate(array):
            try:
                color = 'red' if int(value) > 30000 else 'blue'
                window.Element(f'ir_{i + 1}').Update(value, button_color=('white', color))
            except Exception as e:
                print(array)
                print(e)
                os._exit(1)
                break
        array.clear()


def splitData(s):
    inputData = ''
    character = ''
    while character != '\n':
        inputData += character
        character = s.read().decode()
    print(inputData)
    return inputData.replace('\r', '').replace('\n', '').split(',')[1:]


read_thread_1 = threading.Thread(target=read_)
read_thread_1.start()

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, "-ESCAPE-"):
        os._exit(1)
        break
