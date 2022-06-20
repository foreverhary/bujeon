from PySide2.QtCore import Qt, Signal, QTimer, Slot
from PySide2.QtWidgets import QDialog, QGridLayout, QGroupBox, QVBoxLayout, QHBoxLayout

from process_package.Views.CustomComponent import LineEdit, Label, Button
from process_package.Views.CustomMixComponent import GroupLabel


class NFCCheckerDialog(QDialog):
    def __init__(self, control, nfc_list):
        super(NFCCheckerDialog, self).__init__()
        self._parent_control = control
        layout = QGridLayout(self)
        for index, (port, nfc) in enumerate(nfc_list.items()):
            layout.addWidget(nfc_box := NFCBox(), index // 2, index % 2)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def showModel(self):
        super().exec_()


class NFCBox(QGroupBox):
    nfc_write = Signal(str)

    def __init__(self, read_signal, port, name):
        super(NFCBox, self).__init__(f"{name}({port})")
        self.read_signal = read_signal
        layout = QVBoxLayout(self)
        self.addWidget(input_group_box := QGroupBox('OUT'))
        input_group_box.setLayout(output_layout := QHBoxLayout())
        output_layout.addWidget(id_edit := LineEdit())
        output_layout.addWidget(result_label := Label(font_size=15))
        output_layout.addWidget(button := Button('WRITE'))
        layout.addWidget(in_label := GroupLabel("IN"))
        in_label.label.setFixedSize(650, 140)

        self.id_edit = id_edit
        self.result_label = result_label
        self.in_label = in_label.label

        button.clicked.connect(lambda: self.nfc_write.emit(f"{self.id_edit.text()},"
                                                           f"{self.result_label.text()}"))

        self.remove_timer = QTimer(self)
        self.remove_timer.start(300)
        self.remove_timer.timeout.connect(self.in_label.clear)

        self.read_signal.connect(self.input_text)

    @Slot(str)
    def input_text(self, input_msg):
        if input_msg:
            split_data = input_msg.split(',')
            length = len(split_data)
            if length == 1:
                msg = input_msg
            elif length == 2:
                msg = '\n'.join(split_data)
            else:
                msg = split_data[0] + '\n' + split_data[1] + '\n' + ','.join(split_data[2:])
            self.label_nfc_enable.setText(msg)
