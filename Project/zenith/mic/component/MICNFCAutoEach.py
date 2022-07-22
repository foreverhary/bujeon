from PySide2.QtCore import Signal
from PySide2.QtWidgets import QVBoxLayout, QWidget

from mic.component.MICNFCWriter import MICNFCWriterControl, MICNFCWriterModel
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.string import STR_DATA_MATRIX, STR_RESULT, STR_OK, STR_FRF, STR_SPL, STR_CURRENT
from process_package.tools.CommonFunction import logger


class MICNFCAutoEach(QWidget):
    def __init__(self, nfc_name, mssql):
        super(MICNFCAutoEach, self).__init__()

        self._model = MICNFCAutoEachModel()
        self._control = MICNFCAutoEachControl(self._model, mssql)

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(nfc_name))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX))
        layout.addWidget(result := GroupLabel(STR_RESULT))

        # Size
        nfc.setMaximumHeight(80)
        data_matrix.setMinimumWidth(300)
        data_matrix.setMaximumHeight(100)
        result.setMinimumHeight(500)

        # asign
        self.nfc = nfc
        self.data_matrix = data_matrix.label
        self.result = result.label

        # NFC Signal
        self._control.nfc_write.connect(self.nfc.write)
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event signals
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.result_changed.connect(self.result.setText)
        self._model.result_clean.connect(self.result.clean)
        self._model.result_color_changed.connect(self.result.set_background_color)

    def set_port(self, value):
        self.nfc.set_port(value)

    def set_result(self, value):
        if value == STR_OK:
            self.result.set_background_color(LIGHT_SKY_BLUE)
        else:
            self.result.set_background_color(RED)
        self._model.result = value
        self._control.sql_update(self._model.data_matrix)

    def set_error_code(self, value):
        logger.debug(value)
        self._model.init_error_code()
        for k, v in value.items():
            if STR_FRF in k:
                self._model.error_code_result[STR_FRF] = v
            if 'SENS' in k:
                self._model.error_code_result[STR_SPL] = v
            if STR_CURRENT in k:
                self._model.error_code_result[STR_CURRENT] = v


class MICNFCAutoEachControl(MICNFCWriterControl):
    def __init__(self, model, mssql):
        super(MICNFCAutoEachControl, self).__init__(model, mssql)

    def receive_nfc_data(self, value):
        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self._model.data_matrix == data_matrix:
            return

        self._model.data_matrix = data_matrix
        self._model.result = ''


class MICNFCAutoEachModel(MICNFCWriterModel):
    data_matrix_changed = Signal(str)

    def __init__(self):
        super(MICNFCAutoEachModel, self).__init__()

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(value)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        if value:
            self.result_changed.emit(value)
        else:
            self.result_clean.emit()

