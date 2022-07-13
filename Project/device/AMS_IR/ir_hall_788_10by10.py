import sys

from PySide2.QtCore import Slot
from PySide2.QtGui import Qt
from PySide2.QtSerialPort import QSerialPortInfo
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QDesktopWidget, QApplication, QVBoxLayout, QHBoxLayout, \
    QLabel

from package.logger import logger
from package.serial_arduino import SerialArduinoButton

IR_OPEN_MIN = 2500
IR_OPEN_MAX = 7000
IR_DIFF_MIN = 600
IR_DIFF_MAX = 4000
HALL_MIN = -120
HALL_MAX = 120


class ArrayDisplay(QWidget):
    def __init__(self):
        super(ArrayDisplay, self).__init__()
        layout = QVBoxLayout(self)
        layout.addLayout(serial_layout := QHBoxLayout())

        serials = [
            SerialArduinoButton(f"/dev/{port.portName()}" if 'ttyUSB' in port.portName() else port.portName(), 115200)
            for index, port in enumerate(QSerialPortInfo.availablePorts())
            if not port.isBusy() and ('ttyUSB' in port.portName() or 'COM' in port.portName()) and index < 3]
        for serial in serials:
            serial.out_data.connect(self.read_data)
            serial_layout.addWidget(serial)

        layout.addLayout(grid_array := QGridLayout())
        self.buttons = [Button() for _ in range(100)]
        for index, button in enumerate(self.buttons):
            grid_array.addWidget(button, (index // 10) + 1, (index % 10) + 1)
            button.setFixedSize(70, 70)
        for index in range(10):
            grid_array.addWidget(label := QLabel(f"{index+1}"), 0, index + 1)
            label.setAlignment(Qt.AlignCenter)
            grid_array.addWidget(label := QLabel(f"{index+1}"), index + 1, 0)
            label.setAlignment(Qt.AlignCenter)

        self.setWindowTitle('10X10')
        self.show()

        # center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        self.switch = 0

    @Slot(str)
    def read_data(self, input_serial_data):
        if input_serial_data in ['1', '0']:
            self.switch = int(input_serial_data)
            logger.debug(self.switch)
            return
        split_data = input_serial_data.split(',')
        if len(split_data) != 51:
            return

        buttons = self.buttons[:50] if split_data[0] == 'L' else self.buttons[50:]
        for value, button in zip(split_data[1:], buttons):
            if self.switch:
                button.ir_close = value
            else:
                button.ir_open = value


class Button(QPushButton):

    def __init__(self):
        super(Button, self).__init__()

    def set_background_color(self, color):
        self.setStyleSheet(f"background-color: {color}")

    @property
    def hall(self):
        return self._hall

    @hall.setter
    def hall(self, value):
        self._hall = value

    @property
    def ir_open(self):
        return self._ir_open

    @ir_open.setter
    def ir_open(self, value):
        self._ir_open, self.hall = list(map(int, value.split(':')))
        self.setText(f"O:{self._ir_open}\nH:{self.hall}")
        if IR_OPEN_MIN < self._ir_open < IR_OPEN_MAX and HALL_MIN < self.hall < HALL_MAX:
            self.set_background_color('lightskyblue')
        else:
            self.set_background_color('red')

    @property
    def ir_close(self):
        return self._ir_close

    @ir_close.setter
    def ir_close(self, value):
        self._ir_close, self.hall = list(map(int, value.split(':')))
        self.diff_value = self._ir_close - self.ir_open

    @property
    def diff_value(self):
        return self._diff_value

    @diff_value.setter
    def diff_value(self, value):
        self._diff_value = value
        self.setText(f"O:{self.ir_open}\n"
                     f"D:{self._diff_value}\n"
                     f"H:{self.hall}")
        if IR_DIFF_MIN < value < IR_DIFF_MAX and HALL_MIN < self.hall < HALL_MAX:
            self.set_background_color('green')
        else:
            self.set_background_color('red')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArrayDisplay()
    sys.exit(app.exec_())
