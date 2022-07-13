import sys

from PySide2.QtCore import Slot
from PySide2.QtSerialPort import QSerialPortInfo
from PySide2.QtWidgets import QWidget, QGridLayout, QPushButton, QDesktopWidget, QApplication, QVBoxLayout, QHBoxLayout

from package.serial_arduino import SerialArduinoButton


class ArrayDisplay(QWidget):
    def __init__(self):
        super(ArrayDisplay, self).__init__()
        layout = QVBoxLayout(self)
        layout.addLayout(serial_layout := QHBoxLayout())

        serials = [SerialArduinoButton(f"/dev/{port.portName()}" if 'ttyUSB' in port.portName() else port.portName(), 115200)
                   for port in QSerialPortInfo.availablePorts()
                   if not port.isBusy() and ('ttyUSB' in port.portName() or 'COM' in port.portName())]
        for serial in serials:
            serial.out_data.connect(self.read_data)
            serial_layout.addWidget(serial)

        layout.addLayout(grid_array := QGridLayout())
        self.buttons = [Button() for _ in range(100)]
        for index, button in enumerate(self.buttons):
            grid_array.addWidget(button, index // 10, index % 10)
            button.setFixedSize(70, 70)

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
            return
        split_data = input_serial_data.split(',')
        if len(split_data) != 51:
            return

        buttons = self.buttons[:50] if split_data[0] == 'L' else self.buttons[50:]
        for value, button in zip(split_data[1:], buttons):
            if self.switch:
                button.close_value = int(value)
            else:
                button.open_value = int(value)


class Button(QPushButton):

    def __init__(self):
        super(Button, self).__init__()

    def set_background_color(self, color):
        self.setStyleSheet(f"background-color: {color}")

    @property
    def open_value(self):
        return self._value

    @open_value.setter
    def open_value(self, value):
        self._value = value
        self.setText(str(value))
        if 120 < value < 3500:
            self.set_background_color('lightskyblue')
        else:
            self.set_background_color('red')

    @property
    def close_value(self):
        return self._close_value

    @close_value.setter
    def close_value(self, value):
        self._close_Value = value
        self.diff_value = value - self.open_value

    @property
    def diff_value(self):
        return self._diff_value

    @diff_value.setter
    def diff_value(self, value):
        self._diff_value = value
        self.setText(f"O:{str(self.open_value)}\n"
                     f"D:{str(value)}")
        if 600 < value < 4000:
            self.set_background_color('green')
        else:
            self.set_background_color('red')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ArrayDisplay()
    sys.exit(app.exec_())
