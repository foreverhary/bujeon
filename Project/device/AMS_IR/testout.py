import sys
from random import randint
from threading import Thread
from time import sleep

import serial
from serial import Serial


def _send_test_serial(com, side):
    ser = Serial(com, 115200)
    while True:
        txt = side
        for _ in range(49):
            txt += str(randint(0,10000)) + ','
        txt += str(randint(0,10000)) + '\r\n'
        ser.write(txt.encode())
        sleep(0.1)


def main(argv):
    if argv.__len__() < 3:
        print('need more args')
        return

    thread_a = Thread(target=_send_test_serial, args=(argv[1], 'L,'))
    thread_b = Thread(target=_send_test_serial, args=(argv[2], 'R,'))
    thread_a.start()
    thread_b.start()

if __name__ == '__main__':
    main(sys.argv)