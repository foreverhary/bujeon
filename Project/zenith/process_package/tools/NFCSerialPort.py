from PySide2.QtCore import QTimer, Signal, Slot

from process_package.check_string import check_nfc_uid, check_dm
from process_package.resource.string import STR_UID, STR_DATA_MATRIX, STR_DISCONNECT, PROCESS_RESULTS, STR_C, STR_A, \
    STR_B, STR_GRADE, STR_PROCESS_RESULTS
from process_package.tools.SerialPort import SerialPort


class NFCSerialPort(SerialPort):
    nfc_out_signal = Signal(dict)
    connection_signal = Signal(bool)

    def is_nfc_connect(self):
        return self.is_open & self.nfc_connection

    def __init__(self):
        super(NFCSerialPort, self).__init__()
        self.baudrate = 115200

        self.check_connection_timer = QTimer()
        self.check_connection_timer.start(1000)
        self.check_connection_timer.timeout.connect(self.check_comport_connection)

        self.line_out_signal.connect(self.line_out)
        self.line_out_without_decode_signal.connect(self.line_out_none_decode)

        self.nfc_connection = False
        self.nfc_connection_state = False

    def check_comport_connection(self):
        if not self.is_open and self.port:
            try:
                self.open()
            except Exception as e:
                pass
        if self.nfc_connection_state != self.is_open and self.nfc_connection and self._serial.dtr:
            self.nfc_connection_state = self.is_open and self.nfc_connection and self._serial.dtr
            self.connection_signal.emit(self.nfc_connection_state)

    @Slot(str)
    def line_out(self, value):
        if STR_DISCONNECT in value.upper():
            self.nfc_connection = False
            return

        if value:
            self.nfc_connection = True

        split_data = {}
        splits = value.split(',')
        while splits:
            split = splits.pop(0)
            if check_nfc_uid(split):
                split_data[STR_UID] = split
            elif check_dm(split):
                split_data[STR_DATA_MATRIX] = split
            else:
                if split in [STR_A, STR_B, STR_C]:
                    split_data[STR_GRADE] = split
                    continue
                result = split.split(':')
                if len(result) != 2:
                    continue
                if result[1] not in PROCESS_RESULTS:
                    continue
                split_data[result[0]] = result[1]
        if split_data:
            self.nfc_out_signal.emit(split_data)

    @Slot(bytes)
    def line_out_none_decode(self, value):
        split_data = {}
        splits = value.split(b',')
        try:
            if uid := check_nfc_uid(splits[0].decode()):
                split_data[STR_UID] = uid
            if data_matrix := check_dm(splits[1].decode()):
                split_data[STR_DATA_MATRIX] = data_matrix
            if splits[2][0] & 1 << 7:
                split_data[STR_PROCESS_RESULTS] = splits[2][0]
            if chr(splits[2][1]) in [STR_A, STR_B, STR_C]:
                split_data[STR_GRADE] = chr(splits[2][1])
        except IndexError:
            pass
        if split_data:
            self.nfc_out_signal.emit(split_data)
