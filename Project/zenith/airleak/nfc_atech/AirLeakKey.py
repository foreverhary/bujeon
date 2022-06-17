import re
import sys
from queue import Queue
from threading import Timer, Thread
from time import time

from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from serial import Serial, SerialException

from process_package.models.Config import Config
from process_package.check_string import check_nfc_uid, check_dm
from process_package.defined_serial_port import connect_serial, serial_flush
from process_package.defined_variable_function import *
from process_package.tools.logger import get_logger
from process_package.mssql_connect import insert_air_leaks

from AirLeakUi import AirLeakUi
from process_package.mssql_dialog import MSSQLDialog


class AirLeak(AirLeakUi):
    """
    Air Leak 좌우 채널용으로 left, right로 구분된 인자를 사용하기 위해 __dict__가 많이 사용 되었다.
    """
    new_dm_signal = pyqtSignal(str)
    machine_signal = pyqtSignal(str)
    write_nfc_signal = pyqtSignal(str)

    def __init__(self, app):
        super(AirLeak, self).__init__()
        self.app = app

        # variable
        self.input_nfc = {}
        self.delete_queue = Queue()
        self.delete_timer = Timer(10, self.delete_timer_function)

        # set logger
        self.logger = get_logger('LOG')
        # self.logger.setLevel(INFO)

        # config
        self.config = Config('air_leak.ini')
        self.mssql_config_window = MSSQLDialog()

        # connect event
        self.connectEvent()

        # window setting
        self.setWindowTitle('Air Leak v0.1')
        self.setWindowIcon(QIcon("./icon/python-icon.png"))

        # self.load_window = SplashScreen()
        # self.load_window.start_signal.connect(self.show_main_window)
        self.show_main_window()

    def show_main_window(self):
        # self.load_window.close()
        self.init_serial()
        style_sheet_setting(self.app)

        self.show()

        window_center(self)

    def init_serial(self):
        self.machine_ser = Serial()
        self.machine_ser.baudrate = 9600
        self.nfc_in_ser = Serial()
        self.nfc_in_ser.baudrate = 115200
        self.nfc_out_ser = Serial()
        self.nfc_out_ser.baudrate = 115200
        self.nfc_in_comport.setCurrentText(self.config.get_value(COMPORT_SECTION, NFC_COMPORT_1))
        self.nfc_out_comport.setCurrentText(self.config.get_value(COMPORT_SECTION, NFC_COMPORT_2))
        self.machine_comport.setCurrentText(self.config.get_value(COMPORT_SECTION, MACHINE_COMPORT_1))
        self.nfc_in_connect_clicked(self.nfc_in_comport.currentText(), self.nfc_in_connect_button)
        self.nfc_out_connect_clicked(self.nfc_out_comport.currentText(), self.nfc_out_connect_button)
        self.result_connect_clicked(self.machine_comport.currentText(), self.machine_connect_button)

    def connectEvent(self):
        self.nfc_in_connect_button.clicked.connect(self.nfc_in_connect_clicked)
        self.machine_connect_button.clicked.connect(self.result_connect_clicked)
        self.nfc_out_connect_button.clicked.connect(self.nfc_out_connect_clicked)
        self.new_dm_signal.connect(self.input_new_dm)
        self.machine_signal.connect(self.machine_result)
        self.write_nfc_signal.connect(self.write_nfc)

    def delete_timer_function(self):
        if uid := self.delete_queue.get():
            del self.input_nfc[self.input_nfc[uid]]
            del self.input_nfc[uid]
        if not self.delete_queue.empty():
            self.delete_timer = Timer(10, self.delete_timer_function)
            self.delete_timer.start()

    @pyqtSlot(str)
    def machine_result(self, result):
        dms = list()
        for input_label, output_label in zip(self.unit_in_list, self.unit_out_list):
            output_label[UNIT].setText('')
            output_label[RESULT].setText('')
            output_label[WRITE].setText('')
            output_label[UNIT].setText(dm := input_label.text())
            input_label.setText('')
            output_label[RESULT].setText('')
            if dm != '':
                dms.append(dm)
                output_label[RESULT].setText(result)
                output_label[RESULT].set_font_size(color=(LIGHT_SKY_BLUE, RED)[result == NG])
                self.input_nfc[output_label[UNIT].text()][STATUS] = RESULT
                self.input_nfc[output_label[UNIT].text()][RESULT] = result
        try:
            insert_air_leaks(self.config, dms, result)
        except Exception as e:
            self.logger.error(f"{type(e)} : {e}")
            pass

    @pyqtSlot(str)
    def write_nfc(self, uid):
        self.logger.debug('write_nfc')
        for output_label in self.unit_out_list:
            if output_label[UNIT].text() == self.input_nfc[uid]:
                output_label[WRITE].setText(OK)
                output_label[WRITE].set_font_size(color=LIGHT_SKY_BLUE)
                with lock:
                    self.input_nfc[self.input_nfc[uid]][STATUS] = DONE
                    self.delete_queue.put(uid)
                    if not self.delete_timer.is_alive():
                        self.delete_timer = Timer(10, self.delete_timer_function)
                        self.delete_timer.start()
                break

    @pyqtSlot(str)
    def input_new_dm(self, dm):
        with lock:
            self.input_nfc[dm] = {STATUS: READY}
        for input_label in self.unit_in_list:
            if input_label.text() == '':
                input_label.setText(dm)
                break

    def nfc_in_connect_clicked(self, port=None, button=None):
        if not port:
            port = self.nfc_in_comport.currentText()
        if not button:
            button = self.sender()
        if connect_serial(self.nfc_in_ser, port, button):
            self.config.set_value(COMPORT_SECTION, NFC_COMPORT_1, self.nfc_in_ser.port)
            try:
                if not self.nfc_in_thread.is_alive():
                    raise AttributeError
            except AttributeError:
                self.nfc_in_thread = Thread(target=self.nfc_read_write, args=(self.nfc_in_ser,))
                self.nfc_in_thread.daemon = True
                self.nfc_in_thread.start()

    def nfc_out_connect_clicked(self, port=None, button=None):
        if not port:
            port = self.nfc_out_comport.currentText()
        if not button:
            button = self.sender()
        if connect_serial(self.nfc_out_ser, port, button):
            self.config.set_value(COMPORT_SECTION, NFC_COMPORT_2, self.nfc_out_ser.port)
            try:
                if not self.nfc_out_thread.is_alive():
                    raise AttributeError
            except AttributeError:
                self.nfc_out_thread = Thread(target=self.nfc_read_write, args=(self.nfc_out_ser,))
                self.nfc_out_thread.daemon = True
                self.nfc_out_thread.start()

    def result_connect_clicked(self, port=None, button=None):
        if not port:
            port = self.machine_comport.currentText()
        if not button:
            button = self.sender()
        if connect_serial(self.machine_ser, port, button):
            self.config.set_value(COMPORT_SECTION, MACHINE_COMPORT_1, self.machine_ser.port)
            try:
                if not self.machine_thread.is_alive():
                    raise AttributeError
            except AttributeError:
                self.machine_thread = Thread(target=self.machine_read)
                self.machine_thread.daemon = True
                self.machine_thread.start()

    def nfc_read_write(self, ser):
        while True:
            try:
                if ser.inWaiting():
                    self.logger.debug(f"line start : {time()}")
                else:
                    continue
                if read_line := ser.readline().decode().replace('\r\n', '').split(","):
                    self.logger.debug(read_line)
                    if uid := check_nfc_uid(read_line[UID_BLOCK]):
                        if dm := check_dm(read_line[DM_BLOCK]):
                            result_dict = {}
                            for item in read_line[2:]:
                                split_item = item.split(':')
                                try:
                                    result_dict[split_item[0]] = split_item[1]
                                except IndexError:
                                    break
                            if dm in self.input_nfc:
                                self.logger.debug(f"{dm}, {self.input_nfc[dm]}")
                            if not (uid in self.input_nfc):
                                self.input_nfc[uid] = dm
                            if not (dm in self.input_nfc):
                                self.new_dm_signal.emit(dm)
                                self.logger.debug(f"read done : {time()}")
                            elif self.input_nfc[dm][STATUS] == RESULT:
                                if 'AIR' in result_dict:
                                    if result_dict['AIR'] == self.input_nfc[dm][RESULT]:
                                        # write done
                                        self.logger.debug(f"write done : {time()}")
                                        self.write_nfc_signal.emit(uid)
                                    else:
                                        self.write_result(dm, result_dict, ser)
                                else:
                                    self.write_result(dm, result_dict, ser)

            except SerialException as e:
                self.logger.warning(type(e))
                ser.close()
                break
            except Exception as e:
                self.logger.error(f"{type(e)} : {e}")

    def write_result(self, dm, result_dict, ser):
        write_data = f"{dm}"
        result_dict['AIR'] = self.input_nfc[dm][RESULT]
        for key, value in result_dict.items():
            write_data += f",{key}:{value}"
        ser.write(write_data.encode())

    def machine_read(self):
        serial_flush(self.machine_ser)
        while True:
            try:
                if result := re.search("[A-Z]{2}", self.machine_ser.readline().decode()):
                    result = result.group(0)
                    self.machine_signal.emit(result)

            except SerialException:
                self.machine_ser.close()
                break
            except Exception as e:
                self.logger.error(e)

    def mousePressEvent(self, event):
        if event.buttons() & Qt.RightButton:
            self.mssql_config_window.show_modal()

    def closeEvent(self, event):
        self.delete_timer.cancel()
        self.nfc_in_ser.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = AirLeak(app)
    sys.exit(app.exec_())
