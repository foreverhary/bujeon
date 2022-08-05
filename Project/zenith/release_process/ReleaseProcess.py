import sys

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QApplication, QVBoxLayout

from process_package.component.CustomComponent import style_sheet_setting, window_center, Widget
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.models.BasicModel import BasicModel
from process_package.resource.color import WHITE, BACK_GROUND_COLOR, RED
from process_package.resource.size import RELEASE_RESULT_FONT_SIZE, NFC_FIXED_HEIGHT, RELEASE_DATA_MATRIX_FIXED_HEIGHT, \
    RELEASE_LABEL_MINIMUM_WIDTH, RELEASE_RESULT_MIN_HEIGHT, RELEASE_GRADE_FONT_SIZE
from process_package.resource.string import STR_RELEASE, STR_NFC1, STR_DATA_MATRIX, STR_RESULT, STR_NFC, STR_FUN, \
    STR_MISS, PROCESS_OK_RESULTS, PROCESS_FULL_NAMES, STR_NG, STR_A, STR_B, STR_C, grade_colors, \
    PROCESS_NAMES_WITHOUT_AIR_LEAK
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import read_beep, logger
from process_package.tools.NFCSerialPort import NFCSerialPort

RELEASE_PROCESS_VERSION = "v1.30"


class ReleaseProcess(QApplication):
    def __init__(self, sys_argv):
        super(ReleaseProcess, self).__init__(sys_argv)
        self._model = ReleaseProcessModel()
        self._control = ReleaseProcessControl(self._model)
        self._view = ReleaseProcessView(self._model, self._control)
        self._view.setWindowTitle(f"Release Process {RELEASE_PROCESS_VERSION}")
        self.load_nfc_window = SplashScreen(STR_RELEASE)
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfcs = nfcs
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


class ReleaseProcessView(Widget):
    def __init__(self, *args):
        super(ReleaseProcessView, self).__init__(*args)
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(STR_NFC1))
        layout.addWidget(data_matrix := GroupLabel(STR_DATA_MATRIX,
                                                   is_clean=True,
                                                   clean_time=2000))
        layout.addWidget(result := GroupLabel(STR_RESULT,
                                              font_size=RELEASE_RESULT_FONT_SIZE,
                                              is_clean=True,
                                              clean_time=1500))

        nfc.setFixedHeight(NFC_FIXED_HEIGHT)
        data_matrix.setFixedHeight(RELEASE_DATA_MATRIX_FIXED_HEIGHT)
        data_matrix.setMinimumWidth(RELEASE_LABEL_MINIMUM_WIDTH)
        result.setMinimumHeight(RELEASE_RESULT_MIN_HEIGHT)

        self.data_matrix = data_matrix.label
        self.result = result.label

        # connect widgets to controller
        nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        # listen for model event signals
        self._model.nfc_changed.connect(nfc.set_port)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)

        self._model.result_changed.connect(self.result.setText)
        self._model.result_font_size_changed.connect(self.result.set_font_size)
        self._model.result_font_color_changed.connect(self.result.set_color)
        self._model.result_background_color_changed.connect(self.result.set_background_color)


class ReleaseProcessControl(QObject):
    close_signal = Signal()

    def __init__(self, model):
        super(ReleaseProcessControl, self).__init__()
        self._model = model

        self.nfc = NFCSerialPort()

        # controller event connect

    @Slot(dict)
    def receive_nfc_data(self, value):
        read_beep()

        if data_matrix := value.get(STR_DATA_MATRIX):
            self._model.data_matrix = data_matrix
            self.display_result(value)

    def display_result(self, value):
        msg = ''
        if self.check_previous_process(value):
            msg += value.get(STR_FUN)
        else:
            for process in PROCESS_NAMES_WITHOUT_AIR_LEAK:
                if not (result := value.get(process)):
                    result = STR_MISS
                if result not in PROCESS_OK_RESULTS:
                    if msg:
                        msg += '\n'
                    msg += f"{PROCESS_FULL_NAMES[process]} : {result}"
        self._model.result = msg or STR_NG

    def check_previous_process(self, value):
        return not any(
            previous_process not in value
            or value.get(previous_process)
            not in PROCESS_OK_RESULTS
            for previous_process in PROCESS_NAMES_WITHOUT_AIR_LEAK
        )

    def right_clicked(self):
        self.close_signal.emit()


class ReleaseProcessModel(BasicModel):
    nfc_changed = Signal(str)
    nfc_connection_changed = Signal(str)

    result_changed = Signal(str)
    result_font_size_changed = Signal(int)
    result_font_color_changed = Signal(str)
    result_background_color_changed = Signal(str)

    @property
    def result(self):
        return self._result

    @result.setter
    def result(self, value):
        self._result = value
        if value in [STR_A, STR_B, STR_C]:
            self.result_font_size = RELEASE_GRADE_FONT_SIZE
            self.result_background_color = BACK_GROUND_COLOR
            self.result_font_color = grade_colors[value]
        else:
            self.result_font_color = WHITE
            self.result_font_size = RELEASE_RESULT_FONT_SIZE
            self.result_background_color = RED
        self.result_changed.emit(value)

    @property
    def result_font_size(self):
        return self._result_font_size

    @result_font_size.setter
    def result_font_size(self, value):
        self._result_font_size = value
        self.result_font_size_changed.emit(value)

    @property
    def result_font_color(self):
        return self._result_font_color

    @result_font_color.setter
    def result_font_color(self, value):
        self._result_font_color = value
        self.result_font_color_changed.emit(value)

    @property
    def result_background_color(self):
        return self._result_background_color

    @result_background_color.setter
    def result_background_color(self, value):
        self._result_background_color = value
        self.result_background_color_changed.emit(value)

    @property
    def nfcs(self):
        return self._nfc

    @nfcs.setter
    def nfcs(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if STR_NFC in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break


if __name__ == '__main__':
    app = ReleaseProcess(sys.argv)
    sys.exit(app.exec_())
