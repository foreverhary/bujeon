import queue
import PySimpleGUI as sg
import ast
from serial import Serial
import numpy as np
import time
import os
from threading import Thread

ser = [Serial(), Serial()]
# ser.port = 'COM11'
# ser[0].port = '/dev/ttyUSB0'
ser[0].port = 'com5'
ser[0].baudrate = 115200
# ser[1].port = '/dev/ttyUSB1'
ser[1].port = 'com6'
ser[1].baudrate = 115200

layout = [[sg.B(f'{i + 1 + j * 10}', size=(8, 4), key=f'ir_{i + 1 + j * 10}') for i in range(0, 10)] for j in
          range(0, 10)]
window = sg.Window('10 x 10', layout, return_keyboard_events=True).Finalize()

b_array = [index for index in range(100)]
a_array = [index for index in range(100)]
array = [index for index in range(100)]


def thread_start(thread):
    thread.start()


def thread_join(thread):
    thread.join()


def read_first(index):
    s = ser[index]
    if not s.isOpen(): s.open()
    accumulate_num = 0
    open_N = 20
    open_ten = list()
    s.flushInput()

    for i in range(open_N):
        s.readline()
        reci_data = s.readline()
        print(reci_data)
        decode_reci_data = reci_data.decode().replace('\r', '').replace('\n', '').split(',')
        l_or_r = decode_reci_data[0]
        while 'R' != l_or_r != 'L' or len(decode_reci_data) != 51:
            reci_data = s.readline()
            decode_reci_data = reci_data.decode().replace('\r', '').replace('\n', '').split(',')
            l_or_r = decode_reci_data[0]
        open_ten.append(decode_reci_data[1:])

    array_half = np.array(open_ten, dtype=int)
    array_half_aver = np.mean(array_half, axis=0, dtype=int).tolist()
    array_half_aver.append(l_or_r)
    return array_half_aver


que = queue.Queue()


def run_read_thread(arr):
    read_thread = [Thread(target=lambda q, arg1: q.put(read_first(arg1)), args=(que, index)) for index in range(2)]
    list(map(thread_start, read_thread))
    list(map(thread_join, read_thread))
    while not que.empty():
        h_array = que.get()
        lr_index = 50 if h_array[-1] == 'R' else 0
        arr[lr_index:lr_index + 50] = h_array[:-1]


done = False

run_read_thread(b_array)

for i, value in enumerate(b_array):
    window.Element(f'ir_{i + 1}').Update(value, button_color=('black', 'yellow'))

while True:
    event, values = window.read()
    print(event)
    if event in (sg.WINDOW_CLOSED, "-ESCAPE-"):
        os._exit(1)
        break

    if event == '\r':
        if not done:
            run_read_thread(a_array)

            array = np.subtract(a_array, b_array)

            for i, value in enumerate(array):
                if abs(value) > 1000:
                    window.Element(f'ir_{i + 1}').Update(abs(value), button_color=('white', 'red'))
                else:
                    window.Element(f'ir_{i + 1}').Update(abs(value), button_color=('white', 'blue'))
            done = True
        else:
            run_read_thread(b_array)

            for i, value in enumerate(b_array):
                window.Element(f'ir_{i + 1}').Update(value, button_color=('black', 'yellow'))
            done = False

    # elif event ==
