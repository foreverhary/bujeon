from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QMenu

from function.FunctionConfig import FunctionConfig
from process_package.component.CustomComponent import Widget
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.PreviousCheckGroupLabel import PreviousCheckerGroupLabelWithNGScreen
from process_package.resource.size import AIR_LEAK_STATUS_FIXED_HEIGHT, AUDIO_BUS_LABEL_MINIMUM_WIDTH, \
    AUDIO_BUS_PREVIOUS_PROCESS_FIXED_HEIGHT, \
    AUDIO_BUS_NFC_FIXED_HEIGHT, AUDIO_BUS_NFC_FONT_SIZE
from process_package.resource.string import STR_NFC1, STR_NFCIN, STR_NFC2, STR_PREVIOUS_PROCESS, STR_GRADE, STR_STATUS, \
    STR_WRITE_STATUS, STR_FUNCTION, STR_FUN


class FunctionView(Widget):
    def __init__(self, *args):
        super(FunctionView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(nfc_layout := QHBoxLayout())
        nfc_layout.addWidget(nfc_in := NFCComponent(STR_NFCIN))
        nfc_layout.addWidget(nfc1 := NFCComponent(STR_NFC1))
        nfc_layout.addWidget(nfc2 := NFCComponent(STR_NFC2))
        layout.addWidget(previous_process := PreviousCheckerGroupLabelWithNGScreen(STR_PREVIOUS_PROCESS,
                                                                                   is_clean=True,
                                                                                   clean_time=3000,
                                                                                   process_name=STR_FUN))
        layout.addWidget(grade := GroupLabel(STR_GRADE))
        layout.addWidget(nfc := GroupLabel(STR_WRITE_STATUS, is_nfc=True))
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

        self.previous_process = previous_process.label
        self.grade = grade.label
        self.nfc = nfc.label
        self.status = status.label

        # connect widgets to controller

        # listen for component event signals
        nfc_in.nfc_data_out.connect(previous_process.check_previous)
        # nfc_in.nfc_data_out.connect(self._control.check_previous)
        nfc1.nfc_data_out.connect(self._control.receive_nfc_data)
        nfc2.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for control event signals
        self._control.nfc_in_write.connect(nfc_in.write)
        self._control.nfc1_write.connect(nfc1.write)
        self._control.nfc2_write.connect(nfc2.write)

        # listen for model event signals
        self._model.nfc_in.nfc_changed.connect(nfc_in.set_port)
        self._model.nfc1.nfc_changed.connect(nfc1.set_port)
        self._model.nfc2.nfc_changed.connect(nfc2.set_port)

        self._model.previous_changed.connect(self.previous_process.setText)
        self._model.previous_color_changed.connect(self.previous_process.set_background_color)

        self._model.grade_changed.connect(self.grade.setText)
        self._model.grade_color_changed.connect(self.grade.set_color)

        self._model.nfc_input_changed.connect(self.nfc.setText)
        self._model.nfc_color_changed.connect(self.nfc.set_background_color)

        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        file_action = menu.addAction('Function File Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == file_action:
            FunctionConfig(self._model, self._control)
        if action == db_action:
            MSSqlDialog()
