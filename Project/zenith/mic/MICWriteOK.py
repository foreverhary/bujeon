import sys

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtWidgets import QApplication, QVBoxLayout

from process_package.Views.CustomComponent import style_sheet_setting, Widget
from process_package.Views.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.resource.color import LIGHT_SKY_BLUE
from process_package.resource.string import STR_DATA_MATRIX, STR_AIR, STR_OK, STR_MIC, STR_AIR_LEAK, STR_NFCIN
from process_package.screen.SplashScreen import SplashScreen
from process_package.tools.CommonFunction import write_beep, logger


class MICWriteOKModel(QObject):
    data_matrix_changed = Signal(str)
    data_matrix_background_changed = Signal(str)
    nfc_changed = Signal(str)

    def __init__(self):
        super(MICWriteOKModel, self).__init__()
        self.data_matrix = ''

    @property
    def data_matrix(self):
        return self._data_matrix

    @data_matrix.setter
    def data_matrix(self, value):
        self._data_matrix = value
        self.data_matrix_changed.emit(self._data_matrix)

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

    @Slot(dict)
    def receive_nfc_data(self, value):
        self._model.data_matrix_background = LIGHT_SKY_BLUE
        if self.delay_write_count:
            self.delay_write_count -= 1
            return

        if not value.get(STR_DATA_MATRIX):
            return

        if value.get(STR_AIR) and STR_OK == value.get(STR_MIC):
            write_beep()
            self._model.data_matrix = f"{value.get(STR_DATA_MATRIX)}\n" \
                                      f"{STR_AIR_LEAK}:{value.get(STR_AIR)}\n" \
                                      f"{STR_MIC}:{value.get(STR_MIC)}"
        else:
            self._model.tmp_data_matrix = value.get(STR_DATA_MATRIX)
            self.nfc_write.emit(
                f"{value.get(STR_DATA_MATRIX)},{STR_AIR}:{value.get(STR_AIR) or STR_OK},{STR_MIC}:{STR_OK}")
            self.delay_write_count = 2


class MICWriteOKView(Widget):
    def __init__(self, *args):
        super(MICWriteOKView, self).__init__(*args)
        self._model, self._control = args
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent())
        layout.addWidget(
            data_matrix := GroupLabel(title=STR_DATA_MATRIX, font_size=50, is_nfc=True, is_clean=True, clean_time=2000))

        nfc.setFixedHeight(70)
        data_matrix.setMinimumSize(420, 230)

        self.data_matrix = data_matrix.label

        nfc.nfc_data_out.connect(self._control.receive_nfc_data)
        self._control.nfc_write.connect(nfc.write)

        self._model.nfc_changed.connect(nfc.set_port)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_background_changed.connect(self.data_matrix.set_background_color)


class MICWriteOK(QApplication):
    def __init__(self, sys_argv):
        super(MICWriteOK, self).__init__(sys_argv)
        self._model = MICWriteOKModel()
        self._control = MICWriteOKControl(self._model)
        self._view = MICWriteOKView(self._model, self._control)
        self.load_nfc_window = SplashScreen("MIC Writer")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        self.load_nfc_window.close()


if __name__ == '__main__':
    app = MICWriteOK(sys.argv)
    sys.exit(app.exec_())
