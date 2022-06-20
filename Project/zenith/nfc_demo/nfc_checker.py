import sys

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QDialog, QGridLayout, QApplication

from nfc_layout import NFCLayout
from process_package.Views.CustomComponent import Label, Widget, style_sheet_setting, window_center
from process_package.resource.color import RED
from process_package.screen.SplashScreen import SplashScreen
LOCATION = 'AA'


class NFCCheckerDialog(QDialog):
    checker_close_signal = Signal()

    def __init__(self, nfc_list):
        super(NFCCheckerDialog, self).__init__()
        self.setLayout(layout := QGridLayout())
        self.grid_layout = layout
        self.nfc_list = nfc_list
        self.set_nfc_list()

    def set_nfc_list(self):
        self.nfc_layout = []
        for index, nfc in enumerate(self.nfc_list):
            self.grid_layout.addLayout(nfc_layout := NFCLayout(nfc), index // 2, index % 2)
            self.nfc_layout.append(nfc_layout)
        if not self.nfc_list:
            self.grid_layout.addWiget(label := Label('NO NFC'))
            label.set_color(RED)

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

    def closeEvent(self, e):
        for nfc in self.nfc_list:
            nfc.debug = False
        self.checker_close_signal.emit()
        self.close()

    def show_modal(self):
        for nfc in self.nfc_list:
            nfc.debug = True
        return super().exec_()


class NFCChecker(Widget):
    def __init__(self, app):
        super(NFCChecker, self).__init__(1,2)
        self.app = app
        self.setLayout(layout := QGridLayout())
        self.grid_layout = layout
        self.nfc_layout = []

        self.load_nfc_window = SplashScreen("NFC Checker")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_nfc_window.close()

        for index, (port, nfc) in enumerate(nfc_list.items()):
            self.grid_layout.addLayout(nfc_layout := NFCLayout(nfc), index // 2, index % 2)
            self.nfc_layout.append(nfc_layout)
        if not nfc_list:
            self.grid_layout.addWidget(label := Label('NO NFC'))
            label.set_color(RED)
        style_sheet_setting(self.app)
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()
        window_center(self)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = NFCChecker(app)
    sys.exit(app.exec_())
