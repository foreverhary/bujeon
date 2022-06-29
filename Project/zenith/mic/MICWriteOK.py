import sys

from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QVBoxLayout, QApplication

from process_package.component.CustomComponent import Widget, style_sheet_setting
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.color import LIGHT_SKY_BLUE, WHITE, GREEN
from process_package.resource.string import STR_AIR_LEAK, STR_AIR, STR_MIC, STR_DATA_MATRIX, STR_NFCIN, STR_OK, STR_NFC
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import logger, write_beep


class MICWriteOKView(Widget):
    def __init__(self):
        super(MICWriteOKView, self).__init__()
        self._model = MICWriteOKModel()
        self._control = MICWriteOKControl(self._model)

        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent())
        layout.addWidget(
            data_matrix := GroupLabel(title=STR_DATA_MATRIX, font_size=50, is_nfc=True))

        nfc.setFixedHeight(70)
        data_matrix.setMinimumSize(420, 230)
        self.nfc = nfc
        self.data_matrix = data_matrix.label

        nfc.nfc_data_out.connect(self._control.receive_nfc_data)
        self._control.nfc_write.connect(nfc.write)

        self._model.nfc_changed.connect(nfc.set_port)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_color_changed.connect(self.data_matrix.set_color)
        self._model.data_matrix_background_changed.connect(self.data_matrix.set_background_color)

        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def set_nfcs(self, nfcs):
        for port, nfc_name in nfcs.items():
            if STR_NFC in nfc_name:
                self.nfc.set_port(port)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self.set_nfcs(nfcs)
        self.show()
        self.load_nfc_window.close()


class MICWriteOKModel(QObject):
    data_matrix_changed = Signal(str)
    data_matrix_color_changed = Signal(str)
    data_matrix_background_changed = Signal(str)
    nfc_changed = Signal(str)

    def __init__(self):
        super(MICWriteOKModel, self).__init__()
        self.data_matrix_color = WHITE
        self.data_matrix = ''

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(self._data_matrix)
        self.data_matrix_color = GREEN if self.data_matrix_color == WHITE else WHITE
        logger.debug(self.data_matrix_color)

    @property
    def data_matrix_color(self):
        return self._data_matrix_color

    @data_matrix_color.setter
    def data_matrix_color(self, value):
        self._data_matrix_color = value
        self.data_matrix_color_changed.emit(value)

    @property
    def data_matrix_background(self):
        return self._data_matrix_background

    @data_matrix_background.setter
    def data_matrix_background(self, value):
        self._data_matrix_background = value
        self.data_matrix_background_changed.emit(value)

    @property
    def nfc(self):
        return self._nfc

    @nfc.setter
    def nfc(self, value):
        if not isinstance(value, dict):
            return
        self._nfc = None
        for port, nfc in value.items():
            logger.debug(f"{port}:{nfc}")
            if STR_NFCIN in nfc:
                self._nfc = port
                self.nfc_changed.emit(port)
                break


class MICWriteOKControl(QObject):
    nfc_write = Signal(str)

    def __init__(self, model):
        super(MICWriteOKControl, self).__init__()
        self._model = model

        self.delay_write_count = 0
        self.data_matrix = None

    @Slot(dict)
    def receive_nfc_data(self, value):
        self._model.data_matrix_background = LIGHT_SKY_BLUE
        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not (data_matrix := value.get(STR_DATA_MATRIX)):
            return

        if self.data_matrix == data_matrix:
            return

        if STR_OK != value.get(STR_MIC):
            self.nfc_write.emit(
                f"{value.get(STR_DATA_MATRIX)},{STR_AIR}:{value.get(STR_AIR) or STR_OK},{STR_MIC}:{STR_OK}")
            self.delay_write_count = 4
        else:
            self.data_matrix = data_matrix
            write_beep()
            self._model.data_matrix = f"{data_matrix}\n" \
                                      f"{STR_AIR_LEAK}:{value.get(STR_AIR)}\n" \
                                      f"{STR_MIC}:{value.get(STR_MIC)}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MICWriteOKView()
    sys.exit(app.exec_())
