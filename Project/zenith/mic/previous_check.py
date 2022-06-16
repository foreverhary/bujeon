import sys

from PySide2.QtCore import Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QWidget, QApplication, QVBoxLayout

from process_package.Views.CustomComponent import Label, Widget
from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, NFCIN1, PROCESS_OK_RESULTS, \
    PROCESS_FULL_NAMES, RED, LIGHT_SKY_BLUE, AIR_LEAK_PROCESS


class PreviousCheck(Widget):
    def __init__(self, app):
        super(PreviousCheck, self).__init__()
        self.app = app
        self.nfc = None
        self.init_ui()
        self.load_window = SplashScreen("AIR LEAK", [])
        self.load_window.start_signal.connect(self.show_main_window)

    def init_ui(self):
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(label := Label(font_size=50, is_clean=True, clean_time=2000))
        self.result_label = label
        self.result_label.setFixedSize(420, 230)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.show()
        self.move(470, 135)
        # window_center(self)

    def init_serial(self, nfc_list):
        for nfc in nfc_list:
            if nfc.serial_name == NFCIN1:
                self.nfc = nfc
                nfc.start_previous_process_check_thread()
                nfc.signal.previous_process_signal.connect(self.received_previous_process)
            else:
                nfc.close()

    def received_previous_process(self, nfc):
        nfc.clean_check_dm()
        msg = nfc.dm
        if not nfc.check_pre_process([AIR_LEAK_PROCESS]):
            self.result_label.set_background_color(RED)
            if not (result := nfc.nfc_previous_process.get(AIR_LEAK_PROCESS)):
                result = 'MISS'
            if result not in PROCESS_OK_RESULTS:
                msg += '\n'
                msg += f"{PROCESS_FULL_NAMES[AIR_LEAK_PROCESS]} : {result}"
        else:
            self.result_label.set_background_color(LIGHT_SKY_BLUE)

        self.result_label.setText(msg)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = PreviousCheck(app)
    sys.exit(app.exec_())
