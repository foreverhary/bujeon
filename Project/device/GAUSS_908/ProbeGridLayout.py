from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ProbeBox import ProbeBox

PASS_FAIL_TEXT_SIZE = 50


class ProbeGridLayout(QGridLayout):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.probes = list()
        for pot in range(1, 6):
            probe = ProbeBox('aa', pot, self.config)
            self.probes.append(probe)
        self.passFailLabel = QLabel()
        self.passFailLabel.setAlignment(Qt.AlignCenter)
        self.passFailLabel.setStyleSheet(f'font-size: {PASS_FAIL_TEXT_SIZE}px')
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
        self.addWidget(groupbox, 0, 2)
        self.addWidget(self.probes[2], 1, 0)
        self.addWidget(self.probes[3], 1, 1)
        self.addWidget(self.probes[4], 1, 2)

    def setText(self, txt):
        self.passFailLabel.setText(txt)
        self.passFailLabel.setStyleSheet(f"font-size: {PASS_FAIL_TEXT_SIZE}px;"
                                         f"font-weight: bold;"
                                         f"color: {('red', 'blue')[txt == 'PASS']}")

