import re
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject
from serial import Serial, SerialException

from process_package.check_string import check_nfc_uid, check_dm
from process_package.defined_variable_function import SENSOR_PREPROCESS, OK, A, B, C, logger, LIGHT_SKY_BLUE, RED, NFC


class SerialNFCSignal(QObject):
    previous_process_signal = pyqtSignal(tuple)
    qr_write_done_signal = pyqtSignal(str, str)
    nfc_write_done_signal = pyqtSignal(object)
    serial_error_signal = pyqtSignal(str)


class SerialNFC(Serial):
    """
    NFC Serial
    param signal
    param serial_name
    param nfc_previous_process: previous process results read from NFC
    param current_process_result
    param previous_process_list: list of previous processes to be confirmed
    """

    def __init__(self, port=None, baudrate=None, timeout=None, serial_name=None):
        super(SerialNFC, self).__init__()

        self.signal = SerialNFCSignal()

        # default serial value + name
        self.port, self.baudrate, self.timeout, self.serial_name = port, baudrate, timeout, serial_name

        # uid and dm
        self.checked_uid = self.uid = None
        self.write_msg = self.checked_dm = self.dm = self.write_dm = None
        self.dm_list = []

        self.unit_count = 0

        # previous process
        self.nfc_previous_process = self.current_process_result = self.previous_process_list = None

        # dummy Thread
        self.th = Thread(target=self.nfc_qr_write_thread, daemon=True)

    @property
    def uid(self):
        return self._uid

    @uid.setter
    def uid(self, uid):
        self._uid = ''
        if isinstance(uid, str):
            self._uid = check_nfc_uid(uid)
        if self._uid:
            self.dm = None

    @property
    def dm(self):
        return self._dm

    @dm.setter
    def dm(self, dm):
        self._dm = ''
        if isinstance(dm, str):
            self._dm = check_dm(dm)

    @property
    def nfc_previous_process(self):
        return self._nfc_previous_process_list

    @nfc_previous_process.setter
    def nfc_previous_process(self, item):
        self._nfc_previous_process_list = []
        self.nfc_previous_process_str = item
        if isinstance(item, list) and self.previous_process_list:
            item_iter = iter(item)
            try:
                for previous_process in self.previous_process_list:
                    process_name, value = next(item_iter).split(':')
                    if previous_process != process_name or value not in [OK, A, B, C]:
                        break
                else:
                    self._nfc_previous_process_list = ','.join(item)
            except Exception as e:
                logger.warning(f"{type(e)} : {e}")
                logger.warning(self.previous_process_list)
                logger.warning(item)

    @property
    def nfc_previous_process_str(self):
        return self._nfc_previous_process_str

    @nfc_previous_process_str.setter
    def nfc_previous_process_str(self, item):
        self._nfc_previous_process_str = ''
        if isinstance(item, str):
            self._nfc_previous_process_str = item
        if isinstance(item, list):
            self._nfc_previous_process_str = ','.join(item)

    @property
    def current_process_result(self):
        return self._current_process_result

    @current_process_result.setter
    def current_process_result(self, value):
        self._current_process_result = value if isinstance(value, str) else ''

    def is_nfc(self):
        return_value = False
        try:
            self.open()
            if check_string := self.readline().decode().replace('\r\n', ''):
                if re.search(NFC, check_string):
                    self.timeout = None
                    self.serial_name = check_string.replace(' ', '').upper()
                    return_value = True
                else:
                    self.is_open_close()
            else:
                self.is_open_close()
        except (SerialException, UnicodeDecodeError) as e:
            self.is_open_close()
        return return_value

    def start_previous_process_check_thread(self):
        self.th = Thread(target=self.previous_process_check_thread, daemon=True)
        self.th.start()

    def previous_process_check_thread(self):
        self.flushInput()
        while True:
            try:
                if self.check_read_line_data():
                    if self.checked_uid == self.uid:
                        continue
                    if not self.dm:
                        self.signal.previous_process_signal.emit(
                            (self.serial_name, "NFC TAG is not Normal", RED)
                        )

                    elif self.nfc_previous_process:
                        self.signal.previous_process_signal.emit(
                            (self.serial_name, f"{self.dm} is PASS", LIGHT_SKY_BLUE)
                        )
                    else:
                        self.signal.previous_process_signal.emit(
                            (self.serial_name, f"{self.dm} is FAIL", RED)
                        )
                    if self.dm:
                        self.checked_uid, self.checked_dm = self.uid, self.dm
            except SerialException:
                logger.error(SerialException)
                self.signal.serial_error_signal.emit("ERROR NFC PLEASE RESTART PROGRAM")
                break
            except UnicodeDecodeError as e:
                logger.error(f"{type(e)} : {e}")

    def check_nfc_split_data(self, read_data):
        logger.info(read_data)
        split_data = read_data.split(b',')
        iter_data = iter(split_data)
        try:
            self.uid = next(iter_data).decode()
            self.dm = next(iter_data).decode()
            if iter_data.__length_hint__():
                self.nfc_previous_process = [x.decode() for x in iter_data]
        except (StopIteration, UnicodeDecodeError, Exception) as e:
            logger.error(f"{type(e)} : {e}")
        return self.uid

    def check_read_line_data(self):
        return self.check_nfc_split_data(self.readline().split(b'\r\n')[0])

    def start_nfc_write(self, dm=None, process_result=None, unit_count=1):
        self.write_dm, self.unit_count = dm, unit_count
        self.current_process_result = process_result
        self.dm = None
        self.dm_list = []
        if not self.th.is_alive():
            if self.write_dm:
                self.th = Thread(target=self.nfc_qr_write_thread, daemon=True)
            else:
                self.th = Thread(target=self.nfc_write_thread, daemon=True)
            self.th.start()

    def nfc_qr_write_thread(self):
        try:
            self.flushInput()
            self.flushOutput()
            while self.check_read_line_data() and self.dm != self.write_dm:
                self.write(f"{self.write_dm}".encode())
            self.write_dm = None
            self.signal.qr_write_done_signal.emit("WRITE DONE, TRY NEXT QR SCAN", LIGHT_SKY_BLUE)
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            self.signal.qr_write_done_signal.emit("CHECK NFC AND RESTART PROGRAM!!", RED)

    def make_write_nfc(self):
        self.write_msg = self.dm
        self.write_msg += f",{self.nfc_previous_process}" if self.nfc_previous_process else ''
        self.write_msg += f",{self.current_process_result}" if self._current_process_result else ''
        return self.write_msg

    def nfc_write_thread(self):
        self.flushInput()
        self.flushOutput()
        while self.unit_count:
            try:
                if self.check_read_line_data():
                    if self.dm in self.dm_list:
                        continue
                    elif self.write_msg == ','.join([self.dm, self.nfc_previous_process_str]):
                        self.dm_list.append(self.dm)
                        self.unit_count -= 1
                        self.signal.nfc_write_done_signal.emit(self)
                    elif self.uid and self.dm:
                        self.write(f"{self.make_write_nfc()}".encode())
                        self.checked_dm = self.dm
            except SerialException as e:
                logger.error(f"{type(e)} : {e}")
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def is_open_close(self):
        if self.is_open:
            self.close()


if __name__ == '__main__':
    ser = SerialNFC('com10', 115200, timeout=2)
    if ser.is_nfc():
        ser.start_previous_process_check_thread(SENSOR_PREPROCESS)

    while True:
        pass
