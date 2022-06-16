from packages.views.CustomComponent import Widget


class Touch(Widget):
    def __init__(self):
        super(Touch, self).__init__()

        # component
        self.status = None
        self.machine_result = None
        self.data_matrix = None
        self.order_number = None
        self.comport = None

        self.setup_ui()

        self.setup_program()

        self.show()

    def setup_program(self):
        self.comport.setup_serial(
            get_config_value(CONFIG_FILE_NAME, COMPORT_SECTION, MACHINE_COMPORT_1),
            baudrate=BAUDRATE_115200,
            serial_name=TOUCH
        )

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(comport_group := QGroupBox(MACHINE_COMPORT))
        comport_group.setLayout(comport := HBoxSerial())

        layout.addWidget(order_number := GroupLabel(title=ORDER_NUMBER))
        layout.addWidget(data_matrix := GroupLabel(title=DATA_MATRIX, font_size=TOUCH_DATA_MATRIX_FONT_SIZE))
        layout.addWidget(machine_result := GroupLabel(title=MACHINE_RESULT, font_size=TOUCH_MACHINE_RESULT_FONT_SIZE))
        layout.addWidget(status := GroupLabel(title=STATUS))

        comport_group.setMaximumHeight(TOUCH_COMPORT_MAXIMUM_HEIGHT)
        order_number.setMaximumHeight(TOUCH_ORDER_MAXIMUM_HEIGHT)
        data_matrix.setMaximumHeight(TOUCH_DATA_MATRIX_MAXIMUM_HEIGHT)
        status.setMaximumHeight(TOUCH_STATUS_MAXIMUM_HEIGHT)
        machine_result.label.setMinimumWidth(TOUCH_MACHINE_MINIMUM_WIDTH)

        self.comport = comport
        self.order_number = order_number
        self.data_matrix = data_matrix
        self.machine_result = machine_result
        self.status = status

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.RightButton:
            print("Right")
        if e.buttons() & Qt.MidButton:
            print("middle")