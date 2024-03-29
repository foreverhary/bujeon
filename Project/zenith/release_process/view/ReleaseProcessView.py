from PySide2.QtWidgets import QVBoxLayout

from process_package.component.CustomComponent import Widget, LabelTimerClean
from process_package.component.CustomMixComponent import GroupLabel
from process_package.resource.size import RELEASE_LABEL_MINIMUM_WIDTH, RELEASE_DATA_MATRIX_FIXED_HEIGHT, \
    RELEASE_RESULT_FONT_SIZE, NFC_FIXED_HEIGHT, RELEASE_RESULT_MIN_HEIGHT
from process_package.resource.string import STR_DATA_MATRIX, STR_RESULT, STR_NFC1


class ReleaseProcessView(Widget):
    def __init__(self, *args):
        super(ReleaseProcessView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := GroupLabel(STR_NFC1))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX,
                                                   label=LabelTimerClean(
                                                           is_clean=True,
                                                           clean_time=2000)))
        layout.addWidget(result := GroupLabel(STR_RESULT,
                                              label=LabelTimerClean(
                                                      font_size=RELEASE_RESULT_FONT_SIZE,
                                                      is_clean=True,
                                                      clean_time=1500)))

        nfc.setFixedHeight(NFC_FIXED_HEIGHT)
        data_matrix.setFixedHeight(RELEASE_DATA_MATRIX_FIXED_HEIGHT)
        data_matrix.setMinimumWidth(RELEASE_LABEL_MINIMUM_WIDTH)
        result.setMinimumHeight(RELEASE_RESULT_MIN_HEIGHT)

        self.nfc_connection = nfc.label
        self.data_matrix = data_matrix.label
        self.result = result.label

        # connect widgets to controller

        # listen for model event signals
        self._model.nfc_changed.connect(self._control.nfc.setPortName)
        self._model.nfc_changed.connect(self.nfc_connection.setText)
        self._model.nfc_connection_changed.connect(self.nfc_connection.set_background_color)

        self._model.data_matrix_changed.connect(self.data_matrix.setText)

        self._model.result_changed.connect(self.result.setText)
        self._model.result_font_size_changed.connect(self.result.set_font_size)
        self._model.result_font_color_changed.connect(self.result.set_color)
        self._model.result_background_color_changed.connect(self.result.set_background_color)
