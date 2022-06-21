from PySide2.QtCore import Qt, Signal, QTimer, Slot
from PySide2.QtWidgets import QDialog, QGridLayout, QGroupBox, QVBoxLayout, QHBoxLayout

from process_package.Views.CustomComponent import LineEdit, Label, Button
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.string import STR_UID, STR_DATA_MATRIX, STR_AIR, STR_MIC, STR_FUN, STR_SEN


class NFCCheckerDialog(QDialog):
    def __init__(self, control, nfc):
        super(NFCCheckerDialog, self).__init__()
        self._parent_control = control
        layout = QGridLayout(self)
        layout.addWidget(nfc_box := NFCBox(nfc))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.showModel()

    def closeEvent(self, e):
        self._parent_control.checker_on = False

    def showModel(self):
        super().exec_()


class NFCBox(QGroupBox):
    nfc_write = Signal(str)

    def __init__(self, nfc):
        super(NFCBox, self).__init__(f"{nfc.get_nfc_name()}({nfc.get_port()})")
        layout = QVBoxLayout(self)
        layout.addWidget(input_group_box := QGroupBox('OUT'))
        input_group_box.setLayout(output_layout := QHBoxLayout())
        output_layout.addWidget(id_edit := LineEdit())
        output_layout.addWidget(result_label := Label(font_size=15))
        output_layout.addWidget(button := Button('WRITE'))
        layout.addWidget(in_label := GroupLabel("IN"))
        in_label.label.setFixedSize(650, 140)

        self.id_edit = id_edit
        self.result_label = result_label
        self.in_label = in_label.label

        self.id_edit.setText("BT6001000")
        self.result_label.setText("AIR:OK,MIC:OK,FUN:B,SEN:OK")

        button.clicked.connect(lambda: self.nfc_write.emit(f"{self.id_edit.text()},"
                                                           f"{self.result_label.text()}"))
        self.nfc_write.connect(nfc.write)

        self.remove_timer = QTimer(self)
        self.remove_timer.start(300)
        self.remove_timer.timeout.connect(self.in_label.clear)

        nfc.nfc_data_out.connect(self.input_text)

    @Slot(dict)
    def input_text(self, input_msg):
        if not input_msg:
            return
        self.remove_timer.stop()
        self.remove_timer.start(300)
        msg = input_msg.get(STR_UID)
        if data_matrix := input_msg.get(STR_DATA_MATRIX):
            msg += '\n' + data_matrix
        if STR_AIR in input_msg or STR_MIC in input_msg or STR_FUN in input_msg or STR_SEN in input_msg:
            msg += '\n'
        if air := input_msg.get(STR_AIR) :
            msg += f"{STR_AIR}:{air} "
        if mic := input_msg.get(STR_MIC) :
            msg += f"{STR_MIC}:{mic} "
        if fun := input_msg.get(STR_FUN) :
            msg += f"{STR_FUN}:{fun} "
        if sen := input_msg.get(STR_SEN) :
            msg += f"{STR_SEN}:{sen} "
        self.in_label.setText(msg)
