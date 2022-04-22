from PyQt5.QtWidgets import QApplication, QGroupBox, QLabel, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt
from Config import Config
import sys
from defined_variable import *

MIN = 'min'
MAX = 'max'
ON_OFF = 'on/off'
CALIBRATION = 'calibration'


class ProbeBox(QGroupBox):
    def __init__(self, *args):
        super().__init__()
        title, self.potNum, self.config = args
        self.potName = f"pot{self.potNum}"

        # component
        self.rangeLabel = QLabel()
        self.valueLabel = QLabel("OFF")
        self.valueOnOff = QLabel("")

        self.updateMinMax()
        self.initUI()

    def updateMinMax(self):
        self.min = int(self.config.getValue(self.potName, MIN))
        self.max = int(self.config.getValue(self.potName, MAX))
        self.convertMin = convertValueToStr(self.min)
        self.convertMax = convertValueToStr(self.max)
        self.rangeLabel.setText(f"{self.potName.upper()} {self.convertMin} ~ {self.convertMax}")

    def initUI(self):
        self.rangeLabel.setStyleSheet(f"font-size: 20px")
        self.rangeLabel.setFixedHeight(50)

        self.valueLabel.setAlignment(Qt.AlignCenter)
        self.valueLabel.setStyleSheet(f"font-size: 38px;"
                                      f"font-weight: bold;")

        self.valueOnOff.setAlignment(Qt.AlignCenter)
        self.valueOnOff.setStyleSheet(f"font-size: 38px;"
                                      f"font-weight: bold")
        self.valueOnOff.setFixedWidth(70)

        valueLayout = QHBoxLayout()
        valueLayout.addWidget(self.valueLabel)
        valueLayout.addWidget(self.valueOnOff)

        layout = QVBoxLayout()
        layout.addWidget(self.rangeLabel)
        layout.addLayout(valueLayout)
        self.setLayout(layout)
        self.setStyleSheet("""
                            QGroupBox{border-style: solid;
                            border-width: 2px;
                            border-radius: 20px}
                            """)

    def update_value(self, data):
        self.updateMinMax()
        value = data + int(self.config.getValue(self.potName, CONFIG_CAL))
        if self.config.getValue(self.potName, CONFIG_ON_OFF) == ON:
            valueStr = convertValueToStr(value)
            if self.min < 0 and self.max < 0:
                onf = ('NG', 'OK')[self.max <= value <= self.min]
            else:
                onf = ('NG', 'OK')[self.min <= value <= self.max]
            self.valueLabel.setText(f"{valueStr}G")
            self.valueOnOff.setText(onf)
            # print(self.potName, valueStr, onf)
            self.valueOnOff.setStyleSheet(f"font-size: 38px;"
                                          f"font-weight: bold;"
                                          f"color: {('red', 'blue')[onf == 'OK']}")
        else:
            self.valueLabel.setText("OFF")
            self.valueOnOff.setText('')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProbeBox('', 1, Config('config.ini'))
    sys.exit(app.exec_())
