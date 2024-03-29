import socket

from PySide2.QtCore import QObject, Signal
from PySide2.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout

from process_package.check_string import nfc_dict_to_list
from process_package.component.CustomComponent import get_time, LabelTimerClean, LabelNFC
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.models.BasicModel import BasicModel
from process_package.resource.color import LIGHT_SKY_BLUE, RED
from process_package.resource.string import STR_NFC, STR_DATA_MATRIX, STR_MIC, STR_SPL, STR_THD, STR_IMP, STR_F0, \
    STR_R_AND_B, STR_POLARITY, STR_CURRENT, STR_SNR, STR_NOISE_LEVEL, \
    STR_FRF, STR_OK, STR_NFC1, STR_NG, STR_PROCESS_RESULTS
from process_package.tools.CommonFunction import logger, is_result_in_nfc, get_write_result_in_nfc

NFC_HEIGHT = 60
NFC_FONT_SIZE = 15
MIC_COMPONENT_WIDTH = 420


class MICNFCWriter(QWidget):

    def __init__(self, nfc_name, mssql):
        super(MICNFCWriter, self).__init__()

        self._model = MICNFCWriterModel()
        self._control = MICNFCWriterControl(self._model, mssql)

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(nfc_name))
        layout.addWidget(result := GroupLabel('CH1' if nfc_name == STR_NFC1 else 'CH2',
                                              label=LabelTimerClean(is_clean=True, clean_time=5000)))
        layout.addLayout(nfc_layout := QHBoxLayout())
        nfc_layout.addWidget(nfc_status := GroupLabel(title=STR_NFC,
                                                      label=LabelNFC(is_clean=True, clean_time=4000)))

        # size
        nfc.setMaximumHeight(NFC_HEIGHT)
        nfc.label.set_font_size(NFC_FONT_SIZE)
        result.setMinimumSize(MIC_COMPONENT_WIDTH, 150)
        nfc_status.setMaximumHeight(NFC_HEIGHT)
        nfc_status.set_font_size(NFC_FONT_SIZE)

        self.nfc = nfc
        self.result = result.label
        self.nfc_status = nfc_status.label

        # NFC Signal
        self._control.nfc_write.connect(nfc.write)
        self._control.nfc_write_bytes.connect(nfc.write)
        nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event signals
        self._model.result_changed.connect(self.result.setText)
        self._model.result_clean.connect(self.result.clean)
        self._model.result_color_changed.connect(self.result.set_background_color)

        self._model.nfc_status_changed.connect(self.nfc_status.setText)
        self._model.nfc_status_clean.connect(self.nfc_status.clean)
        self._model.nfc_status_color_changed.connect(self.nfc_status.set_background_color)

    def set_port(self, value):
        self.nfc.set_port(value)

    def set_result(self, value):
        logger.debug(value)
        if value == STR_OK:
            self.result.set_background_color(LIGHT_SKY_BLUE)
        else:
            self.result.set_background_color(RED)
        self._model.result = value

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

    def close_force(self):
        self.nfc.close_force()


class MICNFCWriterControl(QObject):
    nfc_write = Signal(str)
    nfc_write_bytes = Signal(bytes)

    def __init__(self, model, mssql):
        super(MICNFCWriterControl, self).__init__()
        self._model = model
        self._mssql = mssql

        self.delay_write_count = 0
        self.process_name = STR_MIC

    def receive_nfc_data(self, value):
        if self.delay_write_count:
            self.delay_write_count -= 1
            return
        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return
        if not self._model.result:
            return
        machine_result_bit = 1 if self._model.result == STR_OK else 0

        if not (results_byte := value.get(STR_PROCESS_RESULTS)) \
                or not is_result_in_nfc(self, results_byte, machine_result_bit):
            msg = data_matrix.encode() + b','
            msg += get_write_result_in_nfc(self, results_byte, machine_result_bit)
            self.nfc_write_bytes.emit(msg)
            self._model.data_matrix = data_matrix
            self.delay_write_count = 1
        else:
            self._model.nfc_status = {
                STR_DATA_MATRIX: data_matrix,
                self.process_name: self._model.result
            }
            self.sql_update(data_matrix)
            self._model.result = ''

    def sql_update(self, data_matrix):
        self._mssql.start_query_thread(self._mssql.insert_pprd,
                                       data_matrix,
                                       get_time(),
                                       self._model.result,
                                       STR_MIC,
                                       self._model.get_error_code(),
                                       socket.gethostbyname(socket.gethostname())
                                       )


class MICNFCWriterModel(BasicModel):
    result_changed = Signal(str)
    result_clean = Signal()
    result_color_changed = Signal(str)
    nfc_status_changed = Signal(str)
    nfc_status_clean = Signal()
    nfc_status_color_changed = Signal(str)

    error_code = {
        STR_SPL: 1,
        STR_THD: 2,
        STR_IMP: 3,
        STR_F0: 4,
        STR_R_AND_B: 5,
        STR_POLARITY: 6,
        STR_CURRENT: 7,
        STR_SNR: 8,
        STR_NOISE_LEVEL: 9,
        STR_FRF: 10
    }

    def __init__(self):
        super(MICNFCWriterModel, self).__init__()
        self.init_error_code()
        self.data_matrix = None
        self.result = None
        self.nfc_status = None

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        if value:
            self.display_result = value

    @property
    def display_result(self):
        return self._display_result

    @display_result.setter
    def display_result(self, value):
        self._display_result = value
        if value:
            self.result_changed.emit(value)
        else:
            self.result_clean.emit()

    @property
    def nfc_status(self):
        return self._nfc_status

    @nfc_status.setter
    def nfc_status(self, value):
        self._nfc_status = value
        if not value:
            self.nfc_status_clean.emit()
            return
        color = LIGHT_SKY_BLUE
        for k, v in value.items():
            if k != STR_DATA_MATRIX and v == STR_NG:
                color = RED

        self.nfc_status_changed.emit(','.join(nfc_dict_to_list(value)))
        self.nfc_status_color = color

    @property
    def nfc_status_color(self):
        return self._nfc_status_color

    @nfc_status_color.setter
    def nfc_status_color(self, value):
        self._nfc_status_color = value
        self.nfc_status_color_changed.emit(value)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def init_error_code(self):
        self.error_code_result = {name: True for name in self.error_code}
