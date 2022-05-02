import re
from threading import Thread

from PyQt5.QtCore import pyqtSignal, QObject
from serial import Serial, SerialException

from process_package.check_string import check_nfc_uid, check_dm
from process_package.defined_variable_function import SENSOR_PREPROCESS, logger, LIGHT_SKY_BLUE, RED, NFC, \
    PROCESS_RESULTS, PROCESS_NAMES, PROCESS_OK_RESULTS


class SerialNFCSignal(QObject):
    previous_process_signal = pyqtSignal(object)
    qr_write_done_signal = pyqtSignal(str, str)
    nfc_write_done_signal = pyqtSignal(object)
    serial_error_signal = pyqtSignal(str)


class SerialNFC(Serial):
    """
    NFC Serial
    param signal
    param serial_name
    param nfc_previous_process: previous process results read from NFC
    param current_process_result: machine result
    param previous_process_list: list of previous processes to be confirmed
    """

    def __init__(self, port=None, baudrate=None, timeout=None, serial_name=None):
        super(SerialNFC, self).__init__()

        self.signal = SerialNFCSignal()

        # default serial value + name
        self.port, self.baudrate, self.timeout, self.serial_name = port, baudrate, timeout, serial_name

        # uid and dm
        self.write_msg = self.uid = self.dm = self.write_dm = ''
        self.dm_list = []

        self.unit_count = 0

        # previous process
        self.nfc_previous_process = self.current_process_result = self.previous_processes = ''

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
        elif isinstance(dm, list):
            self._dm = check_dm(dm[0])

    @property
    def nfc_previous_process(self):
        return self._nfc_previous_process

    @nfc_previous_process.setter
    def nfc_previous_process(self, saved_processes):
        self._nfc_previous_process = {}
        if isinstance(saved_processes, list):
            try:
                for saved_process in saved_processes:
                    process_name, process_result = saved_process.split(':')
                    self._nfc_previous_process[process_name] = process_result
            except Exception as e:
                logger.warning(f"{type(e)} : {e}")
                self._nfc_previous_process = {}

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
                split_data = self.readline().decode().replace('\r\n', '').split(',')

                if not self.is_valid_input(split_data):
                    continue
                self.nfc_previous_process = split_data[2:]
                self.signal.previous_process_signal.emit(self)
            except (UnicodeDecodeError, ValueError) as e:
                logger.error(f"{type(e)} : {e}")
            except SerialException:
                logger.error(SerialException)
                self.signal.serial_error_signal.emit("ERROR NFC PLEASE RESTART PROGRAM")
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def read_nfc_valid(self):
        try:
            nfc_serial_input = self.readline().decode().replace('\r\n', '')
            self.uid, *self.dm = nfc_serial_input.split(',')
            logger.debug(nfc_serial_input)
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            self.uid, self.dm = '', ''
            nfc_serial_input = ''
        return nfc_serial_input

    def start_nfc_write(self, dm=None, process_result=None, unit_count=1):
        self.write_dm, self.unit_count = dm, unit_count
        self.write_msg = ''
        self.current_process_result = process_result
        self.uid = self.dm = ''
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
            while self.read_nfc_valid() != ','.join([self.uid, self.write_dm]):
                logger.debug(self.write_dm)
                self.write(f"{self.write_dm}".encode())
                self.read_nfc_valid()
                # self.read_nfc_valid()
            self.write_dm = None
            self.signal.qr_write_done_signal.emit("WRITE DONE, TRY NEXT QR SCAN", LIGHT_SKY_BLUE)
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            self.signal.serial_error_signal.emit("ERROR NFC PLEASE RESTART PROGRAM")
            # self.signal.qr_write_done_signal.emit("CHECK NFC AND RESTART PROGRAM!!", RED)

    def make_write_nfc(self):
        self.write_msg = self.dm
        merge_previous_process = [f"{key}:{value}" for key, value in self.nfc_previous_process.items()]
        self.write_msg = ','.join([self.dm] + merge_previous_process + [self.current_process_result])
        logger.debug(self.write_msg)
        return self.write_msg

    def nfc_write_thread(self):
        self.flushInput()
        self.flushOutput()
        while self.unit_count:
            try:
                split_data = self.readline().decode().replace('\r\n', '').split(',')
                logger.debug(split_data)
                if not self.is_valid_input(split_data) or self.is_write_done():
                    continue
                self.nfc_previous_process = split_data[2:]
                logger.debug(self.write_msg)
                if self.is_need_to_write() and not self.write_msg:
                    self.write(f"{self.make_write_nfc()}".encode())
                    self.read_nfc_valid()

                if self.check_write_done(split_data[1:]):
                    self.write_done()

            except SerialException as e:
                logger.error(f"{type(e)} : {e}")
                self.signal.serial_error_signal.emit("ERROR NFC PLEASE RESTART PROGRAM")
                self.unit_count = 0
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def check_write_done(self, split_data):
        return self.write_msg == ','.join(split_data)

    def write_done(self):
        self.write_msg = ''
        self.dm_list.append(self.dm)
        self.unit_count -= 1
        self.signal.nfc_write_done_signal.emit(self)

    def check_pre_process(self):
        for (process, result), previous_process in zip(self.nfc_previous_process.items(), self.previous_processes):
            if process != previous_process or result not in PROCESS_OK_RESULTS:
                return False
        return self.is_need_to_write()

    def is_need_to_write(self):
        return len(self.nfc_previous_process) == len(self.previous_processes)

    def is_write_done(self):
        return self.dm in self.dm_list

    def is_valid_pre_process(self, processes):
        if not isinstance(processes, list):
            return False
        try:
            for item in processes:
                p, r = item.split(':')
                if p not in PROCESS_NAMES or r not in PROCESS_RESULTS:
                    raise ValueError
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            return False
        return True

    def is_valid_input_with_message(self, split_data):
        if return_value := self.is_valid_input(split_data):
            return return_value
        self.signal.previous_process_signal.emit(
            (self.serial_name, "NFC TAG is not Normal", RED)
        )
        return return_value

    def is_valid_input(self, split_data):
        self.uid, self.dm, *rest = split_data
        return self.uid and self.dm and self.is_valid_pre_process(rest)

    def is_open_close(self):
        if self.is_open:
            self.close()


if __name__ == '__main__':
    ser = SerialNFC('com10', 115200, timeout=2)
    if ser.is_nfc():
        ser.start_previous_process_check_thread(SENSOR_PREPROCESS)

    while True:
        pass
