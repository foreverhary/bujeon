from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout

from process_package.Views.CustomComponent import Widget, Label, LabelBlink, LabelNFC
from process_package.Views.CustomMixComponent import GroupLabel, HBoxComboButton
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.number import AIR_LEAK_UNIT_COUNT
from process_package.resource.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, \
    AIR_LEAK_RESULT_MINIMUM_HEIGHT, AIR_LEAK_RESULT_FONT_SIZE, NFC_FIXED_HEIGHT, COMPORT_FIXED_HEIGHT, \
    AIR_LEAK_STATUS_FIXED_HEIGHT, AUDIO_BUS_LABEL_MINIMUM_WIDTH, AUDIO_BUS_PREVIOUS_PROCESS_FIXED_HEIGHT, \
    AUDIO_BUS_NFC_FIXED_HEIGHT, AUDIO_BUS_NFC_FONT_SIZE
from process_package.resource.string import STR_NFC1, STR_MACHINE_COMPORT, STR_RESULT, STR_UNIT, STR_AIR_LEAK, \
    STR_NFCIN, STR_NFC2, STR_PREVIOUS_PROCESS, STR_GRADE, STR_STATUS, STR_WRITE_STATUS, STR_FUNCTION


class FunctionView(Widget):
    def __init__(self, *args):
        super(FunctionView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(nfc_layout := QHBoxLayout())
        nfc_layout.addWidget(nfc_in := GroupLabel(STR_NFCIN))
        nfc_layout.addWidget(nfc1 := GroupLabel(STR_NFC1))
        nfc_layout.addWidget(nfc2 := GroupLabel(STR_NFC2))
        layout.addWidget(previous_process := GroupLabel(STR_PREVIOUS_PROCESS, is_clean=True))
        layout.addWidget(grade := GroupLabel(STR_GRADE))
        layout.addWidget(nfc := GroupLabel(STR_WRITE_STATUS))
        layout.addWidget(status := GroupLabel(STR_STATUS))

        status.label.setMinimumWidth(AUDIO_BUS_LABEL_MINIMUM_WIDTH)
        nfc_in.setFixedHeight(AUDIO_BUS_NFC_FIXED_HEIGHT)
        nfc_in.label.set_font_size(AUDIO_BUS_NFC_FONT_SIZE)
        nfc1.setFixedHeight(AUDIO_BUS_NFC_FIXED_HEIGHT)
        nfc1.label.set_font_size(AUDIO_BUS_NFC_FONT_SIZE)
        nfc2.setFixedHeight(AUDIO_BUS_NFC_FIXED_HEIGHT)
        nfc2.label.set_font_size(AUDIO_BUS_NFC_FONT_SIZE)
        previous_process.setFixedHeight(AUDIO_BUS_PREVIOUS_PROCESS_FIXED_HEIGHT)
        status.setFixedHeight(AIR_LEAK_STATUS_FIXED_HEIGHT)

        self.nfc_in_connection = nfc_in.label
        self.nfc1_connection = nfc1.label
        self.nfc2_connection = nfc2.label
        self.previous_process = previous_process.label
        self.grade = grade.label
        self.nfc = nfc.label
        self.status = status.label

        self.setWindowTitle(STR_FUNCTION)

        # connect widgets to controller

        # listen for model event signals
        self._model.nfc_in.nfc_changed.connect(self._control.nfc_in.setPortName)
        self._model.nfc_in.nfc_changed.connect(self.nfc_in_connection.setText)
        self._model.nfc_in.nfc_connection_changed.connect(self.nfc_in_connection.set_background_color)

        self._model.nfc1.nfc_changed.connect(self._control.nfc1.setPortName)
        self._model.nfc1.nfc_changed.connect(self.nfc1_connection.setText)
        self._model.nfc1.nfc_connection_changed.connect(self.nfc1_connection.set_background_color)

        self._model.nfc2.nfc_changed.connect(self._control.nfc2.setPortName)
        self._model.nfc2.nfc_changed.connect(self.nfc2_connection.setText)
        self._model.nfc2.nfc_connection_changed.connect(self.nfc2_connection.set_background_color)

        self._model.grade_changed.connect(self.grade.setText)
        self._model.grade_color_changed.connect(self.grade.set_color)

        self._model.nfc_input_changed.connect(self.nfc.setText)
        self._model.nfc_color_changed.connect(self.nfc.set_background_color)

        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)
