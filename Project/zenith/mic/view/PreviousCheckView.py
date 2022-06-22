from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from process_package.Views.CustomComponent import Widget, Label, LabelTimerClean
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.size import MATCHING_PREVIOUS_PROCESS_FONT_SIZE, MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT, \
    MATCHING_DATA_MATRIX_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, MATCHING_STATUS_FONT_SIZE, \
    MATCHING_STATUS_MAXIMUM_HEIGHT
from process_package.resource.string import STR_PREVIOUS_PROCESS, STR_DATA_MATRIX, STR_STATUS, STR_QR_MATCHING


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
