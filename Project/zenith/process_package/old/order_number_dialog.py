import sys

from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import QApplication

from process_package.component.CustomComponent import style_sheet_setting
from process_package.tools.Config import set_order_number
from process_package.tools.mssql_connect import select_order_number_with_date_material_model
from process_package.old.order_number_dialog_ui import OrderNumberDialogUI


class OderNumberDialog(OrderNumberDialogUI):
    orderNumberSendSignal = Signal()

    def __init__(self):
        super(OderNumberDialog, self).__init__()

        self.df = None

        self.connect_event()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def connect_event(self):
        # button event connect
        self.search_button.clicked.connect(self.get_db_button_clicked)
        self.saveButton.clicked.connect(self.save_button_clicked)
        self.cancelButton.clicked.connect(self.cancel_button_clicked)

        # combobox event connect
        self.orderNumberComboBox.currentIndexChanged.connect(self.order_number_changed)

    def save_button_clicked(self):
        set_order_number(self.orderNumberEdit.text())
        self.orderNumberSendSignal.emit()
        self.close()

    def cancel_button_clicked(self):
        self.df = None
        self.close()

    def get_db_button_clicked(self):
        date = self.calendar.date().getDate()
        date = list(map(lambda x: f"{x}".zfill(2), date))
        date = ''.join(date)
        try:
            self.df = select_order_number_with_date_material_model(date,
                                                                   self.order_keyword.text(),
                                                                   self.material_keyword.text(),
                                                                   self.model_keyword.text())

            self.orderNumberComboBox.clear()

            self.orderNumberComboBox.addItems([row[0] for row in self.df])
        except Exception as e:
            print(e)

    def order_number_changed(self):
        index = self.orderNumberComboBox.currentIndex()
        order_number = self.orderNumberComboBox.currentText()
        self.orderNumberEdit.setText(self.df[index][0])
        try:
            self.material.setText(self.df[index][1])
            self.model.setText(self.df[index][2])
        except IndexError:
            pass

    def show_modal(self):
        return super().exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = OderNumberDialog()
    ex.show()
    sys.exit(app.exec_())
