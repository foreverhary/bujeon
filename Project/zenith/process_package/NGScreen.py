from threading import Timer

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout

from process_package.PyQtCustomComponent import Label
from process_package.defined_variable_function import RED, PROCESS_OK_RESULTS, PROCESS_FULL_NAMES

NG_FONT_SIZE = 70


class NGScreen(QDialog):
    def __init__(self):
        super(NGScreen, self).__init__()

        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(ng_label := Label())
        ng_label.set_background_color(RED)

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.timeout_close)
        self.ng_label = ng_label
        ng_label.set_font_size(100)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def timeout_close(self):
        self.close_timer.stop()
        self.close()

    def set_text(self, nfc, process_names):
        msg = f"{nfc.dm}\n"
        for process in process_names:
            if not (result := nfc.nfc_previous_process.get(process)):
                result = 'MISS'
            if result not in PROCESS_OK_RESULTS:
                if msg:
                    msg += '\n'
                msg += f"{PROCESS_FULL_NAMES[process]} : {result}"
        self.ng_label.setText(msg)

    def show_modal(self):
        self.close_timer.start(5000)
        # self.showMaximized()
        self.show()