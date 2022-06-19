from PySide2.QtCore import QObject, Signal

from process_package.resource.string import STR_NFC
from process_package.tools.SerialPort import SerialPort


class ReleaseProcessControl(QObject):
    close_signal = Signal()

    def __init__(self, model):
        super(ReleaseProcessControl, self).__init__()
        self._model = model

        self.nfc = SerialPort(STR_NFC)

        # controller event connect
        self.nfc.line_out_signal.connect(self.input_serial_data)

    def input_serial_data(self):
        pass

    def right_clicked(self):
        self.close_signal.emit()
