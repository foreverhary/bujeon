from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QHBoxLayout
from PyQt5.QtCore import Qt
from MenuButton import Button
from defined_variable import *
import pyautogui

pyautogui.FAILSAFE = False


class CalFrame(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.potNum = 1
        self.calValue = 0
        self.init_ui()

    def init_ui(self):
        self.potTitle = QLabel(f"POT {self.potNum}")
        self.potTitle.setFixedHeight(80)
        self.potTitle.setAlignment(Qt.AlignCenter)
        self.potTitle.setStyleSheet('font-size: 80px')
        cal_label = QLabel('CAL: ')
        cal_label.setFixedWidth(200)
        cal_label.setStyleSheet('font-size: 90px')
        self.valueLine = QLabel()
        # self.valueLine.setReadOnly(True)
        self.valueLine.setFixedHeight(130)
        self.valueLine.setStyleSheet('font-size: 130px')

        self.upbutton = Button('▲', 50)
        self.downbutton = Button('▼', 50)
        # self.upbutton = Button('up', 50)
        # self.downbutton = Button('down', 50)
        self.okbutton = Button('EXT', 50)

        layout = QVBoxLayout()
        value_layout = QHBoxLayout()
        button_layout = QHBoxLayout()

        value_layout.addWidget(cal_label)
        value_layout.addWidget(self.valueLine)
        button_layout.addWidget(self.upbutton)
        button_layout.addWidget(self.downbutton)
        button_layout.addWidget(self.okbutton)

        self.upbutton.clicked.connect(self.up_clicked)
        self.downbutton.clicked.connect(self.down_clicked)

        layout.addWidget(self.potTitle)
        layout.addLayout(value_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def setpotnum(self, potNum):
        self.potNum = potNum
        self.potName = make_pot_name(self.potNum)
        self.calValue = int(self.config.getValue(self.potName, CONFIG_CAL))
        self.potTitle.setText(f"POT {self.potNum}")

    def update_cal_value(self, values):
        value = values[self.potNum - 1]
        value += self.calValue
        valueStr = convertValueToStr(value)
        self.valueLine.setText(f"{valueStr}G")

    def up_clicked(self):
        pyautogui.moveTo(2000, 2000)
        self.calValue += 1

    def down_clicked(self):
        pyautogui.moveTo(2000, 2000)
        self.calValue -= 1

