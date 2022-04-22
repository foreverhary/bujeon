from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox

from process_package.PyQtCustomComponent import Button, DateEdit, ComboBox, LineEdit, LeftAlignLabel

search_args_size = 380


class OrderNumberDialogUI(QDialog):
    """
    오더번호 및 공정 순서 DB 입력을 위한 설정 창
    설정 완료 시 Config에 저장 후 실제 DM 값 업데이트 시 Config 값 참조 하여 사용함
    """

    def __init__(self):
        super(OrderNumberDialogUI, self).__init__()
        self.setWindowTitle('Order Setting')

        layout = QVBoxLayout()

        # Search
        search_box = QGroupBox("Search")

        # Search Label
        calendar_label = LeftAlignLabel("Date")
        order_keyword_label = LeftAlignLabel("Order Keyword")
        material_keyword_label = LeftAlignLabel("Material Keyword")
        model_keyword_label = LeftAlignLabel("Model Keyword")

        # Search Value
        self.calendar = DateEdit()
        self.calendar.setMinimumWidth(search_args_size)
        self.order_keyword = LineEdit()
        self.order_keyword.setMinimumWidth(search_args_size)
        self.material_keyword = LineEdit()
        self.material_keyword.setMinimumWidth(search_args_size)
        self.model_keyword = LineEdit()
        self.model_keyword.setMinimumWidth(search_args_size)

        # Search Button
        self.search_button = Button('Search')

        # Search Layout
        search_layout = QGridLayout()
        search_layout.addWidget(calendar_label, 0, 0)
        search_layout.addWidget(order_keyword_label, 1, 0)
        search_layout.addWidget(material_keyword_label, 2, 0)
        search_layout.addWidget(model_keyword_label, 3, 0)
        search_layout.addWidget(self.calendar, 0, 1)
        search_layout.addWidget(self.order_keyword, 1, 1)
        search_layout.addWidget(self.material_keyword, 2, 1)
        search_layout.addWidget(self.model_keyword, 3, 1)
        search_layout.addWidget(self.search_button, 4, 1)

        search_box.setLayout(search_layout)

        # Result
        result_box = QGroupBox("Result")

        # Result Label
        order_label = LeftAlignLabel('Order Number')
        material_label = LeftAlignLabel('Material Code')
        model_label = LeftAlignLabel('Model Name')

        # Result Widget
        self.orderNumberComboBox = ComboBox()
        self.orderNumberComboBox.setMinimumWidth(search_args_size)
        self.material = LeftAlignLabel('')
        self.model = LeftAlignLabel('')

        button_layout = QHBoxLayout()
        self.saveButton = Button('SAVE')
        self.saveButton.setMinimumWidth(150)
        self.cancelButton = Button('CANCEL')
        self.cancelButton.setMinimumWidth(150)
        button_layout.addWidget(self.saveButton)
        button_layout.addWidget(self.cancelButton)

        # Result Layout
        setting_layout = QGridLayout()
        setting_layout.addWidget(order_label, 0, 0)
        setting_layout.addWidget(material_label, 1, 0)
        setting_layout.addWidget(model_label, 2, 0)
        setting_layout.addWidget(self.orderNumberComboBox, 0, 1)
        setting_layout.addWidget(self.material, 1, 1)
        setting_layout.addWidget(self.model, 2, 1)
        setting_layout.addLayout(button_layout, 3, 0, -1, 2)

        result_box.setLayout(setting_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(search_box)
        input_layout.addWidget(result_box)

        layout.addLayout(input_layout)
        layout.addLayout(button_layout)

        self.setLayout(layout)
