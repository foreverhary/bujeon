import os
import re
import sys
import time
from threading import Thread

from PyQt5.QtCore import Qt, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication
from pynput import keyboard
from pynput.keyboard import Key
from serial import Serial, SerialException

from AudioBusConfig import AudioBusConfig
from AudioBusUI import AudioBusUI
from FileObserver import Target
from process_package.Config import Config
from process_package.check_string import check_dm, keyboard_event_check_char
from process_package.defined_serial_port import setting_serial_automation
from process_package.logger import get_logger
from process_package.mssql_connect import *
from process_package.order_number_dialog import OderNumberDialog
from process_package.style.style import STYLE


class AudioBus(AudioBusUI):
    key_enter_input_signal = pyqtSignal()
    get_grade_signal = pyqtSignal(str)
    get_ok_ng_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str, str)
    input_qr_signal = pyqtSignal(str)

    def __init__(self):
        super(AudioBus, self).__init__()

        # set logger
        self.logger = get_logger('AudioBus')

        # config
        self.config = Config('config.ini')

        # variable
        self.msg = ''

        # sub windows
        self.audio_bus_config_window = AudioBusConfig(self.config)
        self.order_config_window = OderNumberDialog(self.config)

        # connect Event
        self.init_event()

        # qr serial
        self.ser = Serial()
        self.ser.baudrate = 9600
        if port := self.config.get_value(COMPORT_SECTION, NFC_COMPORT_1):
            self.ser.port = port
            self.qr_read_start()

        # NFC Auto connect
        self.nfc = []
        ser_dict = setting_serial_automation()
        for index in range(1,3):
            if ser := ser_dict.get(f"nfc {index}"):
        for index, key in ser_dict:
        for key, value in ser_dict.items():
            if key == "NFC 1":
                self.nfc_in = value

            if key == "NFC 2"

        # window setting
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.show()

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().bottomLeft()
        qr.moveBottomLeft(cp)
        self.move(qr.topLeft())

    def qr_read_start(self):
        try:
            self.ser.open()
            self.status_signal.emit(READY, BLUE)
            self.audio_bus_config_window.comport_combobox.setCurrentText(self.ser.port)
            self.audio_bus_config_window.comport_connect_button.set_clicked(BLUE)
            self.read_thread = Thread(target=self._read_qr)
            self.read_thread.start()
        except SerialException as e:
            self.logger.error(e)
            self.qr_error()
        except Exception as e:
            self.logger.error(e)

    def init_event(self):
        self.key_enter_input_signal.connect(self.key_enter_process)
        self.get_grade_signal.connect(self.grade_process)
        self.get_ok_ng_signal.connect(self.ok_ng_process)
        self.status_signal.connect(self.update_status_process)
        self.input_qr_signal.connect(self.qr_update)
        self.audio_bus_config_window.comport_connect_button.clicked.connect(self.connect_qr_serial)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.audio_bus_config_window.showModal()
        if e.buttons() & Qt.LeftButton:
            self.order_config_window.show_modal()
        if e.buttons() & Qt.MidButton:
            self.ser.close()
            QCoreApplication.instance().quit()

    def connect_qr_serial(self):
        self.ser.port = self.audio_bus_config_window.comport_combobox.currentText()

        try:
            if self.ser.isOpen():
                self.ser.close()
                self.qr_error()
            else:
                self.qr_read_start()
        except SerialException as e:
            self.logger.error(e)
            self.qr_error()
        except Exception as e:
            self.logger.error(e)
            self.qr_error()
        time.sleep(1)

    def qr_update(self, qr):
        self.grade_label.setText(qr)
        if os.path.isdir(path := self.config.get_value(AUDIO_BUS_SECTION, GRADE_FILE_PATH)):
            self.start_file_observe(path, self.get_grade_signal)
        else:
            self.status_signal.emit('Check Directory!!!', RED)

    def _read_qr(self):
        while True:
            try:
                if qr := re.search('0x[0-9A-F]{2} 0x[0-9A-F]{2} 0x[0-9A-F]{2} 0x[0-9A-F]{2}', self.ser.readline().decode()):
                    qr = list(map(lambda x: int(x, 16), qr.group(0).split(' ')))
                qr = self.ser.readline().decode().replace('\r\n', '')
                if check_dm(qr):
                    self.input_qr_signal.emit(qr)

            except SerialException as e:
                self.logger.error(e)
                self.qr_error()
                break
            except Exception as e:
                self.logger.error(e)
                self.qr_error()
                break

    def qr_error(self):
        try:
            if self.ser.isOpen():
                self.ser.close()
        except Exception as e:
            self.logger.error(e)
        self.audio_bus_config_window.comport_connect_button.set_clicked(RED)
        self.status_signal.emit('Check QR SCAN!!', RED)

    def update_status_process(self, text, color):
        self.status_label.setText(text)
        self.status_label.set_text_property(color=color)

    def grade_process(self, file_path):
        try:
            self.logger.debug(file_path)
            df = pd.read_csv(file_path)
            self.logger.debug(df)
            self.status_signal.emit('Reading Grade File...', WHITE)
            if os.path.isdir(path := self.config.get_value(AUDIO_BUS_SECTION, SUMMARY_FILE_PATH)):
                self.start_file_observe(path, self.get_ok_ng_signal)
                self.status_signal.emit('Wait Result...', WHITE)
            else:
                self.status_signal.emit('Check Directory!!!', RED)
        except Exception as e:
            self.logger.error(e)

    def ok_ng_process(self, file_path):
        try:
            self.logger.debug(file_path)
            self.status_signal.emit('Read Result...', WHITE)
            df = pd.read_excel(file_path, sheet_name="Summary")
            self.logger.debug(df)
            self.status_signal.emit('Done', BLUE)
        except Exception as e:
            self.logger.error(e)

    def key_enter_process(self):
        if check_dm(self.msg):
            self.grade_label.setText(self.msg)
            if os.path.isdir(path := self.config.get_value(AUDIO_BUS_SECTION, GRADE_FILE_PATH)):
                self.start_file_observe(path, self.get_grade_signal)
            else:
                self.status_signal.emit('Check Directory!!!', RED)
        self.msg = ''

    def start_file_observe(self, file_path, signal):
        try:
            self.observer = Target(file_path, signal)
            self.observer.start()
            self.status_signal.emit('Wait Grade...', WHITE)
        except Exception as e:
            self.logger(e)

    def on_press(self, key):
        try:
            if keyboard_event_check_char(key.char):
                raise TypeError
            self.msg += key.char
        except TypeError:
            pass
        except AttributeError:
            if key == Key.enter:
                self.key_enter_input_signal.emit()
            elif key == Key.space:
                self.msg += ' '

    def on_release(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    # app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
    ex = AudioBus()
    listener = keyboard.Listener(
        on_press=ex.on_press,
        on_release=ex.on_release
    )
    listener.start()
    sys.exit(app.exec_())
