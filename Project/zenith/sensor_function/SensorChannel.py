from PySide2.QtCore import QObject
from PySide2.QtWidgets import QGroupBox, QVBoxLayout

from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.Views.CustomComponent import Button, ComboBox, Label, Widget, get_time, LabelTimerClean, LabelNFC
from process_package.resource.string import STR_RESULT, STR_CON_OS, STR_POGO_OS, STR_LED, STR_HALL_IC, STR_VBAT_ID, \
    STR_C_TEST, STR_BATTERY, STR_PROX_TEST, STR_MIC, STR_PCM


class SensorChannel(QGroupBox):
    def __init__(self, title):
        super(SensorChannel, self).__init__()
        self._model = SensorChannelModel()
        self._control = SensorChannelControl(self._model)

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(SerialComboHBoxLayout(self._model, button_text='CONN'))
        layout.addWidget(Label(STR_RESULT))
        layout.addWidget(result := Label())
        layout.addWidget(Label('DM'))
        layout.addWidget(data_matrix := LabelNFC())

        # size & font size
        result.setFixedHeight(350)
        result.set_font_size(100)

        # assign
        self.data_matrix = data_matrix
        self.result = result


class SensorChannelControl(QObject):
    def __init__(self, model):
        super(SensorChannelControl, self).__init__()
        self._model = model


class SensorChannelModel(QObject):
    error_code = {
        STR_CON_OS: 1,
        STR_POGO_OS: 2,
        STR_LED: 3,
        STR_HALL_IC: 10,
        STR_VBAT_ID: 4,
        STR_C_TEST: 5,
        STR_BATTERY: 6,
        STR_PROX_TEST: 8,
        STR_MIC: 7,
        STR_PCM: 9,
    }

    def __init__(self):
        super(SensorChannelModel, self).__init__()
        self.error_code_result = {}

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
        self.result_changed.emit(value)

    def get_error_code(self):
        return ','.join([
            str(self.error_code[key]) for key, value in self.error_code_result.items() if not value
        ])

    def begin(self):
        self.error_code_result = {name: True for name in self.error_code}
