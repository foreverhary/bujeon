import sys
from winsound import Beep

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QApplication

from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import window_center, style_sheet_setting, NFC_IN, FUNCTION_PROCESS, \
    PROCESS_OK_RESULTS, PROCESS_NAMES, FREQ, DUR, NG, RED, LIGHT_SKY_BLUE, PROCESS_FULL_NAMES, WHITE, A, B, YELLOW, C, \
    GREEN, RELEASE_GRADE_TEXT_SIZE
from release_process_ui import ReleaseProcessUI, RELEASE_FIXED_RESULT_FONT_SIZE

NFC_IN_COUNT = 1


class ReleaseProcess(ReleaseProcessUI):
    key_enter_input_signal = pyqtSignal()

    def __init__(self, app):
        super(ReleaseProcess, self).__init__()
        self.app = app
        self.nfc = None

        self.load_window = SplashScreen("Release")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        self.load_window.close()
        self.init_event()
        if self.init_nfc_serial(nfcs):
            self.status_label.set_color(LIGHT_SKY_BLUE)
            self.status_label.setText('NFC READY')
        else:
            self.status_label.set_color(RED)
            self.status_label.setText('CHECK NFC AND RESTART PROGRAM')
        style_sheet_setting(self.app)

        # self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.show()

        window_center(self)

    def init_event(self):
        pass

    def init_nfc_serial(self, nfcs):
        nfc_in_count = 0
        for nfc in nfcs:
            if NFC_IN in nfc.serial_name:
                nfc.previous_processes = PROCESS_NAMES
                self.nfc = nfc
                nfc.signal.previous_process_signal.connect(self.received_previous_process)
                nfc.start_previous_process_check_thread()
                nfc_in_count += 1
            else:
                nfc.close()

        return nfc_in_count == NFC_IN_COUNT

    # @pyqtSignal(object)
    def received_previous_process(self, nfc):
        Beep(FREQ, DUR)
        msg = ''
        if nfc.check_pre_process():
            msg += nfc.nfc_previous_process[FUNCTION_PROCESS]
            if msg == A:
                color = WHITE
            elif msg == B:
                color = YELLOW
            elif msg == C:
                color = GREEN
            self.result_input_label.set_text_property(size=RELEASE_GRADE_TEXT_SIZE)
            self.result_input_label.set_color(color)
        else:
            for process in nfc.previous_processes:
                if not (result := nfc.nfc_previous_process.get(process)):
                    result = 'MISS'
                if result not in PROCESS_OK_RESULTS:
                    if msg:
                        msg += '\n'
                    msg += f"{PROCESS_FULL_NAMES[process]} : {result}"

            self.result_input_label.set_text_property(size=RELEASE_FIXED_RESULT_FONT_SIZE)
            self.result_input_label.set_color(RED)
        self.dm_input_label.setText(nfc.dm)
        self.result_input_label.setText(msg or NG)

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
    ex = ReleaseProcess(app)
    sys.exit(app.exec_())
