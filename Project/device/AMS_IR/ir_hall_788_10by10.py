import sys

from PySide2.QtCore import Slot
from PySide2.QtGui import Qt
from PySide2.QtSerialPort import QSerialPortInfo
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QDesktopWidget, QApplication, QVBoxLayout, QHBoxLayout, \
    QLabel

from package.logger import logger
from package.serial_arduino import SerialArduinoButton

IR_OPEN_MIN = 140
IR_OPEN_MAX = 4500
IR_DIFF_MIN = 600
IR_DIFF_MAX = 4000
HALL_MIN = -4000
HALL_MAX = 4000

AVERAGE_COUNT = 10


class ArrayDisplay(QWidget):
    def __init__(self):
        super(ArrayDisplay, self).__init__()
        layout = QVBoxLayout(self)
        layout.addLayout(serial_layout := QHBoxLayout())

        serials = [
            SerialArduinoButton(f"/dev/{port.portName()}" if 'ttyUSB' in port.portName() else port.portName(), 115200)
            for index, port in enumerate(QSerialPortInfo.availablePorts())
            if not port.isBusy() and ('ttyUSB' in port.portName() or 'COM' in port.portName())]
        for serial in serials:
            serial.out_data.connect(self.read_data)
            serial_layout.addWidget(serial)

        layout.addLayout(grid_array := QGridLayout())
        self.buttons = [Button() for _ in range(100)]
        for index, button in enumerate(self.buttons):
            grid_array.addWidget(button, (index // 10) + 1, (index % 10) + 1)
            button.setFixedSize(70, 70)
        for index in range(10):
            grid_array.addWidget(label := QLabel(f"{index + 1}"), 0, index + 1)
            label.setAlignment(Qt.AlignCenter)
            grid_array.addWidget(label := QLabel(f"{index + 1}"), index + 1, 0)
            label.setAlignment(Qt.AlignCenter)

        self.setWindowTitle('10X10')
        self.show()

        # center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.switch = 0
        self.l_count = 0
        self.r_count = 0

    @Slot(str)
    def read_data(self, input_serial_data):
        if input_serial_data in ['1', '0']:
            self.switch = int(input_serial_data)
            logger.debug(self.switch)
            return
        split_data = input_serial_data.split(',')

        if 'L' in split_data[0]:
            self.l_count += 1
            button_index = int(split_data[0][1:]) - 1
            if self.l_count > 50:
                self.l_count = 0
                self.sender().toggle_background_color()
        else:
            self.r_count += 1
            button_index = int(split_data[0][1:]) + 49
            if self.r_count > 50:
                self.r_count = 0
                self.sender().toggle_background_color()
        self.buttons[button_index].input_value(split_data[1], self.switch)


ERROR_VALUE = 65535


class Button(QPushButton):

    def __init__(self):
        super(Button, self).__init__()
        self._ir_open = []
        self._ir_close = []
        self._hall = []

    def set_background_color(self, color):
        self.setStyleSheet(f"background-color: {color}")

    def input_value(self, value, switch):
        if switch:
            self.ir_close, self.hall = list(map(int, value.split(':')))
            diff = self.ir_close - self.ir_open
            self.setText(f"O:{self.ir_open}\n"
                         f"D:{diff}\n"
                         f"H:{self.hall}")
            if IR_DIFF_MIN < diff < IR_DIFF_MAX and HALL_MIN < self.hall < HALL_MAX:
                self.set_background_color('green')
            else:
                self.set_background_color('red')
        else:
            self.ir_open, self.hall = list(map(int, value.split(':')))
            if IR_OPEN_MIN < self.ir_open < IR_OPEN_MAX and HALL_MIN < self.hall < HALL_MAX:
                self.set_background_color('lightskyblue')
                self.setText(f"O:{self.ir_open}\nH:{self.hall}")
            else:
                self.setText('')
                self.set_background_color('red')

    @property
    def hall(self):
        if len(self._hall) > AVERAGE_COUNT:
            self._hall = self._hall[:AVERAGE_COUNT]
            return sum(self._hall) // len(self._hall)
        else:
            return self._hall[0]

    @hall.setter
    def hall(self, value):
        self._hall.insert(0, value)

    @property
    def ir_open(self):
        if len(self._ir_open) >= AVERAGE_COUNT:
            self._ir_open = self._ir_open[:AVERAGE_COUNT]
            if ERROR_VALUE in self._ir_open:
                return ERROR_VALUE
            else:
                return sum(self._ir_open) // len(self._ir_open)
        else:
            return ERROR_VALUE

    @ir_open.setter
    def ir_open(self, value):
        if value == ERROR_VALUE or (IR_OPEN_MIN < value < IR_OPEN_MAX):
            self._ir_open.insert(0, value)

    @property
    def ir_close(self):
        if len(self._ir_close) > AVERAGE_COUNT:
            self._ir_close = self._ir_close[:AVERAGE_COUNT]
            return sum(self._ir_close) // len(self._ir_close)
        else:
            return self._ir_close[0]

    @ir_close.setter
    def ir_close(self, value):
        self._ir_close.insert(0, value)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArrayDisplay()
    sys.exit(app.exec_())
