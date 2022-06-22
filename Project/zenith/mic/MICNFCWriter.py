from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QVBoxLayout, QWidget

from process_package.Views.CustomMixComponent import GroupLabel, GroupLabelNumber
from process_package.check_string import nfc_dict_to_str, nfc_dict_to_list
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.string import STR_PREVIOUS_PROCESS, STR_RESULT, STR_NFC, STR_OK, STR_DATA_MATRIX, STR_AIR, \
    STR_MIC, STR_FUN, STR_SEN
from process_package.tools.CommonFunction import logger


class MICNFCWriter(QWidget):
    def __init__(self, nfc_name):
        super(MICNFCWriter, self).__init__()

        self._model = MICNFCWriterModel()
        self._control = MICNFCWriterControl(self._model)

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(nfc_name))
        layout.addWidget(reader := GroupLabelNumber(title=STR_PREVIOUS_PROCESS, count=2))
        layout.addWidget(result := GroupLabel(STR_RESULT))
        layout.addWidget(writer := GroupLabelNumber(title=STR_NFC, count=3))

        # size
        nfc.setFixedHeight(80)

        self.nfc = nfc
        self.reader = reader
        self.result = result.label
        self.writer = writer

        # NFC Signal
        self._control.nfc_write.connect(nfc.write)
        nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event signals
        self._model.reader_changed.connect(self.reader.setText)
        self._model.result_changed.connect(self.result.setText)
        self._model.writer_changed.connect(self.writer.setText)

    def set_port(self, value):
        self.nfc.set_port(value)

    def mouseMoveEvent(self, e):
        super().mouseMoveEvent(e)
        logger.debug(self.nfc.size())
        logger.debug(self.reader.size())
        logger.debug(self.result.size())
        logger.debug(self.writer.size())


class MICNFCWriterControl(QObject):
    nfc_write = Signal(str)

    def __init__(self, model):
        super(MICNFCWriterControl, self).__init__()
        self._model = model

        self.delay_write_count = 0

    def receive_nfc_data(self, value):

        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not self._model.result:
            self._model.reader = nfc_dict_to_list(value)
            return

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self._model.result != value.get(STR_MIC):
            writer = data_matrix
            if result := value.get(STR_AIR):
                writer += f",{STR_AIR}:{result}"
            writer += f",{STR_MIC}:{self._model.result}"
            self.nfc_write.emit(writer)
            self.delay_write_count = 2
        else:
            self._model.writer = nfc_dict_to_list(value)


class MICNFCWriterModel(QObject):
    reader_changed = Signal(list)

    result_changed = Signal(str)
    result_color_changed = Signal(str)
    writer_changed = Signal(list)

    def __init__(self):
        super(MICNFCWriterModel, self).__init__()
        self.reader = None
        self.result = 'OK'
        self.writer = None

    @property
    def reader(self):
        return self._previous

    @reader.setter
    def reader(self, value):
        self._previous = value
        self.reader_changed.emit(value)
        self.result = ''

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        self.result_changed.emit(value)

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, value):
        self._writer = value
        self.writer_changed.emit(value)
