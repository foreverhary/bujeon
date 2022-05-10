from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox

from process_package.PyQtCustomComponent import Button, ComboBox, LeftAlignLabel, Label, LineEdit
from process_package.defined_serial_port import ports

search_args_size = 380


class AudioBusConfigUI(QDialog):
    """
    오더번호 및 공정 순서 DB 입력을 위한 설정 창
    설정 완료 시 Config에 저장 후 실제 DM 값 업데이트 시 Config 값 참조 하여 사용함
    """

    def __init__(self):
        super(AudioBusConfigUI, self).__init__()
        self.setWindowTitle('Audio Bus Config')

        layout = QVBoxLayout()

        # main groupbox
        main_config_box = QGroupBox("Main Config")

        # main Label
        comport_label = LeftAlignLabel("QR Port")
        grade_file_path = LeftAlignLabel("Grade Path")
        result_file_path = LeftAlignLabel("Result Path")

        # Main Config
        self.comport_combobox = ComboBox()
        self.comport_combobox.addItems(ports)
        self.grade_path = Label('')
        self.summary_path = Label('')
        self.summary_path.setMinimumWidth(search_args_size)

        # Main Config Button
        self.comport_connect_button = Button('Connect')
        self.grade_path_button = Button('...')
        self.result_path_button = Button('...')

        # Main Setting Layout
        main_config = QGridLayout()
        main_config.addWidget(comport_label, 0, 0)
        main_config.addWidget(grade_file_path, 1, 0)
        main_config.addWidget(result_file_path, 2, 0)
        main_config.addWidget(self.comport_combobox, 0, 1)
        main_config.addWidget(self.grade_path, 1, 1)
        main_config.addWidget(self.summary_path, 2, 1)
        main_config.addWidget(self.comport_connect_button, 0, 2)
        main_config.addWidget(self.grade_path_button, 1, 2)
        main_config.addWidget(self.result_path_button, 2, 2)

        # disble component
        comport_label.setDisabled(True)
        self.comport_combobox.setDisabled(True)
        self.comport_connect_button.setDisabled(True)

        main_config_box.setLayout(main_config)

        # Result
        grade_box = QGroupBox("Grade Config")

        # Result Label
        grade_a_label = LeftAlignLabel('A Grade')
        grade_b_label = LeftAlignLabel('B Grade')
        grade_c_label = LeftAlignLabel('C Grade')

        # Result Widget
        self.grade_a_min = LineEdit()
        self.grade_a_max = LineEdit()
        self.grade_b_min = LineEdit()
        self.grade_b_max = LineEdit()
        self.grade_c_min = LineEdit()
        self.grade_c_max = LineEdit()

        buttonLayout = QHBoxLayout()
        self.saveButton = Button('SAVE')
        self.saveButton.setMinimumWidth(150)
        self.cancelButton = Button('CANCEL')
        self.cancelButton.setMinimumWidth(150)
        buttonLayout.addWidget(self.saveButton)
        buttonLayout.addWidget(self.cancelButton)

        # Result Layout
        setting_layout = QGridLayout()
        setting_layout.addWidget(grade_a_label, 0, 0)
        setting_layout.addWidget(grade_b_label, 1, 0)
        setting_layout.addWidget(grade_c_label, 2, 0)
        setting_layout.addWidget(self.grade_a_min, 0, 1)
        middle_wave = Label(' ~ ')
        setting_layout.addWidget(middle_wave, 0, 2)
        setting_layout.addWidget(self.grade_a_max, 0, 3)
        setting_layout.addWidget(self.grade_b_min, 1, 1)
        middle_wave = Label(' ~ ')
        setting_layout.addWidget(middle_wave, 1, 2)
        setting_layout.addWidget(self.grade_b_max, 1, 3)
        setting_layout.addWidget(self.grade_c_min, 2, 1)
        middle_wave = Label(' ~ ')
        setting_layout.addWidget(middle_wave, 2, 2)
        setting_layout.addWidget(self.grade_c_max, 2, 3)

        grade_box.setLayout(setting_layout)

        input_layout = QHBoxLayout()
        input_layout.addWidget(main_config_box)
        input_layout.addWidget(grade_box)

        layout.addLayout(input_layout)
        layout.addLayout(buttonLayout)

        self.setLayout(layout)
