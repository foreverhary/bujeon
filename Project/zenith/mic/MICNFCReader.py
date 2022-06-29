from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QWidget, QVBoxLayout

from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.string import STR_DATA_MATRIX, STR_AIR, STR_NG, STR_PREVIOUS_PROCESS


class MICNFCReader(QWidget):
    def __init__(self, nfc_name):
        super(MICNFCReader, self).__init__()

        self._model = MICNFCReaderModel()
        self._control = MICNFCReaderControl(self._model)

        layout = QVBoxLayout(self)
        layout.addWidget(label := GroupLabel(title=STR_PREVIOUS_PROCESS, font_size=50, is_clean=True, clean_time=2000))
        # layout.addWidget(label := LabelTimerClean(font_size=50, is_clean=True, clean_time=2000))
        self.result_label = label.label
        self.nfc = NFCComponent(nfc_name)

        self.setMinimumWidth(420)
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event
        self._model.result_changed.connect(self.result_label.setText)
        self._model.result_color_changed.connect(self.result_label.set_background_color)

    def set_port(self, value):
        self.nfc.set_port(value)


class MICNFCReaderModel(QObject):
    result_changed = Signal(str)
    result_color_changed = Signal(str)

    def __init__(self):
        super(MICNFCReaderModel, self).__init__()

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)

    @property
    def result_color(self):
        return self._result_color

    @result_color.setter
    def result_color(self, value):
        self._result_color = value
        self.result_color_changed.emit(value)


class MICNFCReaderControl(QObject):
    def __init__(self, model):
        super(MICNFCReaderControl, self).__init__()
        self._model = model

    def receive_nfc_data(self, value):
        color = LIGHT_SKY_BLUE
        msg = value.get(STR_DATA_MATRIX)
        msg += '\n'
        if air := value.get(STR_AIR):
            msg += f"{STR_AIR}:{air}"
            if air == STR_NG:
                color = RED
        else:
            color = RED
        self._model.result = msg
        self._model.result_color = color
