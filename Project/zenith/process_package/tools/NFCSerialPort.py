from PySide2.QtCore import QTimer, Signal, Slot

from process_package.check_string import check_nfc_uid, check_dm
from process_package.resource.string import STR_UID, STR_DATA_MATRIX, STR_AIR, STR_MIC, STR_FUN, STR_SEN, STR_NFC, \
    STR_DISCONNECT
from process_package.tools.SerialPort import SerialPort


class NFCSerialPort(SerialPort):
    nfc_out_signal = Signal(dict)
    connection_signal = Signal(bool)

    def __init__(self, name):
        super(NFCSerialPort, self).__init__(name)

        self.check_connection_timer = QTimer()
        self.check_connection_timer.start(1000)
        self.check_connection_timer.timeout.connect(self.check_comport_connection)

        self.line_out_signal.connect(self.line_out)

    def check_comport_connection(self):
        if not self.isOpen() and not self.open():
            self.connection_signal.emit(False)
        else:
            self.connection_signal.emit(bool(self.pinoutSignals() & self.ClearToSendSignal))

    @Slot(str)
    def line_out(self, value):
        if STR_NFC in value:
            self.connection_signal.emit(True)
            return
        if STR_DISCONNECT in value:
            self.connection_signal.emit(False)
            return

        split_data = {}
        for split in value.split(','):
            if check_nfc_uid(split):
                split_data[STR_UID] = split
            if check_dm(split):
                split_data[STR_DATA_MATRIX] = split
            if STR_AIR in split:
                split_data[STR_AIR] = split.split(':')[1]
            if STR_MIC in split:
                split_data[STR_MIC] = split.split(':')[1]
            if STR_FUN in split:
                split_data[STR_FUN] = split.split(':')[1]
            if STR_SEN in split:
                split_data[STR_SEN] = split.split(':')[1]
        if split_data:
            self.nfc_out_signal.emit(split_data)
