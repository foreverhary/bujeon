from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout

from process_package.Views.CustomComponent import LabelTimerClean
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.string import STR_DATA_MATRIX, STR_AIR


class MICNFCReader(QWidget):
    def __init__(self, nfc_name):
        super(MICNFCReader, self).__init__()

        self._model = MICNFCReaderModel()
        self._control = MICNFCReaderControl(self._model)

        layout = QVBoxLayout(self)
        layout.addWidget(label := LabelTimerClean(font_size=50, is_clean=True, clean_time=2000))
        self.result_label = label
        nfc = NFCComponent(nfc_name)

        self.setMinimumWidth(420)
        nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event
        self._model.result_display_changed.connect(self.result_label.setText)


class MICNFCReaderModel(QObject):
    result_display_changed = Signal(str)

    def __init__(self):
        super(MICNFCReaderModel, self).__init__()

    @property
    def result_display(self):
        return self._result_display

    @result_display.setter
    def result_display(self, value):
        self._result_display = value
        self.result_display_changed.emit()


class MICNFCReaderControl(QObject):
    def __init__(self, model):
        super(MICNFCReaderControl, self).__init__()
        self._model = model

    def receive_nfc_data(self, value):
        msg = value.get(STR_DATA_MATRIX)
        msg += '\n'
        msg += f"{STR_AIR}:{value.get(STR_AIR)}"
        self._model.result = msg
