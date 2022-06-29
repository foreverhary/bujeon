from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox

from process_package.component.CustomComponent import Button, DateEdit, ComboBox, LineEdit, LeftAlignLabel

search_args_size = 380


class OrderNumberDialogUI(QDialog):
    """
    오더번호 및 공정 순서 DB 입력을 위한 설정 창
    설정 완료 시 Config에 저장 후 실제 DM 값 업데이트 시 Config 값 참조 하여 사용함
    """

    def __init__(self):
        super(OrderNumberDialogUI, self).__init__()
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
        setting_layout.addWidget(LeftAlignLabel('Order Edit'), 3, 0)
        setting_layout.addWidget(orderNumberComboBox := ComboBox(), 0, 1)
        setting_layout.addWidget(material := LeftAlignLabel(''), 1, 1)
        setting_layout.addWidget(model := LeftAlignLabel(''), 2, 1)
        setting_layout.addWidget(orderNumberEdit := LineEdit(), 3, 1)

        layout.addLayout(button_layout := QHBoxLayout())
        button_layout.addWidget(saveButton := Button('SAVE'))
        button_layout.addWidget(cancelButton := Button('CANCEL'))

        calendar.setMinimumWidth(search_args_size)
        order_keyword.setMinimumWidth(search_args_size)
        material_keyword.setMinimumWidth(search_args_size)
        model_keyword.setMinimumWidth(search_args_size)

        orderNumberComboBox.setMinimumWidth(search_args_size)

        saveButton.setMinimumWidth(150)
        cancelButton.setMinimumWidth(150)

        self.calendar = calendar
        self.order_keyword = order_keyword
        self.material_keyword = material_keyword
        self.model_keyword = model_keyword
        self.search_button = search_button

        self.orderNumberComboBox = orderNumberComboBox
        self.material = material
        self.model = model
        self.orderNumberEdit = orderNumberEdit

        self.saveButton = saveButton
        self.cancelButton = cancelButton
