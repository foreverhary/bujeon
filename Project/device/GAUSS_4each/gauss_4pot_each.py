import platform
import sys
from threading import Lock

import pyautogui
import qdarkstyle
from PyQt5.QtCore import QFile, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QFrame
from serial import SerialException

from CalFrame import CalFrame
from Config import Config
from MinMaxFrame import MinMaxFrame
from PotMenu import PotMenu
from ProbeGridLayout import ProbeGridLayout, POT_COUNT, PASS_FAIL_TEXT_SIZE
from clickable import clickable
from defined_variable import CONFIG_FILE_NAME, MENU_PAGE, MAIN_PAGE, CAL_PAGE, MINMAX_PAGE, BUTTON_POT, CONFIG_ON_OFF, \
    OFF, ON, BUTTON_CAL, BUTTON_MIN, BUTTON_MAX, BUTTON_EXIT, CONFIG_CAL, convertStrToValue, CONFIG_MIN, CONFIG_MAX
from gauss_each_serial import SerialGauss

pyautogui.FAILSAFE = False

lock = Lock()

window_ser_list = ['com15', 'com16', 'com17', 'com18']


class Main(QWidget):
    def __init__(self):
        super().__init__()
        if 'Window' in platform.platform():
            self.config = Config('config.ini')
        else:
            self.config = Config(CONFIG_FILE_NAME)

        self.init_ui()
        self.eventConnecter()
        self.pot_values = [0 for _ in range(POT_COUNT)]

        if 'Window' in platform.platform():
            self.ser = [SerialGauss(port=port, baudrate=115200, serial_name=index) for index, port in
                        enumerate(window_ser_list)]
        else:
            self.ser = [SerialGauss(port=f"/dev/ttyACM{index}", baudrate=115200, serial_name=index) for index in
                        range(POT_COUNT)]
        try:
            for ser in self.ser:
                ser.signal.probe_signal.connect(self.update_pot_value)
                ser.signal.stop_signal.connect(self.stop_program)
                ser.open()
                ser.start_thread()
        except SerialException as e:
            self.stop_program()

    @pyqtSlot()
    def stop_program(self):
        print('out')
        sys.exit()

    @pyqtSlot(object)
    def update_pot_value(self, ser):
        self.pot_values[ser.value[0]-1] = ser.value[1]
        self.update_probe_value_display(ser.serial_name)

    def update_probe_value_display(self, index):
        self.probeGridLayout.probes[index].update_value(self.pot_values[index])
        pass_fail = True
        for item in self.probeGridLayout.probes:
            if 'NG' in item.valueOnOff.text():
                pass_fail = False

        self.probeGridLayout.passFailLabel.setText(('FAIL', 'PASS')[pass_fail])
        if pass_fail:
            self.probeGridLayout.pass_fail_color('blue')
        else:
            self.probeGridLayout.pass_fail_color('red')

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

    def eventConnecter(self):
        clickable(self.probeGridLayout.probes[0]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[0].potNum))
        clickable(self.probeGridLayout.probes[1]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[1].potNum))
        clickable(self.probeGridLayout.probes[2]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[2].potNum))
        clickable(self.probeGridLayout.probes[3]).connect(
            lambda: self.probe_clicked(self.probeGridLayout.probes[3].potNum))

        for button in self.potMenuFrame.button:
            button.clicked.connect(self.menu_clicked)

        self.calFrame.okbutton.clicked.connect(self.calOkClicked)

        self.minmaxFrame.buttonEXT.clicked.connect(self.minmaxExtClicked)

    def probe_clicked(self, pot_num):
        self.cancel_thread()
        self.potMenuFrame.setPotNumber(pot_num)
        self.updateDisplay(MENU_PAGE)

    def disable_display(self):
        pyautogui.moveTo(2000, 2000)
        self.probeFrame.setVisible(False)
        self.potMenuFrame.setVisible(False)
        self.calFrame.setVisible(False)
        self.minmaxFrame.setVisible(False)

    def start_thread(self):
        for ser in self.ser:
            ser.start_thread()

    def cancel_thread(self):
        for ser in self.ser:
            ser.thread_stop = True

    def updateDisplay(self, page):
        self.disable_display()
        if page == MAIN_PAGE:
            self.start_thread()
            self.probeFrame.setVisible(True)
        elif page == MENU_PAGE:
            self.cancel_thread()
            self.potMenuFrame.updateValue()
            self.potMenuFrame.setVisible(True)
        elif page == CAL_PAGE:
            self.start_thread()
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

    def closeEvent(self, *args):
        print('out', args)
        # self.cancel_thread()

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
