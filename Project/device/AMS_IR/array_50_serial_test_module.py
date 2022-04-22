import time
import threading
from serial import Serial
import random as rd
import sys


def sending_serial(ser, lr):
    while True:
        if not ser.isOpen():
            ser.open()
        send_data = str()
        send_data += lr + ','

        for index in range(49):
            send_data += str(rd.randint(0, 32000))
            send_data += ','
        send_data += str(rd.randint(0, 32000))
        send_data += "\n"
        ser.write(send_data.encode())
        time.sleep(0.2)


def main(argv):
    sers = [Serial() for l in range(2)]
    for index, ser in enumerate(sers):
        ser.port = argv[index + 1]
        ser.baudrate = 115200
        send_thread = threading.Thread(target=sending_serial, args=(ser, ('L', 'R')[index]))
        send_thread.start()


if __name__ == "__main__":
    main(sys.argv)
