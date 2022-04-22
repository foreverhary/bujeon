from PyQt5.QtWidgets import QGroupBox, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from ProbeBox import ProbeBox

PASS_FAIL_TEXT_SIZE = 80
POT_COUNT = 4


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
        self.pass_fail_groupbox = QGroupBox()
        self.pass_fail_groupbox.setStyleSheet("""
                                QGroupBox{border-style: solid;
                                border-width: 2px;
                                border-radius: 20px}
                                """)
        layout = QVBoxLayout()
        layout.addWidget(self.passFailLabel)
        self.pass_fail_groupbox.setLayout(layout)

        for index, probe in enumerate(self.probes):
            self.addWidget(probe, index // 2, index % 2)
        self.addWidget(self.pass_fail_groupbox, 0, 2, 0, 1)
        # self.addWidget(groupbox, 0, 2)

    def pass_fail_color(self, color):
        if color == 'blue':
            self.pass_fail_groupbox.setStyleSheet("""
                                    QGroupBox{border-style: solid;
                                    border-width: 2px;
                                    border-radius: 20px};
                                    background-color: blue
                                    """)

        else:
            self.pass_fail_groupbox.setStyleSheet("""
                                    QGroupBox{border-style: solid;
                                    border-width: 2px;
                                    border-radius: 20px};
                                    background-color: red
                                    """)
