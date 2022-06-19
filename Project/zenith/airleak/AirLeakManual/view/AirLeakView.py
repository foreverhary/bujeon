from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout

from process_package.Views.CustomComponent import Widget, Label, LabelBlink, LabelNFC
from process_package.Views.CustomMixComponent import GroupLabel, HBoxComboButton
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.number import AIR_LEAK_UNIT_COUNT
from process_package.resource.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, \
    AIR_LEAK_RESULT_MINIMUM_HEIGHT, AIR_LEAK_RESULT_FONT_SIZE, NFC_FIXED_HEIGHT, COMPORT_FIXED_HEIGHT, \
    AIR_LEAK_STATUS_FIXED_HEIGHT
from process_package.resource.string import STR_NFC1, STR_MACHINE_COMPORT, STR_RESULT, STR_UNIT, STR_AIR_LEAK


class AirLeakView(Widget):
    def __init__(self, *args):
        super(AirLeakView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc1 := GroupLabel(STR_NFC1))
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := HBoxComboButton(STR_AIR_LEAK))
        layout.addLayout(unit_layout := QHBoxLayout())
        unit_layout.addWidget(out_group := QGroupBox("OUT"))
        out_group.setLayout(out_grid := QGridLayout())
        out_grid.addWidget(result_label := Label(STR_RESULT), 0, 0)
        out_grid.addWidget(result := Label(font_size=AIR_LEAK_RESULT_FONT_SIZE), 1, 0, AIR_LEAK_UNIT_COUNT + 1, 1)

        out_grid.addWidget(unit_out_label := Label(STR_UNIT), 0, 1)
        self.units = []
        for index in range(AIR_LEAK_UNIT_COUNT):
            out_grid.addWidget(label := LabelNFC(font_size=AIR_LEAK_UNIT_FONT_SIZE), index + 1, 1)
            self.units.append(label)

        layout.addWidget(status := LabelBlink())

        nfc1.setFixedHeight(NFC_FIXED_HEIGHT)
        comport_box.setFixedHeight(COMPORT_FIXED_HEIGHT)
        result_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
        unit_out_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
        result.setMinimumSize(AIR_LEAK_UNIT_MINIMUM_WIDTH, AIR_LEAK_RESULT_MINIMUM_HEIGHT)
        status.setFixedHeight(AIR_LEAK_STATUS_FIXED_HEIGHT)

        self.nfc1_connection = nfc1.label
        self.comport = comport
        self.result = result
        self.status = status

        self.setWindowTitle(STR_AIR_LEAK)

        # connect widgets to controller
        self.comport.comport.currentIndexChanged.connect(self._control.change_comport)
        self.comport.button.clicked.connect(self._control.comport_clicked)

        # listen for model event signals
        self._model.comport_changed.connect(self.comport.comport.setCurrentText)
        self._model.comport_open_changed.connect(self.comport.serial_connection)
        self._model.available_comport_changed.connect(self.comport.fill_combobox)

        self._model.nfc_changed.connect(self._control.nfc.setPortName)
        self._model.nfc_changed.connect(self.nfc1_connection.setText)
        self._model.nfc_connection_changed.connect(self.nfc1_connection.set_background_color)

        self._model.unit_input_changed.connect(lambda unit_index, text: self.units[unit_index].setText(text))
        self._model.unit_color_changed.connect(
            lambda unit_index: self.units[unit_index].set_background_color(LIGHT_SKY_BLUE))
        self._model.unit_blink_changed.connect(lambda unit_index: self.units[unit_index].blink_text())

        self._model.result_changed.connect(self.result.setText)
        self._model.result_background_color_changed.connect(self.result.set_background_color)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)
