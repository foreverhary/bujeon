import sys
from threading import Thread
from winsound import Beep

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QTextCursor, QCursor
from PyQt5.QtWidgets import QWidget, QApplication, QVBoxLayout, QGridLayout, QGroupBox

from NFC import VirtualNFC
from nfc_layout import NFCLayout
from process_package.PyQtCustomComponent import LineEdit, Button, Label
from process_package.SplashScreen import SplashScreen
from process_package.check_string import check_nfc_uid
from process_package.defined_variable_function import style_sheet_setting, window_bottom_left, FREQ, DUR, logger, \
    window_center

LOCATION = 'AA'


class NFCChecker(QWidget):
    def __init__(self, app):
        super(NFCChecker, self).__init__()
        self.app = app
        self.setLayout(layout := QGridLayout())
        self.grid_layout = layout
        self.nfc_layout = []

        self.load_nfc_window = SplashScreen("NFC Checker")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()

        for index, nfc in enumerate(nfc_list):
            self.grid_layout.addLayout(nfc_layout := NFCLayout(nfc), index // 2, index % 2)
            self.nfc_layout.append(nfc_layout)
        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)

    def mousePressEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            self.m_flag = True
            self.m_Position = e.globalPos() - self.pos()
            e.accept()
            self.setCursor((QCursor(Qt.OpenHandCursor)))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFCChecker(app)
    sys.exit(app.exec_())
