from PySide2.QtWidgets import QWidget, QVBoxLayout

from mic.component.MICNFCWriter import NFC_HEIGHT, NFC_FONT_SIZE, MIC_COMPONENT_WIDTH
from process_package.component.NFCComponent import NFCComponent
from process_package.component.PreviousCheckGroupLabel import PreviousCheckerGroupLabel
from process_package.resource.string import STR_PREVIOUS_PROCESS, STR_MIC


class MICNFCReader(QWidget):
    def __init__(self, nfc_name):
        super(MICNFCReader, self).__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(nfc_name))
        layout.addWidget(label := PreviousCheckerGroupLabel(title=STR_PREVIOUS_PROCESS,
                                                            font_size=40,
                                                            is_clean=True,
                                                            clean_time=2000,
                                                            process_name=STR_MIC))
        self.result_label = label
        self.nfc = nfc

        nfc.setFixedHeight(NFC_HEIGHT)
        nfc.label.set_font_size(NFC_FONT_SIZE)
        self.setMinimumWidth(MIC_COMPONENT_WIDTH)
        self.setMinimumHeight(320)
        self.nfc.nfc_data_out.connect(self.result_label.check_previous)

        # listen for model event

    def set_port(self, value):
        self.nfc.set_port(value)
