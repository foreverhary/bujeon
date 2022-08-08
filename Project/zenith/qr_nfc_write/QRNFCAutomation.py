import sys

from PySide2.QtWidgets import QApplication, QMenu

from process_package.MSSqlDialog import MSSqlDialog
from process_package.OrderNumberDialog import OrderNumberDialog
from process_package.check_string import check_dm
from process_package.component.CustomMixComponent import GroupLabel
from process_package.resource.string import STR_ORDER_NUMBER
from process_package.screen.SplashScreen import SplashScreen
from process_package.component.CustomComponent import style_sheet_setting, window_center, get_time
from process_package.tools.Config import get_order_number
from qr_nfc_write.control.QRNFCWriterControl import QRNFCWriterControl
from qr_nfc_write.model.QRNFCWriterModel import QRNFCWriterModel
from qr_nfc_write.view.QRNFCWriterView import QRNFCWriterView

QR_MATCHING_AUTOMATION_VERSION = 'v0.1'


class QRNFCAutomation(QApplication):
    def __init__(self, sys_argv):
        super(QRNFCAutomation, self).__init__(sys_argv)
        self._model = QRNFCAutomationModel()
        self._control = QRNFCAutomationControl(self._model)
        self._view = QRNFCAutomationView(self._model, self._control)
        self._view.order.setText(get_order_number())
        self._view.setWindowTitle(f"QR Matching {QR_MATCHING_AUTOMATION_VERSION}")
        self.load_nfc_window = SplashScreen("QR MATCHING")
        self.load_nfc_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfcs):
        style_sheet_setting(self)
        self._model.nfc = nfcs
        self._view.show()
        window_center(self._view)
        self.load_nfc_window.close()


class QRNFCAutomationModel(QRNFCWriterModel):
    pass


class QRNFCAutomationControl(QRNFCWriterControl):

    def input_keyboard_line(self, value):
        if self.keyboard_disabled:
            return
        self._model.data_matrix = data_matrix if (data_matrix := check_dm(value)) else ''

        if not self._model.data_matrix:
            return

        self._mssql.start_query_thread(
                self._mssql.insert_pprh,
                self._model.data_matrix,
                get_order_number(),
                get_time()
        )


class QRNFCAutomationView(QRNFCWriterView):
    def __init__(self, *args):
        super(QRNFCAutomationView, self).__init__(*args)
        self._model, self._control = args

        # UI
        self.layout().insertWidget(1, order := GroupLabel(title=STR_ORDER_NUMBER))
        self.previous.setParent(None)
        self.order = order

    def contextMenuEvent(self, e):
        menu = QMenu(self)

        order_action = menu.addAction('Order Number Setting')
        db_action = menu.addAction('DB Setting')

        action = menu.exec_(self.mapToGlobal(e.pos()))
        if action == db_action:
            MSSqlDialog()
        elif action == order_action:
            OrderNumberDialog(self.order)


if __name__ == '__main__':
    app = QRNFCAutomation(sys.argv)
    sys.exit(app.exec_())
