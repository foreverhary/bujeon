from PyQt5.QtWidgets import QWidget, QGridLayout

from process_package.PyQtCustomComponent import Label, RightAlignLabel, ComboBox
from process_package.defined_serial_port import ports


class QRNFCWriterUI(QWidget):
    def __init__(self):
        super(QRNFCWriterUI, self).__init__()
        self.comport_list = ComboBox()
        self.comport_list.addItems(ports)
        self.order_label = Label('')
        self.dm_label = Label('')
        self.dm_label.setMinimumWidth(500)
        self.dm_label.set_text_property(size=60)
        self.status_label = Label('')
        self.dm_label.set_text_property(size=50)

        layout = QGridLayout()

        raw = 0

        layout.addWidget(RightAlignLabel('ORDER :'), raw, 0)
        layout.addWidget(self.order_label, raw, 1)
        raw += 1
        layout.addWidget(RightAlignLabel('DM :'), raw, 0)
        layout.addWidget(self.dm_label, raw, 1)
        raw += 1
        layout.addWidget(self.status_label, raw, 0, -1, 2)

        self.setWindowTitle('DM Registration')

        self.setLayout(layout)

