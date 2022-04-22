import re
import sys
from threading import Thread

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QGraphicsDropShadowEffect, QApplication, QDesktopWidget
from serial import Serial

from process_package.SerialNFC import SerialNFC
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import logger
from process_package.ui_splash_screen import Ui_SplashScreen

# GLOBALS
counter = 0
jumper = 10


class SplashScreen(QMainWindow):
    serial_check_signal = pyqtSignal()
    start_signal_old = pyqtSignal(dict)
    start_signal = pyqtSignal(list)

    def __init__(self, app_name):
        QMainWindow.__init__(self)
        self.ui = Ui_SplashScreen()
        self.ui.setupUi(self, app_name)

        self.ser_list_old = {}
        self.ser_list = []

        self.counter = 0
        self.jumper = 0

        # ==> SET INITIAL PROGRESS BAR TO (0) ZERO
        self.progressBarValue(0)

        # ==> REMOVE STANDARD TITLE BAR
        self.setWindowFlags(Qt.FramelessWindowHint)  # Remove title bar
        self.setAttribute(Qt.WA_TranslucentBackground)  # Set background to transparent

        # ==> APPLY DROP SHADOW EFFECT
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 120))
        self.ui.circularBg.setGraphicsEffect(self.shadow)

        # Connect signal
        self.serial_check_signal.connect(self.start_progress)

        #
        # # ## QTIMER ==> START
        # self.timer = QTimer()
        # self.timer.timeout.connect(self.progress)
        # # TIMER IN MILLISECONDS
        # self.timer.start(15)

        # SHOW ==> MAIN WINDOW
        ########################################################################
        self.show()
        # ==> END ##

        # center
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

        # Start Serial Thread
        thread = Thread(target=self.setting_serial_automation)
        # if app_name == "IR SENSOR" or app_name == "QR RESISTOR" or app_name == 'AIR LEAK':
        #     thread = Thread(target=self.setting_serial_automation)
        # else:
        #     thread = Thread(target=self.setting_serial_automation_old)

        thread.daemon = True
        thread.start()

    def start_progress(self):
        self.jumper += 1 / ports.__len__() * 100
        self.timer = QTimer()
        self.timer.timeout.connect(self.progress)
        self.timer.start(1)

    # DEF TO LOANDING    ########################################################################
    def progress(self):
        value = self.counter

        # HTML TEXT PERCENTAGE
        htmlText = """<p><span style=" font-size:68pt;">{VALUE}</span><span style=" font-size:58pt; vertical-align:super;">%</span></p>"""

        # REPLACE VALUE
        # newHtml = htmlText.replace("{VALUE}", str(round(self.jumper)))
        newHtml = htmlText.replace("{VALUE}", str(round(self.counter)))

        if value > self.jumper:
            # APPLY NEW PERCENTAGE TEXT

            self.timer.stop()

        # SET VALUE TO PROGRESS BAR
        # fix max value error if > than 100
        self.ui.labelPercentage.setText(newHtml)
        if value >= 100: value = 0
        self.progressBarValue(value)

        # CLOSE SPLASH SCREE AND OPEN APP
        if self.counter >= 100:
            # STOP TIMER
            self.timer.stop()

            # SHOW MAIN WINDOW
            self.start_signal.emit(self.ser_list)
            self.start_signal_old.emit(self.ser_list_old)
            # self.start_signal.emit()

        # INCREASE COUNTER
        self.counter += 0.5

    # DEF PROGRESS BAR VALUE
    ########################################################################
    def progressBarValue(self, value):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 150px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} rgba(85, 170, 255, 255));
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace("{STOP_2}", stop_2)

        # APPLY STYLESHEET WITH NEW VALUES
        self.ui.circularProgress.setStyleSheet(newStylesheet)

    def serial_nfc_check_old(self, port, ser_list):
        ser = Serial()
        ser.port = port
        ser.timeout = 2
        ser.baudrate = 115200
        try:
            ser.open()
            if check_string := ser.readline().decode().replace('\r\n', ''):
                if re.search("NFC", check_string):
                    ser.timeout = None
                    ser_list[check_string] = ser
                else:
                    ser.close()
            else:
                ser.close()
        except Exception as e:
            logger.error(port)
            logger.error(f"{type(e)}, {e}")
        self.serial_check_signal.emit()

    def serial_nfc_check(self, port, ser_list):
        ser = SerialNFC(port, 115200, timeout=2)
        if ser.is_nfc():
            ser_list.append(ser)
        self.serial_check_signal.emit()

    def setting_serial_automation(self):
        th = []
        ser_list = []
        for port in ports:
            t = Thread(target=self.serial_nfc_check, args=(port, ser_list), daemon=True)
            t.start()
            th.append(t)
        for t in th:
            t.join()
        for ser in ser_list:
            logger.info(ser.serial_name)
        self.ser_list = ser_list

    def setting_serial_automation_old(self):
        th = []
        ser_list = {}
        for port in ports:
            t = Thread(target=self.serial_nfc_check_old, args=(port, ser_list), daemon=True)
            t.start()
            th.append(t)
        for t in th:
            t.join()
        print(ser_list)
        self.ser_list_old = ser_list


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SplashScreen('test')
    sys.exit(app.exec_())
