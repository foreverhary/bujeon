from PySide2.QtCore import QObject, Signal, Slot

from process_package.resource.string import STR_NFC, STR_DATA_MATRIX, PROCESS_OK_RESULTS, PROCESS_NAMES, STR_FUN, \
    STR_MISS, PROCESS_FULL_NAMES, STR_NG
from process_package.tools.CommonFunction import logger, read_beep
from process_package.tools.NFCSerialPort import NFCSerialPort
from process_package.tools.SerialPort import SerialPort


class ReleaseProcessControl(QObject):
    close_signal = Signal()

    def __init__(self, model):
        super(ReleaseProcessControl, self).__init__()
        self._model = model

        self.nfc = NFCSerialPort(STR_NFC)

        # controller event connect
        self.nfc.nfc_out_signal.connect(self.receive_nfc_data)
        self.nfc.connection_signal.connect(self.receive_nfc_connection)

    @Slot(bool)
    def receive_nfc_connection(self, connection):
        self._model.nfc_connection = connection

    @Slot(str)
    def receive_nfc_data(self, value):
        read_beep()

        if data_matrix := value.get(STR_DATA_MATRIX):
            self._model.data_matrix = data_matrix
            self.display_result(value)

    def display_result(self, value):
        msg = ''
        if self.check_previous_process(value):
            msg += value.get(STR_FUN)
        else:
            for process in PROCESS_NAMES:
                if not (result := value.get(process)):
                    result = STR_MISS
                if result not in PROCESS_OK_RESULTS:
                    if msg:
                        msg += '\n'
                    msg += f"{PROCESS_FULL_NAMES[process]} : {result}"
        self._model.result = msg or STR_NG

    def check_previous_process(self, value):
        return not any(
            previous_process not in value
            or value.get(previous_process)
            not in PROCESS_OK_RESULTS
            for previous_process in PROCESS_NAMES
        )

    def right_clicked(self):
        self.close_signal.emit()
