from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from process_package.Views.CustomComponent import Widget, LabelTimerClean


class PreviousCheckView(Widget):
    def __init__(self, *args):
        super(PreviousCheckView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(label := LabelTimerClean(font_size=50, is_clean=True, clean_time=2000))
        self.result_label = label
        self.result_label.setFixedSize(420, 230)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)


        # connect widgets to controller

        # listen for model event signals
