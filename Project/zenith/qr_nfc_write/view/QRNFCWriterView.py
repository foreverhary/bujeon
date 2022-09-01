from PySide2.QtWidgets import QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.component.CustomComponent import Widget, LabelNFC, LabelTimerClean, style_sheet_setting, \
    window_center
from process_package.component.CustomMixComponent import GroupLabel, NetworkStatusGroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.component.PreviousCheckGroupLabel import PreviousCheckerGroupLabelAirTouch
from process_package.resource.size import MATCHING_DATA_MATRIX_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, \
    MATCHING_STATUS_FONT_SIZE, \
    MATCHING_STATUS_MAXIMUM_HEIGHT, NFC_FIXED_HEIGHT
from process_package.resource.string import STR_DATA_MATRIX, STR_STATUS, STR_NFC, STR_PREVIOUS_PROCESS, STR_MIC, \
    STR_NETWORK
from process_package.screen.SplashScreen import SplashScreen


class QRNFCWriterView(Widget):
    def __init__(self, app):
        super(QRNFCWriterView, self).__init__()
        self.app = app
        self.setObjectName("Widget")
        self._model, self._control = self.app._model, self.app._control
        self.setup_ui()
        self.setup_event()

    def setup_ui(self):

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(network_label := NetworkStatusGroupLabel(STR_NETWORK))
        layout.addWidget(nfc := NFCComponent(STR_NFC))
        layout.addWidget(
                previous := PreviousCheckerGroupLabelAirTouch(STR_PREVIOUS_PROCESS,
                                                              label=LabelTimerClean(
                                                                      is_clean=True,
                                                                      clean_time=1000),
                                                              process_name=STR_MIC
                                                              ))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, label=LabelNFC()))
        status = GroupLabel(STR_STATUS)
        network_label.setMaximumHeight(NFC_FIXED_HEIGHT)
        nfc.setMaximumHeight(NFC_FIXED_HEIGHT)
        data_matrix.label.set_font_size(MATCHING_DATA_MATRIX_FONT_SIZE)
        data_matrix.label.setMinimumWidth(MATCHING_DATA_MATRIX_MINIMUM_WIDTH)
        status.label.set_font_size(MATCHING_STATUS_FONT_SIZE)
        status.setMaximumHeight(MATCHING_STATUS_MAXIMUM_HEIGHT)

        self.nfc = nfc
        self.previous = previous
        self.data_matrix = data_matrix.label
        self.status = status.label

    def setup_event(self):
        # connect widgets to controller
        self._control.nfc_write.connect(self.nfc.write)
        self._control.nfc_write_bytes.connect(self.nfc.write)

        # listen for model event signals
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        self._model.previous_result_changed.connect(self.previous.check_previous)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_background_color_changed.connect(self.data_matrix.set_background_color)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

    def load_nfc(self):
        self.nfc.close_force()
        self.app.setStyleSheet("QWidget{};")
        self.hide()
        self.load_nfc_window = SplashScreen("QR MATCHING")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        db_action = menu.addAction('DB Setting')
        nfc_action = menu.addAction('Load NFC Port')

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == nfc_action:
            self.load_nfc()
        elif action == db_action:
            MSSqlDialog()

    def show_main_window(self, nfcs):
        style_sheet_setting(self.app)
        for port, nfc in nfcs.items():
            if STR_NFC in nfc:
                self.nfc.set_port(port)
                break

        self.show()

        window_center(self)
        self.load_nfc_window.close()
