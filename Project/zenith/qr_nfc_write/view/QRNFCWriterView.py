from PySide2.QtWidgets import QVBoxLayout, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.component.CustomComponent import Widget
from process_package.component.CustomMixComponent import GroupLabel
from process_package.component.NFCComponent import NFCComponent
from process_package.component.PreviousCheckGroupLabel import PreviousCheckerGroupLabelAirTouch
from process_package.resource.size import MATCHING_DATA_MATRIX_FONT_SIZE, MATCHING_DATA_MATRIX_MINIMUM_WIDTH, \
    MATCHING_STATUS_FONT_SIZE, \
    MATCHING_STATUS_MAXIMUM_HEIGHT, NFC_FIXED_HEIGHT
from process_package.resource.string import STR_DATA_MATRIX, STR_STATUS, STR_QR_MATCHING, \
    STR_NFC, STR_PREVIOUS_PROCESS, STR_MIC


class QRNFCWriterView(Widget):
    def __init__(self, *args):
        super(QRNFCWriterView, self).__init__()
        self._model, self._control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(nfc := NFCComponent(STR_NFC))
        # layout.addWidget(order := GroupLabel(STR_ORDER_NUMBER))
        layout.addWidget(
            previous := PreviousCheckerGroupLabelAirTouch(
                STR_PREVIOUS_PROCESS,
                is_clean=True,
                clean_time=3000,
                process_name=STR_MIC
            ))
        layout.addWidget(data_matrix := GroupLabel(title=STR_DATA_MATRIX, is_nfc=True))
        layout.addWidget(status := GroupLabel(STR_STATUS))

        nfc.setFixedHeight(NFC_FIXED_HEIGHT)
        # order.label.set_font_size(MATCHING_PREVIOUS_PROCESS_FONT_SIZE)
        # order.setMaximumHeight(MATCHING_PREVIOUS_PROCESS_MINIMUM_HEIGHT)
        data_matrix.label.set_font_size(MATCHING_DATA_MATRIX_FONT_SIZE)
        data_matrix.label.setMinimumWidth(MATCHING_DATA_MATRIX_MINIMUM_WIDTH)
        status.label.set_font_size(MATCHING_STATUS_FONT_SIZE)
        status.setMaximumHeight(MATCHING_STATUS_MAXIMUM_HEIGHT)

        self.nfc = nfc
        # self.order = order.label
        self.data_matrix = data_matrix.label
        self.status = status.label

        self.setWindowTitle(STR_QR_MATCHING)

        # connect widgets to controller
        self._control.nfc_write.connect(self.nfc.write)

        # listen for model event signals
        self.nfc.nfc_data_out.connect(self._control.receive_nfc_data)

        self._model.nfc_changed.connect(self.nfc.set_port)
        self._model.previous_result_changed.connect(previous.check_previous)
        # self._model.order_changed.connect(self.order.setText)
        self._model.data_matrix_changed.connect(self.data_matrix.setText)
        self._model.data_matrix_background_color_changed.connect(self.data_matrix.set_background_color)
        self._model.status_changed.connect(self.status.setText)
        self._model.status_color_changed.connect(self.status.set_color)

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == order_action:
            OrderNumberDialog(self._model)
        elif action == db_action:
            MSSqlDialog()
