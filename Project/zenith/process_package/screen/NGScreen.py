from PySide2.QtCore import QTimer, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout

from process_package.component.CustomComponent import Label
from process_package.resource.color import RED
from process_package.resource.string import STR_DATA_MATRIX, PROCESS_FULL_NAMES

NG_FONT_SIZE = 70


class NGScreen(QDialog):
    def __init__(self, parent_control):
        super(NGScreen, self).__init__()
        self._parent_control = parent_control

        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(ng_label := Label())
        ng_label.set_background_color(RED)

        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.close)
        self.close_timer.start(2000)
        self.ng_label = ng_label
        ng_label.set_font_size(100)

        self.set_text(self._parent_control.previous)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.show_modal()

    def closeEvent(self, e):
        self.close_timer.stop()
        self._parent_control.ng_screen_opened = False

    def set_text(self, previous):
        msg = ''
        if data_matrix := previous.get(STR_DATA_MATRIX):
            msg += data_matrix
        for name, full_name in PROCESS_FULL_NAMES.items():
            if name == self._parent_control.process_name:
                break
            msg += '\n'
            if process_result := previous.get(name):
                msg += f"{full_name}:{process_result}"
            else:
                msg += f"{full_name}:MISS"
        self.ng_label.setText(msg)

    def show_modal(self):
        return super().exec_()
