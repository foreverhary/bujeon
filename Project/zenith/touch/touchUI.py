from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox

from process_package.PyQtCustomComponent import Label, RightAlignLabel, ComboBox
from process_package.defined_serial_port import ports


class TouchUI(QWidget):
    def __init__(self):
        super(TouchUI, self).__init__()

        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(order_box := QGroupBox("ORDER NUMBER"))
        order_box.setLayout(order_layout := QVBoxLayout())
        order_layout.addWidget(order := Label(''))

        layout.addWidget(dm_box := QGroupBox("DATA MATRIX"))
        dm_box.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm := Label(''))

        layout.addWidget(machine_box := QGroupBox("MACHINE RESULT"))
        machine_box.setLayout(machine_layout := QVBoxLayout())
        machine_layout.addWidget(machine := Label(''))

        layout.addWidget(status_box := QGroupBox("STATUS"))
        status_box.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status := Label(''))

        self.order_label = order
        self.dm_label = dm
        self.machine_label = machine
        self.status_label = status
        self.dm_label.setMinimumWidth(500)
        self.dm_label.set_text_property(size=60)

        self.setWindowTitle('Touch Process')