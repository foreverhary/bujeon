from PySide2.QtCore import Signal, Qt
from PySide2.QtWidgets import QDialog, QHBoxLayout, QGroupBox, QGridLayout, QVBoxLayout

from process_package.component.CustomComponent import LeftAlignLabel, DateEdit, LineEdit, Button, ComboBox
from process_package.resource.size import ORDER_SEARCH_BOX_MINIMUM_WIDTH


class OrderNumberDialogView(QDialog):
    close_signal = Signal(str)

    def __init__(self, model, control):
        super(OrderNumberDialogView, self).__init__()
        self._model = model
        self._control = control

        # ui
        self.setWindowTitle('Order Setting')
        layout = QVBoxLayout(self)

        layout.addLayout(input_layout := QHBoxLayout())

        input_layout.addWidget(search_box := QGroupBox("Search"))
        search_box.setLayout(search_layout := QGridLayout())
        search_layout.addWidget(LeftAlignLabel("Date"), 0, 0)
        search_layout.addWidget(LeftAlignLabel("Order Keyword"), 1, 0)
        search_layout.addWidget(LeftAlignLabel("Material Keyword"), 2, 0)
        search_layout.addWidget(LeftAlignLabel("Model Keyword"), 3, 0)
        search_layout.addWidget(calendar := DateEdit(), 0, 1)
        search_layout.addWidget(order_keyword := LineEdit(), 1, 1)
        search_layout.addWidget(material_keyword := LineEdit(), 2, 1)
        search_layout.addWidget(model_keyword := LineEdit(), 3, 1)
        search_layout.addWidget(search_button := Button('Search'), 4, 1)

        input_layout.addWidget(result_box := QGroupBox("Result"))
        result_box.setLayout(setting_layout := QGridLayout())
        setting_layout.addWidget(LeftAlignLabel('Order Number'), 0, 0)
        setting_layout.addWidget(LeftAlignLabel('Material Code'), 1, 0)
        setting_layout.addWidget(LeftAlignLabel('Model Name'), 2, 0)
        setting_layout.addWidget(LeftAlignLabel('Order Temp'), 3, 0)
        setting_layout.addWidget(LeftAlignLabel('Order Edit'), 4, 0)
        setting_layout.addWidget(orderNumberComboBox := ComboBox(), 0, 1)
        setting_layout.addWidget(material := LeftAlignLabel(''), 1, 1)
        setting_layout.addWidget(model := LeftAlignLabel(''), 2, 1)
        setting_layout.addWidget(orderTempComboBox := ComboBox(), 3, 1)
        setting_layout.addWidget(orderNumberEdit := LineEdit(), 4, 1)

        layout.addLayout(button_layout := QHBoxLayout())
        button_layout.addWidget(saveButton := Button('SAVE'))
        button_layout.addWidget(cancelButton := Button('CANCEL'))

        calendar.setMinimumWidth(ORDER_SEARCH_BOX_MINIMUM_WIDTH)
        order_keyword.setMinimumWidth(ORDER_SEARCH_BOX_MINIMUM_WIDTH)
        material_keyword.setMinimumWidth(ORDER_SEARCH_BOX_MINIMUM_WIDTH)
        model_keyword.setMinimumWidth(ORDER_SEARCH_BOX_MINIMUM_WIDTH)

        orderNumberComboBox.setMinimumWidth(ORDER_SEARCH_BOX_MINIMUM_WIDTH)

        saveButton.setMinimumWidth(150)
        cancelButton.setMinimumWidth(150)

        orderTempComboBox.addItems(["Not Used", "Temp Left", "Temp Right"])

        self.calendar = calendar
        self.order_keyword = order_keyword
        self.material_keyword = material_keyword
        self.model_keyword = model_keyword
        self.search_button = search_button

        self.order_number_combo = orderNumberComboBox
        self.material = material
        self.model_name = model
        self.order_number_edit = orderNumberEdit

        self.saveButton = saveButton
        self.cancelButton = cancelButton

        self._control.change_date(self.calendar.date())

        # connect widgets to controller
        self.calendar.dateChanged.connect(self._control.change_date)
        self.order_keyword.textChanged.connect(self._control.change_order_keyword)
        self.material_keyword.textChanged.connect(self._control.change_material_keyword)
        self.model_keyword.textChanged.connect(self._control.change_model_keyword)

        self.order_number_combo.currentIndexChanged.connect(self._control.change_order_number_index)
        self.search_button.clicked.connect(self._control.get_order_list)
        orderTempComboBox.currentIndexChanged.connect(self._control.set_temp_order)

        self.order_number_edit.textChanged.connect(self._control.change_order_number)
        self.saveButton.clicked.connect(self.save)
        self.cancelButton.clicked.connect(self.close)

        # listen for model event signals
        self._model.order_number_list_changed.connect(self.order_number_combo.addItems)
        self._model.material_code_changed.connect(self.material.setText)
        self._model.model_name_changed.connect(self.model_name.setText)
        self._model.order_number_changed.connect(self.order_number_edit.setText)
        self._model.connection_changed.connect(self.search_button.setEnabled)
        self._model.temp_index_reset.connect(lambda: orderTempComboBox.setCurrentIndex(0))

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    def save(self):
        self._model.save()
        self.close_signal.emit(self._model.order_number)
        self.close()

    def showModal(self):
        return super().exec_()
