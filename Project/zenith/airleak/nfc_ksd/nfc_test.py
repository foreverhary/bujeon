import sys
from threading import Thread

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QApplication
from serial import Serial, SerialException

serial_name = ['com7', 'com19', 'com13', 'com10']


def serial_thread(s):
    # print(s)
    while True:
        try:
            print(s.port, s.readline())
        except SerialException:
            break
        except Exception as e:
            print(f"{s.port}, {type(e)} : {e}")


def connect_btn(btn, func):
    def inner():
        btn.clicked.connect(func)

    return inner


def open_nfc(nfc):
    if nfc.is_open:
        nfc.close()
    nfc.open()


def thread_nfc(th, nfc):
    if not th.is_alive():
        th = Thread(target=serial_thread, args=(nfc,), daemon=True)
        th.start()
    return th


def write_nfc(nfc, msg):
    if nfc.is_open:
        nfc.write(msg)


class NfcThread(Thread):
    def __init__(self, nfc):
        super(NfcThread, self).__init__()
        self.thread = True
        self.nfc = nfc
        self.daemon = True

    def run(self) -> None:
        self.nfc.flushInput()
        while True:
            if not self.thread:
                break
            try:
                if read_data := self.nfc.readline():
                    print(self.nfc.port, read_data)
            except Exception as e:
                print(self.nfc.port, f"{type(e)} : {e}")


class NfcTest(QWidget):
    def __init__(self):
        super(NfcTest, self).__init__()

        self.nfcs = [Serial() for _ in range(4)]

        for nfc, port in zip(self.nfcs, serial_name):
            nfc.port = port
            nfc.baudrate = 115200
            nfc.timeout = 0.5
            nfc.open()
        self.th = [NfcThread(nfc) for nfc in self.nfcs]

        self.setLayout(layout := QHBoxLayout())
        buttons = [QPushButton(str(index + 1)) for index in range(4)]
        for button in buttons:
            button.clicked.connect(self.button_clicked)
            layout.addWidget(button)

        layout.addWidget(odd_button := QPushButton('ODD'))
        odd_button.clicked.connect(self.odd_even_button)
        layout.addWidget(even_button := QPushButton('EVEN'))
        even_button.clicked.connect(self.odd_even_button)

        self.show()
        # self.showFullScreen()

    def odd_even_button(self):
        button = self.sender().text()
        for i in range(2):
            if button == 'ODD':
                nfc = self.nfcs[i * 2]
                open_nfc(nfc)
                self.th[i * 2] = NfcThread(nfc)
                self.th[i * 2].start()
                write_nfc(self.nfcs[i * 2 + 1], b'\xff')
                self.th[i * 2 + 1].thread = False
            else:
                nfc = self.nfcs[i * 2 + 1]
                open_nfc(nfc)
                self.th[i * 2 + 1] = NfcThread(nfc)
                self.th[i * 2 + 1].start()
                write_nfc(self.nfcs[i * 2], b'\xff')
                self.th[i * 2].thread = False

    def button_clicked(self):
        print(self.sender().text())
        button = int(self.sender().text()) - 1
        nfc = self.nfcs[button]
        open_nfc(nfc)
        self.th[button] = NfcThread(nfc)
        self.th[button].start()

        a = [0, 1, 2, 3]
        a.remove(button)
        for i in a:
            write_nfc(self.nfcs[i], b'\xff')
            self.th[i].thread = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NfcTest()
    sys.exit(app.exec_())
