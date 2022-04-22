from PyQt5.QtWidgets import QVBoxLayout, QFrame, QLabel, QLineEdit, QHBoxLayout, QGridLayout
from PyQt5.QtCore import Qt
from MenuButton import Button
from defined_variable import *
import pyautogui

pyautogui.FAILSAFE = False


class MinMaxFrame(QFrame):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.init_ui()

    def init_ui(self):
        self.potTitle = QLabel()
        self.potTitle.setFixedHeight(80)
        self.potTitle.setAlignment(Qt.AlignCenter)
        self.potTitle.setStyleSheet('font-size: 80px')
        self.minmaxLabel = QLabel()
        self.minmaxLabel.setFixedWidth(230)
        self.minmaxLabel.setStyleSheet('font-size: 90px')
        self.minmaxValue = QLineEdit()
        self.minmaxValue.setReadOnly(True)
        self.minmaxValue.setFixedHeight(130)
        self.minmaxValue.setStyleSheet('font-size: 130px')

        layout = QVBoxLayout()
        valueline_layout = QHBoxLayout()
        valueline_layout.addWidget(self.minmaxLabel)
        valueline_layout.addWidget(self.minmaxValue)
        buttonlayout = QGridLayout()
        self.buttonN = Button('N', 40)
        self.buttonS = Button('S', 40)
        self.buttonN.clicked.connect(self.buttonClicked)
        self.buttonS.clicked.connect(self.buttonClicked)
        self.buttonNum = list()
        for index in range(10):
            button = Button(str(index), 40)
            button.clicked.connect(self.buttonClicked)
            self.buttonNum.append(button)
        self.buttonCLR = Button('CLR', 40)
        self.buttonCLR.clicked.connect(self.buttonClicked)
        self.buttonEXT = Button('EXT', 40)

        buttonlayout.addWidget(self.buttonN, 0, 0)
        buttonlayout.addWidget(self.buttonS, 1, 0)

        buttonlayout.addWidget(self.buttonNum[0], 1, 5)
        buttonlayout.addWidget(self.buttonNum[1], 0, 1)
        buttonlayout.addWidget(self.buttonNum[2], 0, 2)
        buttonlayout.addWidget(self.buttonNum[3], 0, 3)
        buttonlayout.addWidget(self.buttonNum[4], 0, 4)
        buttonlayout.addWidget(self.buttonNum[5], 0, 5)
        buttonlayout.addWidget(self.buttonNum[6], 1, 1)
        buttonlayout.addWidget(self.buttonNum[7], 1, 2)
        buttonlayout.addWidget(self.buttonNum[8], 1, 3)
        buttonlayout.addWidget(self.buttonNum[9], 1, 4)

        buttonlayout.addWidget(self.buttonCLR, 0, 6)
        buttonlayout.addWidget(self.buttonEXT, 1, 6)

        layout.addWidget(self.potTitle)
        layout.addLayout(valueline_layout)
        layout.addLayout(buttonlayout)
        self.setLayout(layout)

    def setpotnum(self, pot_num, minmax):
        self.pot_num, self.minmax = pot_num, minmax
        self.pot_name = make_pot_name(self.pot_num)
        self.potTitle.setText(self.pot_name.upper())
        self.minmaxLabel.setText(self.minmax.upper() + ':')
        self.minmaxValue.setText(convertValueToStr(
            self.config.getValue(self.pot_name, (CONFIG_MIN, CONFIG_MAX)['max' in self.minmax.lower()])))

    def buttonClicked(self):
        button = self.sender()
        buttonText = button.text()
        valueText = self.minmaxValue.text()
        if buttonText == 'CLR':
            valueText = ''
        elif buttonText == 'N' or buttonText == 'S':
            if len(valueText) == 0:
                valueText += buttonText
        else:
            if len(valueText):
                valueText += buttonText
        self.minmaxValue.setText(valueText)
