from PySide2.QtCore import Qt, Signal, Slot, QTimer
from PySide2.QtWidgets import QDialog, QGridLayout, QGroupBox, QVBoxLayout, QHBoxLayout, QComboBox

from process_package.component.CustomComponent import Button, Label, LineEdit
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.string import STR_UID, STR_DATA_MATRIX, STR_GRADE, STR_A, STR_B, STR_C


class NFCBoxGradeChecker(QGroupBox):
    nfc_write = Signal(str)

    def __init__(self, nfc):
        super(NFCBoxGradeChecker, self).__init__(f"{nfc.get_nfc_name()}({nfc.get_port()})")
        layout = QVBoxLayout(self)
        layout.addWidget(input_group_box := QGroupBox('OUT'))
        input_group_box.setLayout(output_layout := QHBoxLayout())
        output_layout.addWidget(data_matrix := LineEdit())
        output_layout.addWidget(grade_combobox := QComboBox())
        output_layout.addWidget(button := Button('WRITE'))
        layout.addWidget(in_label := GroupLabel("IN"))
        data_matrix.setMaximumWidth(250)
        in_label.label.setFixedSize(650, 140)

        grade_combobox.addItems([STR_A, STR_B, STR_C])

        self.data_matrix = data_matrix
        self.grade_combobox = grade_combobox
        self.in_label = in_label.label

        self.data_matrix.setText("BT6001000")

        button.clicked.connect(lambda: self.nfc_write.emit(f"{self.data_matrix.text()},"
                                                           f"{self.grade_combobox.currentText()}"))
        self.nfc_write.connect(nfc.write)

        self.remove_timer = QTimer(self)
        self.remove_timer.start(300)
        self.remove_timer.timeout.connect(self.in_label.clear)

        nfc.nfc_data_out_to_checker.connect(self.input_text)

    @Slot(dict)
    def input_text(self, input_msg):
        if not input_msg:
            return
        self.remove_timer.stop()
        self.remove_timer.start(300)
        msg = input_msg.get(STR_UID)
        if data_matrix := input_msg.get(STR_DATA_MATRIX):
            msg += '\n' + data_matrix
        if grade := input_msg.get(STR_GRADE):
            msg += f"\n{STR_GRADE} : {grade}"
        self.in_label.setText(msg)


class NFCCheckerGradeChecker(QDialog):
    def __init__(self, nfc):
        super(NFCCheckerGradeChecker, self).__init__()
        self.nfc = nfc
        layout = QVBoxLayout(self)
        layout.addWidget(nfc_box := NFCBoxGradeChecker(nfc))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.showModal()

    def closeEvent(self, e):
        self.nfc.checker_on = False

    def showModal(self):
        super().exec_()


class NFCComponentGradeChecker(NFCComponent):
    def __init__(self, title=''):
        super(NFCComponentGradeChecker, self).__init__(title)

    def open_checker(self):
        self.checker_on = True
        NFCCheckerGradeChecker(self)
