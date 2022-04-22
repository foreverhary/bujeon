from PyQt5.QtWidgets import QVBoxLayout, QFrame, QSizePolicy
from MenuButton import Button
from defined_variable import *


class PotMenu(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.pot_num = 0
        self.button = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        for menu in BUTTON_MENU:
            button = Button(menu)
            button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            button.setStyleSheet('font-size: 50px')
            self.button.append(button)
            layout.addWidget(button)
        self.setLayout(layout)

    def setPotNumber(self, pot_num):
        self.pot_num = pot_num
        self.pot_name = f"pot{pot_num}"
        self.button[0].setText(f"{BUTTON_POT}{pot_num} [{self.config.getValue(self.pot_name, CONFIG_ON_OFF).upper()}]")
        self.button[1].setText(f"{BUTTON_CAL} [{self.config.getValue(self.pot_name, CONFIG_CAL)}]")
        self.button[2].setText(f"{BUTTON_MIN} [{convertValueToStr(int(self.config.getValue(self.pot_name, CONFIG_MIN)))}]")
        self.button[3].setText(f"{BUTTON_MAX} [{convertValueToStr(int(self.config.getValue(self.pot_name, CONFIG_MAX)))}]")

    def updateValue(self):
        self.setPotNumber(self.pot_num)
