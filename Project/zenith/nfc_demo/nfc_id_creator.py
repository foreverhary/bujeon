import sys
from threading import Thread
from winsound import Beep

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGridLayout, QGroupBox

from NFC import VirtualNFC
from process_package.PyQtCustomComponent import LineEdit, Button, Label
from process_package.SplashScreen import SplashScreen
from process_package.check_string import check_nfc_uid
from process_package.defined_variable_function import style_sheet_setting, window_bottom_left, FREQ, DUR, logger

LOCATION = 'AA'


class NFCIDCreator(QWidget):
    update_id_signal = pyqtSignal()

    def __init__(self, app):
        super(NFCIDCreator, self).__init__()
        self.app = app
        self.id_num = 1100001
        self.setLayout(layout := QGridLayout())
        layout.addWidget(Label('ID'), 0, 0)
        layout.addWidget(id_value := LineEdit(LOCATION + str(self.id_num)), 0, 1)
        layout.addWidget(Label('RESULT'), 1, 0)
        layout.addWidget(result_value := LineEdit('AIR:OK,MIC:OK,FUN:A'), 1, 1)

        self.id = id_value
        self.result = result_value
        self.result.setMinimumWidth(400)
        self.update_id_signal.connect(self.up_id)

        self.load_nfc_window = SplashScreen("QR RESISTOR")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()
        self.nfc = nfc_list[0]
        for nfc in nfc_list[1:]:
            nfc.close()

        self.th = Thread(target=self.write_auto, daemon=True)
        self.th.start()

        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

    def up_id(self):
        self.id.setText(LOCATION + str(self.id_num))

    def write_auto(self):
        saved_uid = ''
        write_msg = ''
        while True:
            if check_nfc_uid(read_line := self.nfc.readline().decode().replace('\r', '').replace('\n', '')):
                uid = read_line.split(',')[0]
                logger.debug(uid)
                if uid != saved_uid:
                    saved_uid = uid
                    write_msg = self.id.text()
                    if self.result.text():
                        write_msg += f',{self.result.text()}'
                    logger.debug(write_msg)
                    self.nfc.write(write_msg.encode())
                    self.id_num += 1

                    self.update_id_signal.emit()
                elif write_msg and write_msg in read_line:
                    logger.debug(read_line)
                    write_msg = ''
                    Beep(FREQ, DUR)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFCIDCreator(app)
    sys.exit(app.exec_())
