from threading import Thread

from PySide2.QtCore import QObject, Signal, QTimer
from serial import Serial

from process_package.defined_serial_port import get_serial_available_list
from process_package.defined_variable_function import logger
from process_package.resource.string import STR_NFC


class NFCCheck(QObject):
    serial_check_done = Signal(dict)

    def __init__(self):
        super(NFCCheck, self).__init__()
        self.timer = None
        self.nfcs = None
        self.available = get_serial_available_list()

        self.counter = 0
        self.jumper = 0

        Thread(target=self.search_nfcs, daemon=True).start()

    def search_nfcs(self):
        logger.debug("search NFC")
        thread = []
        nfcs = {}
        logger.info(self.available)
        for port in self.available:
            if 'COM' in port:
                t = Thread(target=self.check_nfc, args=(port, nfcs), daemon=True)
                t.start()
                thread.append(t)
        for t in thread:
            t.join()
        for name, port in nfcs.items():
            logger.info(f"{name} : {port}")
        self.nfcs = nfcs
        self.serial_check_done.emit(self.nfcs)

    def check_nfc(self, port, nfcs):
        ser = Serial(port, 115200, timeout=2)
        if nfc_id := ser.readline().decode().rstrip('\n').rstrip('\r'):
            if STR_NFC in nfc_id:
                nfcs.setdefault(nfc_id.replace(' ', '').upper(), port)
                logger.info(f"{nfc_id} : {port}")
        ser.close()

if __name__ == '__main__':
    a = NFCCheck()
