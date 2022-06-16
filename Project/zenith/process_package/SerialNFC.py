import re
from threading import Thread

from PySide2.QtCore import Signal, QObject
from serial import Serial, SerialException

from process_package.check_string import check_nfc_uid, check_dm
from process_package.defined_variable_function import SENSOR_PREVIOUS_PROCESS, logger, NFC, \
    PROCESS_RESULTS, PROCESS_NAMES, PROCESS_OK_RESULTS


class SerialNFCSignal(QObject):
    previous_process_signal = Signal(object)
    qr_write_done_signal = Signal()
    nfc_write_done_signal = Signal(object)
    serial_error_signal = Signal(str)
    dm_read_done_signal = Signal(object)
    same_dm_signal = Signal(object)
    debug_nfc_signal = Signal(str)


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
        self.debug = False

        # default serial value + name
        self.port, self.baudrate, self.timeout, self.serial_name = port, baudrate, timeout, serial_name
        self.num = 0

        # uid and dm
        self.write_msg = self.uid = self.dm = self.write_dm = ''
        self.check_dm = None
        self.dm_list = []
        self.enable = True

        self.unit_count = 0

        # previous process
        self.nfc_previous_process = self.current_process_result = self.previous_processes = ''

        # dummy Thread
        self.th = Thread(target=self.nfc_qr_write_thread, daemon=True)
        # self.debug_th = Thread(target=self.debug_nfc, daemon=True)
        # self.debug_th.start()

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
                    if process_result in PROCESS_RESULTS:
                        self._nfc_previous_process[process_name] = process_result
            except Exception as e:
                logger.warning(f"{type(e)} : {e}")
                self._nfc_previous_process = {}

    def debug_nfc(self):
        while True:
            while self.debug:
                if line_data := self.read_line_decode():
                    self.signal.debug_nfc_signal.emit(line_data)

    def clean_check_dm(self):
        self.check_dm = ''

    def read_line_decode(self):
        input_serial_data = self.readline().decode().replace('\r', '').replace('\n', '')
        start_index = input_serial_data.find('UID:')
        if start_index != -1:
            return input_serial_data[input_serial_data.find('UID:'):]

    def is_nfc(self):
        return_value = False
        try:
            self.open()
            if (check_string := self.readline().decode().replace('\r\n', '')) and re.search(NFC, check_string):
                logger.debug(check_string)
                self.timeout = None
                self.serial_name = check_string.replace(' ', '').upper()
                self.num = int(self.serial_name[-1])
                return_value = True
            else:
                self.is_open_close()
        except (SerialException, UnicodeDecodeError) as e:
            self.is_open_close()
        return return_value

    def start_read_dm_thread(self):
        self.enable = True
        if not self.th.is_alive():
            self.th = Thread(target=self.read_dm_thread, daemon=True)
            self.th.start()

    def read_dm_thread(self):
        self.close_and_open()
        self.flushInput()
        logger.debug(self.serial_name)
        while self.enable:
            if self.split_uid_dm(self.get_serial_readline_with_decode().split(',')) \
                    and self.dm != self.check_dm:
                self.check_dm = self.dm
                self.enable = False
                self.signal.dm_read_done_signal.emit(self)

    def start_previous_process_check_thread(self):
        self.th = Thread(target=self.previous_process_check_thread, daemon=True)
        self.th.start()

    def previous_process_check_thread(self):
        self.flushInput()
        while True:
            try:
                self.is_close_open()
                line_data = self.read_line_decode()
                if not self.enable or not line_data:
                    continue
                logger.debug(line_data)
                split_data = line_data.split(',')
                self.split_input(split_data)
                if self.uid and not self.dm:
                    self.signal.previous_process_signal.emit(self)
                    continue

                if self.dm == self.check_dm:
                    continue
                self.nfc_previous_process = split_data[2:]
                self.signal.previous_process_signal.emit(self)
                self.check_dm = self.dm
            except (UnicodeDecodeError, ValueError) as e:
                logger.error(f"{type(e)} : {e}")
            except SerialException:
                logger.error(f"{SerialException}:{self.serial_name}")
                self.signal.serial_error_signal.emit("ERROR NFC PLEASE RESTART PROGRAM")
                break
            except Exception as e:
                logger.error(f"{type(e)} : {e}")

    def power_down(self):
        if self.is_open:
            self.write(b'\xff')
            self.close()
            logger.debug(self.serial_name)

    def read_nfc_valid(self):
        try:
            nfc_serial_input = self.readline().decode().replace('\r\n', '')
            logger.debug(nfc_serial_input)
            self.uid, *self.dm = nfc_serial_input.split(',')
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
            self.signal.qr_write_done_signal.emit()
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
                split_data = self.readline().decode().replace('\r\n', '')
                if not split_data:
                    continue
                split_data = split_data.split(',')
                logger.debug(split_data)
                self.split_input(split_data)
                if self.is_write_done():
                    self.signal.same_dm_signal.emit(self)

                self.nfc_previous_process = split_data[2:]
                if self.is_need_to_write() and not self.write_msg:
                    self.write(f"{self.make_write_nfc()}".encode())
                    logger.debug(self.write_msg)
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

    def check_pre_process(self, previous_processes):
        return not any(
            previous_process not in self.nfc_previous_process
            or self.nfc_previous_process[previous_process]
            not in PROCESS_OK_RESULTS
            for previous_process in previous_processes
        )

    def check_pre_process_valid(self, previous_processes):
        return not any(
            previous_process not in self.nfc_previous_process
            or self.nfc_previous_process[previous_process]
            not in PROCESS_RESULTS
            for previous_process in previous_processes
        )

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
        except ValueError:
            return False
        except Exception as e:
            logger.error(f"{type(e)} : {e}")
            return False
        return True

    def split_uid_dm(self, split_data):
        try:
            self.uid, self.dm, *rest = split_data
        except ValueError:
            self.uid = self.dm = ''
        return self.uid and self.dm

    def split_input(self, split_data):
        length = len(split_data)
        if length == 1:
            self.uid = split_data[0]
        elif length == 2:
            self.uid, self.dm = split_data
        else:
            self.uid, self.dm, *self.nfc_previous_process = split_data

        # return self.uid and self.dm and self.is_valid_pre_process(rest)

    def close_and_open(self):
        if self.is_open:
            self.close()
        self.open()

    def is_open_close(self):
        if self.is_open:
            self.close()

    def is_close_open(self):
        if not self.is_open:
            self.open()

    def get_serial_readline_with_decode(self):
        return self.readline().decode().replace('\r', '').replace('\n', '')


if __name__ == '__main__':
    ser = SerialNFC('com10', 115200, timeout=2)
    if ser.is_nfc():
        ser.start_previous_process_check_thread(SENSOR_PREVIOUS_PROCESS)

    while True:
        pass
