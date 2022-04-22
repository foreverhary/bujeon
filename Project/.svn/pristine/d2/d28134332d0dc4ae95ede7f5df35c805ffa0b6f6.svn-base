from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ProbeBox import ProbeBox

PASS_FAIL_TEXT_SIZE = 50
POT_COUNT = 2

class ProbeGridLayout(QGridLayout):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.probes = [ProbeBox('aa', index, self.config) for index in range(1, POT_COUNT + 1)]
        self.passFailLabel = QLabel('PASS')
        self.passFailLabel.setAlignment(Qt.AlignCenter)
        self.passFailLabel.setStyleSheet(f'font-size: {PASS_FAIL_TEXT_SIZE}px;'
                                         f'font-weight: bold')
        self.init_ui()

    def init_ui(self):
        groupbox = QGroupBox()
        groupbox.setStyleSheet("""
                                QGroupBox{border-style: solid;
                                border-width: 2px;
                                border-radius: 20px}
                                """)
        layout = QVBoxLayout()
        layout.addWidget(self.passFailLabel)
        groupbox.setLayout(layout)

        self.addWidget(self.probes[0], 0, 0)
        self.addWidget(self.probes[1], 0, 1)
        # self.addWidget(groupbox, 0, 2)
