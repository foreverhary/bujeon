import serial
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from PyQt5.QtCore import QCoreApplication, Qt, QFile, pyqtSignal
from Config import Config
from ProbeGridLayout import ProbeGridLayout
from clickable import clickable
from PotMenu import PotMenu
from CalFrame import CalFrame
from MinMaxFrame import MinMaxFrame
from defined_variable import *
import qdarkstyle
import sys
from serial import Serial
import platform
from threading import Lock, Timer
import pyautogui

pyautogui.FAILSAFE = False

lock = Lock()


class Main(QWidget):
    pot_value_update_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.config = Config(CONFIG_FILE_NAME)
        self.ser = Serial()
        self.ser.port = 'com5' if 'Window' in platform.platform() else '/dev/ttyACM0'
        self.ser.baudrate = 115200
        try:
            self.ser.open()
        except Exception as e:
            print(e)
            sys.exit()
        self.init_ui()
        self.eventConnecter()
        self._pot_values = [0 for _ in range(5)]
        self.pot_value_update_signal.connect(self.pot_value_update)
        self.makeTimer()

    @property
    def pot_values(self):
        return self._pot_values

    @pot_values.setter
    def pot_values(self, values):
        self._pot_values = values
        if len(self._pot_values) == 5:
            self.update_probe_value_display()

    def pot_value_update(self, pot_values):
        self.pot_values = pot_values

    def update_probe_value_display(self):
        for index, item in enumerate(self.probeGridLayout.probes):
            item.update_value(self.pot_values[index])
        pass_fail = True
        for item in self.probeGridLayout.probes:
            if 'NG' in item.valueOnOff.text():
                pass_fail = False
        self.probeGridLayout.setText(('FAIL', 'PASS')[pass_fail])

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

        self.setCursor(Qt.BlankCursor)

        self.setLayout(layout)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.showFullScreen()

    def makeTimer(self):
        self.serialThread = Timer(0.2, self.serialRead)
        self.serialThread.start()

    def eventConnecter(self):
        clickable(self.probeGridLayout.probes[0]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[0].potNum))
        clickable(self.probeGridLayout.probes[1]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[1].potNum))
        clickable(self.probeGridLayout.probes[2]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[2].potNum))
        clickable(self.probeGridLayout.probes[3]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[3].potNum))
        clickable(self.probeGridLayout.probes[4]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[4].potNum))

        for button in self.potMenuFrame.button:
            button.clicked.connect(self.menu_clicked)

        self.calFrame.okbutton.clicked.connect(self.calOkClicked)

        self.minmaxFrame.buttonEXT.clicked.connect(self.minmaxExtClicked)

    def serialRead(self):
        try:
            if not self.ser.isOpen():
                self.ser.open()
            # pot_values = list(map(int, map(float, self.ser.readline().decode().split(","))))
            self.ser.readline()
            pot_values = list(map(int, map(float, self.ser.readline().decode().split(","))))

            self.pot_value_update_signal.emit(
                [pot_values[3], pot_values[1], pot_values[4], pot_values[2], pot_values[0]])
            self.ser.flushInput()
            self.makeTimer()
            # self.probeFrame.setVisible(False)
            # self.probeFrame.setVisible(True)
        except serial.SerialException as e:
            print(e)
            QCoreApplication.instance().quit()
        except Exception as e:
            print(e)
            self.makeTimer()

    def serial_close(self):
        try:
            self.serialThread.cancel()
        except Exception as e:
            print(e)

    def probe_clicked(self, pot_num):
        self.serial_close()
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
            self.makeTimer()
            self.probeFrame.setVisible(True)
        elif page == MENU_PAGE:
            self.serial_close()
            self.potMenuFrame.updateValue()
            self.potMenuFrame.setVisible(True)
        elif page == CAL_PAGE:
            self.makeTimer()
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
            for index, probe in enumerate(self.probeGridLayout.probes):
                probe.update_value(self.pot_values[index])
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

    def closeEvent(self, event):
        self.serialThread.cancel()


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
