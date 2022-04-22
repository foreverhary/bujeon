import serial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import QCoreApplication, Qt, QFile, pyqtSignal
from Config import Config
from ProbeGridLayout import ProbeGridLayout
from clickable import clickable
from PotMenu import PotMenu
from CalFrame import CalFrame
from MinMaxFrame import MinMaxFrame
from common.common import logger
from defined_variable import *
import qdarkstyle
import sys
from serial import Serial
import platform
from threading import Lock, Timer, Thread
import pyautogui

pyautogui.FAILSAFE = False

lock = Lock()

POT_COUNT = 2


class Main(QWidget):
    value_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.config = Config('config.ini') if 'Window' in platform.platform() else Config(CONFIG_FILE_NAME)
        self.ser = Serial()
        self.ser.port = 'com9' if 'Window' in platform.platform() else '/dev/ttyUSB0'
        self.ser.baudrate = 115200
        try:
            self.ser.open()
        except Exception as e:
            logger.error(e)
            sys.exit()
        self.init_ui()
        self.eventConnecter()
        self._pot_values = [0 for _ in range(5)]
        # self.serialThread = Timer(0.5, self.serialRead)
        self.serialThread = Thread(target=self.serial_read, daemon=True)
        self.serialThread.start()

    @property
    def pot_values(self):
        return self._pot_values

    @pot_values.setter
    def pot_values(self, values):
        self._pot_values = values
        if len(self._pot_values) == POT_COUNT:
            self.update_probe_value_display()

    def received_value_signal(self, value):
        self.pot_values = value

    def update_probe_value_display(self):
        for index, item in enumerate(self.probeGridLayout.probes):
            item.update_value(self.pot_values[index])
        pass_fail = True
        for item in self.probeGridLayout.probes:
            if 'NG' in item.valueOnOff.text():
                pass_fail = False

        # self.probeGridLayout.passFailLabel.setText(('FAIL', 'PASS')[pass_fail])

        # cal frame
        self.calFrame.update_cal_value(self.pot_values)

    def init_ui(self):
        self.probeGridLayout = ProbeGridLayout(self.config)
        layout = QVBoxLayout()
        self.probeFrame = QFrame()
        self.probeFrame.setLayout(self.probeGridLayout)
        layout.addWidget(self.probeFrame)

        self.potMenuFrame = PotMenu(self.config)
        self.potMenuFrame.setVisible(False)
        layout.addWidget(self.potMenuFrame)

        self.calFrame = CalFrame(self.config)
        self.calFrame.setVisible(False)
        layout.addWidget(self.calFrame)

        self.minmaxFrame = MinMaxFrame(self.config)
        self.minmaxFrame.setVisible(False)
        layout.addWidget(self.minmaxFrame)

        # self.setCursor(Qt.BlankCursor)

        self.setLayout(layout)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def eventConnecter(self):
        clickable(self.probeGridLayout.probes[0]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[0].potNum))
        clickable(self.probeGridLayout.probes[1]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[1].potNum))

        for button in self.potMenuFrame.button:
            button.clicked.connect(self.menu_clicked)

        self.calFrame.okbutton.clicked.connect(self.calOkClicked)

        self.minmaxFrame.buttonEXT.clicked.connect(self.minmaxExtClicked)
        self.value_signal.connect(self.received_value_signal)

    def serial_read(self):
        if not self.ser.isOpen():
            self.ser.open()
        while True:
            try:
                # pot_values = list(map(float, self.ser.readline().decode().split(",")))
                # if len(pot_values) != POT_COUNT:
                pot_values = list(map(float, self.ser.readline().decode().split(",")))
                self.value_signal.emit(list(map(int, pot_values)))
                # self.ser.flushInput()
            except serial.SerialException as e:
                logger.error(e)
                QCoreApplication.instance().quit()
                break
            except Exception as e:
                logger.error(type(e))

    def probe_clicked(self, pot_num):
        self.potMenuFrame.setPotNumber(pot_num)
        self.updateDisplay(MENU_PAGE)

    def disable_display(self):
        pyautogui.moveTo(2000, 2000)
        self.probeFrame.setVisible(False)
        self.potMenuFrame.setVisible(False)
        self.calFrame.setVisible(False)
        self.minmaxFrame.setVisible(False)

    def updateDisplay(self, page):
        self.disable_display()
        if page == MAIN_PAGE:
            self.probeFrame.setVisible(True)
        elif page == MENU_PAGE:
            self.potMenuFrame.updateValue()
            self.potMenuFrame.setVisible(True)
        elif page == CAL_PAGE:
            self.calFrame.setVisible(True)
        elif page == MINMAX_PAGE:
            self.minmaxFrame.setVisible(True)

    def menu_clicked(self):
        button = self.sender()
        button_text = button.text()
        pot_num = self.potMenuFrame.pot_num
        pot_name = f"pot{pot_num}"
        if BUTTON_POT in button_text:
            self.config.setValue(pot_name, CONFIG_ON_OFF,
                                 (OFF, ON)[self.config.getValue(pot_name, CONFIG_ON_OFF) == OFF])
            button.setText(pot_name.upper() + f" [{self.config.getValue(pot_name, CONFIG_ON_OFF).upper()}]")
        elif BUTTON_CAL in button_text:
            self.calFrame.setpotnum(pot_num)
            self.updateDisplay(CAL_PAGE)
        elif BUTTON_MIN in button_text:
            self.minmaxFrame.setpotnum(pot_num, 'MIN')
            self.updateDisplay(MINMAX_PAGE)
        elif BUTTON_MAX in button_text:
            self.minmaxFrame.setpotnum(pot_num, 'MAX')
            self.updateDisplay(MINMAX_PAGE)
        elif BUTTON_EXIT in button_text:
            self.updateDisplay(MAIN_PAGE)

    def calOkClicked(self):
        self.config.setValue(self.calFrame.potName, CONFIG_CAL, self.calFrame.calValue)
        self.updateDisplay(MENU_PAGE)

    def minmaxExtClicked(self):
        if value := self.minmaxFrame.minmaxValue.text():
            value = convertStrToValue(value)
            self.config.setValue(self.minmaxFrame.pot_name,
                                 (CONFIG_MIN, CONFIG_MAX)[self.minmaxFrame.minmax.lower() == CONFIG_MAX],
                                 value)
            self.updateDisplay(MENU_PAGE)


def load_stylesheet(res):
    rc = QFile(res)
    rc.open(QFile.ReadOnly)
    return str(rc.readAll().data(), 'utf-8')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Main()
    dark_stylesheet = qdarkstyle.load_stylesheet_pyqt5()
    app.setStyleSheet(dark_stylesheet)
    # app.setStyleSheet(load_stylesheet('./qdark.css'))
    # qtmodern.styles.dark(app)
    # mw = qtmodern.windows.ModernWindow(ex)
    # mw.showFullScreen()
    sys.exit(app.exec_())
