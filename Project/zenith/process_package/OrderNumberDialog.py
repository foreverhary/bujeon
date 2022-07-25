import sys

from PySide2.QtCore import QObject, Slot, Signal
from PySide2.QtWidgets import QApplication

from process_package.component.CustomComponent import style_sheet_setting
from process_package.Views.OrderNumberDialogView import OrderNumberDialogView
from process_package.controllers.OrderNumberDialogControl import OrderNumberDialogControl
from process_package.models.OrderNumberDialogModel import OrderNumberDialogModel


class OrderNumberDialog(QObject):
    order_changed = Signal(str)

    def __init__(self, order):
        super(OrderNumberDialog, self).__init__()
        self._model = OrderNumberDialogModel()
        self._control = OrderNumberDialogControl(self._model)
        self._view = OrderNumberDialogView(self._model, self._control)
        self._model.read_order_number()

        self._view.close_signal.connect(order.setText)
        self._view.showModal()

    def close(self):
        self._view.close()

    def showModal(self):
        self._view.showModal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = OrderNumberDialog()
    ex.showModal()
    sys.exit(app.exec_())
