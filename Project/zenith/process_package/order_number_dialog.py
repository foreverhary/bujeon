import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from process_package.Config import set_order_number
from process_package.defined_variable_function import style_sheet_setting
from process_package.mssql_connect import select_order_number_with_date_material_model
from process_package.order_number_dialog_ui import OrderNumberDialogUI


class OderNumberDialog(OrderNumberDialogUI):
    orderNumberSendSignal = pyqtSignal()

    def __init__(self):
        super(OderNumberDialog, self).__init__()

        self.df = None

        self.connect_event()

    def connect_event(self):
        # button event connect
        self.search_button.clicked.connect(self.get_db_button_clicked)
        self.saveButton.clicked.connect(self.save_button_clicked)
        self.cancelButton.clicked.connect(self.cancel_button_clicked)

        # combobox event connect
        self.orderNumberComboBox.currentIndexChanged.connect(self.order_number_changed)

    def save_button_clicked(self):
        set_order_number(self.orderNumberComboBox.currentText())
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

            self.orderNumberComboBox.addItems(self.df.order_number.unique())
        except Exception as e:
            print(e)

    def order_number_changed(self):
        order_number = self.orderNumberComboBox.currentText()
        try:
            self.material.setText(self.df[self.df.order_number == order_number].material_code.iloc[0])
            self.model.setText(self.df[self.df.order_number == order_number].model_name.iloc[0])
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
