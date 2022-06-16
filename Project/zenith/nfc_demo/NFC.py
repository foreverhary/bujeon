from random import randint
from threading import Thread, Timer

from PySide2.QtCore import Signal, QObject
from serial import Serial


class Signal(QObject):
    signal_dtr = Signal()
    signal_read_msg = Signal(str)


class VirtualNFC(Serial):
    def __init__(self, index, com):
        super(VirtualNFC, self).__init__()
        self.signal = Signal()
        self.port = com
        self.serial_index = index
        self.baudrate = 115200
        self.open()
        self.uid = ' '.join(['UID:'] + ['0x' + format(randint(0, 255), '02x').upper() for _ in range(7)])
        self.th_dtr = Thread(target=self.checking_dtr, daemon=True)
        self.th_dtr.start()
        self.read_forever = Thread(target=self.nfc_read_forever, daemon=True)
        self.read_forever.start()

    def send_msg(self, msg):
        for _ in range(2):
            send_msg = ','.join([self.uid, msg]) if msg else self.uid
            send_msg += '\r\n'
            self.write(send_msg.encode())

    def action_dtr(self):
        if self.dtr:
            if self.serial_index:
                self.write(f"NFC {self.serial_index}\r\n".encode())
            else:
                self.write(b"NFC IN 1\r\n")

    def checking_dtr(self):
        if self.dsr:
            while self.dsr:
                pass
        else:
            while not self.dsr:
                pass

        self.signal.signal_dtr.emit()
        dsr_timer = Timer(1, self.checking_dtr)
        dsr_timer.daemon = True
        dsr_timer.start()
        timer = Timer(1, self.action_dtr)
        timer.daemon = True
        timer.start()

    def nfc_read_forever(self):
        print('forever start')
        while True:
            while self.inWaiting():
                print(self.inWaiting())
                msg = self.read_all().decode()
                print(msg)
                self.signal.signal_read_msg.emit(msg)
                # self.send_msg(msg)
