from PySide2.QtCore import Qt
from PySide2.QtWidgets import QVBoxLayout

from process_package.Views.CustomComponent import Widget, LabelTimerClean
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.resource.size import RELEASE_LABEL_MINIMUM_WIDTH, RELEASE_DATA_MATRIX_MINIMUM_HEIGHT, \
    RELEASE_STATUS_FONT_SIZE, RELEASE_RESULT_FONT_SIZE
from process_package.resource.string import STR_DATA_MATRIX, STR_RESULT, STR_STATUS


class ReleaseProcessView(Widget):
    def __init__(self, *args):
        super(ReleaseProcessView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX,
                                                   is_clean=True,
                                                   clean_time=2000))
        layout.addWidget(result := GroupLabel(STR_RESULT,
                                              font_size=RELEASE_RESULT_FONT_SIZE,
                                              is_clean=True,
                                              clean_time=1500))
        layout.addWidget(status := GroupLabel(STR_STATUS, font_size=RELEASE_STATUS_FONT_SIZE))

        data_matrix.setMinimumSize(RELEASE_LABEL_MINIMUM_WIDTH, RELEASE_DATA_MATRIX_MINIMUM_HEIGHT)


        self.data_matrix = data_matrix.label
        self.result = result.label
        self.status = status.label

        # connect widgets to controller

        # listen for model event signals
