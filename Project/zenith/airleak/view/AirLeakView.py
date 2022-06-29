from PySide2.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout, QGridLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import Widget, Label, LabelBlink, LabelNFC
from process_package.component.NFCComponent import NFCComponent
from process_package.component.SerialComboHBoxLayout import SerialComboHBoxLayout
from process_package.resource.color import LIGHT_SKY_BLUE, BLUE
from process_package.resource.number import AIR_LEAK_UNIT_COUNT
from process_package.resource.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, \
    AIR_LEAK_RESULT_MINIMUM_HEIGHT, AIR_LEAK_RESULT_FONT_SIZE, NFC_FIXED_HEIGHT, COMPORT_FIXED_HEIGHT, \
    AIR_LEAK_STATUS_FIXED_HEIGHT
from process_package.resource.string import STR_MACHINE_COMPORT, STR_RESULT, STR_UNIT, STR_AIR_LEAK, STR_NFC


class AirLeakView(Widget):
    def __init__(self, *args):
        super(AirLeakView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(STR_NFC))
        layout.addWidget(comport_box := QGroupBox(STR_MACHINE_COMPORT))
        comport_box.setLayout(comport := SerialComboHBoxLayout(self._model))
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

        nfc.setFixedHeight(NFC_FIXED_HEIGHT)
        comport_box.setFixedHeight(COMPORT_FIXED_HEIGHT)
        result_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
        unit_out_label.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
        result.setMinimumSize(AIR_LEAK_UNIT_MINIMUM_WIDTH, AIR_LEAK_RESULT_MINIMUM_HEIGHT)
        status.setFixedHeight(AIR_LEAK_STATUS_FIXED_HEIGHT)

        self.result = result
        self.status = status

        self.setWindowTitle(f"{STR_AIR_LEAK} v1.11")

        # connect widgets to controller
        comport.comport_save.connect(self._control.comport_save)
        comport.serial_output_data.connect(self._control.input_serial_data)
        self._control.nfc_write.connect(nfc.write)

        # listen for model event signals
        nfc.nfc_data_out.connect(self._control.receive_nfc_data)
        self._model.nfc_changed.connect(nfc.set_port)

        self._model.unit_input_changed.connect(lambda unit_index, text: self.units[unit_index].setText(text))
        self._model.unit_color_changed.connect(
            lambda unit_index: self.units[unit_index].set_background_color(LIGHT_SKY_BLUE))
        self._model.unit_blink_changed.connect(lambda unit_index: self.units[unit_index].set_background_color(BLUE))
        self._model.units_clean.connect(self.unit_clean)

        self._model.result_changed.connect(self.result.setText)
        self._model.result_background_color_changed.connect(self.result.set_background_color)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

    def unit_clean(self):
        for unit in self.units:
            unit.clean()

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))

        if action == db_action:
            MSSqlDialog()
