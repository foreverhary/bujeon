from threading import Thread

from PySide2.QtCore import QObject, Signal, QTimer
from serial import Serial

from process_package.defined_serial_port import get_serial_available_list
from process_package.resource.string import STR_NFC
from process_package.tools.CommonFunction import logger


class SearchNFC(QObject):
    def __init__(self, model):
        super(SearchNFC, self).__init__()
        self._model = model
        self.ports = get_serial_available_list()
        self.nfcs = {}

        self._model.status = "NFC Searching..."
        Thread(target=self.search, daemon=True).start()

    def search(self):
        th = []
        for port in self.ports:
            if 'COM' in port:
                t = Thread(target=self.nfc_check, args=(port,), daemon=True)
                t.start()
                th.append(t)
        for t in th:
            t.join()
        self._model.nfc = self.nfcs

    def nfc_check(self, port):
        ser = Serial(port, 115200, timeout=2)
        self.is_nfc(ser)

    def is_nfc(self, ser):
        try:
            ser.open()
            data = ser.readline().decode().replace('\r', '').replace('\n', '')
            if STR_NFC in data:
                self.nfcs[ser.port] = data
            ser.close()
        except Exception as e:
            logger.error(f"{ser.port} : {type(e)}, {e}")
            if ser.is_open:
                ser.close()
