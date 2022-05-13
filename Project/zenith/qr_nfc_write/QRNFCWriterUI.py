from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox

from process_package.PyQtCustomComponent import Label, RightAlignLabel, ComboBox
from process_package.defined_serial_port import ports


class QRNFCWriterUI(QWidget):
    """
    등록 공정 UI
    """

    def __init__(self):
        super(QRNFCWriterUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(preprocess_box := QGroupBox("PREPROCESS RESULT"))
        preprocess_box.setLayout(preprocess_layout := QVBoxLayout())
        preprocess_layout.addWidget(preprocess := Label())

        layout.addWidget(dm_box := QGroupBox("DATA MATRIX"))
        dm_box.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm := Label())

        layout.addWidget(status_box := QGroupBox("NFC STATUS"))
        status_box.setLayout(status_layout := QVBoxLayout())
        status_layout.addWidget(status := Label())

        self.preprocess_label = preprocess
        self.dm_label = dm
        self.dm_label.setMinimumWidth(500)
        self.dm_label.set_text_property(size=60)
        self.status_label = status
        self.dm_label.set_text_property(size=50)

        self.setWindowTitle('DM Registration')

        self.setLayout(layout)
