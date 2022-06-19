import sys
from threading import Timer
from winsound import Beep

from PySide2.QtCore import Signal, Qt
from PySide2.QtGui import QCursor
from PySide2.QtWidgets import QApplication

from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, NFC_IN, FUNCTION_PROCESS, \
    PROCESS_OK_RESULTS, PROCESS_NAMES, FREQ, DUR, NG, RED, LIGHT_SKY_BLUE, PROCESS_FULL_NAMES, WHITE, A, B, YELLOW, C, \
    GREEN, RELEASE_GRADE_TEXT_SIZE
from release_process_ui import ReleaseProcessUI, RELEASE_FIXED_RESULT_FONT_SIZE

NFC_IN_COUNT = 1


class ReleaseProcess(ReleaseProcessUI):
    key_enter_input_signal = Signal()

    def __init__(self, app):
        super(ReleaseProcess, self).__init__()
        self.app = app
        self.nfc = None

        self.load_window = SplashScreen("Release", [])
        self.load_window.start_signal.connect(self.show_main_window)
        self.clean_timer = Timer(1, self.show_main_window)

    def show_main_window(self, nfcs):
        self.load_window.close()
        if self.init_nfc_serial(nfcs):
            self.status_label.set_color(LIGHT_SKY_BLUE)
            self.status_label.setText('NFC READY')
        else:
            self.status_label.set_color(RED)
            self.status_label.setText('CHECK NFC AND RESTART PROGRAM')
        style_sheet_setting(self.app)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.showMaximized()
        self.show()

    def init_nfc_serial(self, nfcs):
        nfc_in_count = 0
        for nfc in nfcs:
            self.nfc = nfc
            nfc.signal.previous_process_signal.connect(self.received_previous_process)
            nfc.start_previous_process_check_thread()
            nfc_in_count += 1

        return nfc_in_count

    # @Signal(object)
    def received_previous_process(self, nfc):
        if self.clean_timer.is_alive():
            self.clean_timer.cancel()
        Beep(FREQ, DUR)
        self.dm_input_label.setText(nfc.dm)
        self.display_result(nfc)
        # self.result_input_label.clean()
        # t = Timer(0.5, self.display_result, args=(nfc,))
        # t.start()

    def display_result(self, nfc):

        msg = ''
        color = WHITE
        self.result_input_label.clean()
        if nfc.check_pre_process(PROCESS_NAMES):
            msg += nfc.nfc_previous_process[FUNCTION_PROCESS]
            if msg == A:
                color = WHITE
            elif msg == B:
                color = YELLOW
            elif msg == C:
                color = GREEN
            self.result_input_label.set_font_size(size=RELEASE_GRADE_TEXT_SIZE)
        else:
            for process in PROCESS_NAMES:
                if not (result := nfc.nfc_previous_process.get(process)):
                    result = 'MISS'
                if result not in PROCESS_OK_RESULTS:
                    if msg:
                        msg += '\n'
                    msg += f"{PROCESS_FULL_NAMES[process]} : {result}"

            self.result_input_label.set_font_size(size=RELEASE_FIXED_RESULT_FONT_SIZE)
            self.result_input_label.set_background_color(RED)
        self.result_input_label.set_color(color)
        self.result_input_label.setText(msg or NG)
        self.clean_timer = Timer(1.5, self.clean_display)
        self.clean_timer.start()

    def clean_display(self):
        # self.dm_input_label.clean()
        # self.result_input_label.clean()
        self.nfc.check_dm = ''

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.result_input_label.clean()
            self.dm_input_label.clean()
            self.status_label.set_color(LIGHT_SKY_BLUE)
            self.status_label.setText('NFC READY')
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
#
from PySide2.QtWidgets import QApplication

from process_package.Views.CustomComponent import style_sheet_setting


class ReleaseProcess(QApplication):
    def __init__(self, sys_argv):
        super(ReleaseProcess, self).__init__(sys_argv)
        style_sheet_setting(self)
        self._model = ReleaseProcessModel()
        self._control = ReleaseProcessControl(self._model)
        self._view = ReleaseProcessView(self._model, self._control)
        self._view.show()

if __name__ == '__main__':
    app = ReleaseProcess(sys.argv)
    sys.exit(app.exec_())
