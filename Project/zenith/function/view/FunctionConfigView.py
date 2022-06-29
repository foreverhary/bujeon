from PySide2.QtCore import Slot, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QGridLayout

from process_package.component.CustomComponent import LeftAlignLabel, Label, Button, LineEdit
from process_package.resource.size import AUDIO_BUS_CONFIG_BUTTON_MIN_WIDTH, \
    AUDIO_BUS_PATH_LINE_EDIT_MIN_WIDTH, AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH, AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE, \
    AUDIO_BUS_PATH_LINE_EDIT_FONT_SIZE


class FunctionConfigView(QDialog):
    def __init__(self, *args):
        super(FunctionConfigView, self).__init__()
        self._model, self._control, self._parent_control = args

        # UI
        layout = QVBoxLayout(self)
        layout.addLayout(input_layout := QHBoxLayout())

        input_layout.addWidget(main_config_box := QGroupBox("Main Config"))
        main_config_box.setLayout(main_config := QGridLayout())
        main_config.addWidget(LeftAlignLabel("Grade Path"), 0, 0)
        main_config.addWidget(LeftAlignLabel("Result Path"), 1, 0)
        main_config.addWidget(grade_path := LineEdit(font_size=AUDIO_BUS_PATH_LINE_EDIT_FONT_SIZE), 0, 1)
        main_config.addWidget(summary_path := LineEdit(font_size=AUDIO_BUS_PATH_LINE_EDIT_FONT_SIZE), 1, 1)
        main_config.addWidget(grade_path_button := Button('..'), 0, 2)
        main_config.addWidget(summary_path_button := Button('..'), 1, 2)

        input_layout.addWidget(grade_box := QGroupBox("Grade Config"))
        grade_box.setLayout(setting_layout := QGridLayout())
        setting_layout.addWidget(LeftAlignLabel('A Grade'), 0, 0)
        setting_layout.addWidget(LeftAlignLabel('B Grade'), 1, 0)
        setting_layout.addWidget(LeftAlignLabel('C Grade'), 2, 0)
        setting_layout.addWidget(grade_a_min := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 0, 1)
        setting_layout.addWidget(Label(' ~ '), 0, 2)
        setting_layout.addWidget(grade_a_max := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 0, 3)
        setting_layout.addWidget(grade_b_min := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 1, 1)
        setting_layout.addWidget(Label(' ~ '), 1, 2)
        setting_layout.addWidget(grade_b_max := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 1, 3)
        setting_layout.addWidget(grade_c_min := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 2, 1)
        setting_layout.addWidget(Label(' ~ '), 2, 2)
        setting_layout.addWidget(grade_c_max := LineEdit(font_size=AUDIO_BUS_GRADE_LINE_EDIT_FONT_SIZE), 2, 3)

        layout.addLayout(buttonLayout := QHBoxLayout())
        buttonLayout.addWidget(saveButton := Button('SAVE'))
        buttonLayout.addWidget(cancelButton := Button('CANCEL'))

        grade_path.setMinimumWidth(AUDIO_BUS_PATH_LINE_EDIT_MIN_WIDTH)
        summary_path.setMinimumWidth(AUDIO_BUS_PATH_LINE_EDIT_MIN_WIDTH)
        grade_a_min.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)
        grade_a_max.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)
        grade_b_min.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)
        grade_b_max.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)
        grade_c_min.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)
        grade_c_max.setFixedWidth(AUDIO_BUS_CONFIG_GRADE_EDIT_FIXED_WIDTH)

        saveButton.setMinimumWidth(AUDIO_BUS_CONFIG_BUTTON_MIN_WIDTH)
        cancelButton.setMinimumWidth(AUDIO_BUS_CONFIG_BUTTON_MIN_WIDTH)

        self.grade_path = grade_path
        self.summary_path = summary_path

        self.grade_a_min = grade_a_min
        self.grade_a_max = grade_a_max
        self.grade_b_min = grade_b_min
        self.grade_b_max = grade_b_max
        self.grade_c_min = grade_c_min
        self.grade_c_max = grade_c_max

        # connect widgets to controller
        grade_path_button.clicked.connect(self._control.open_set_directory_grade_path)
        summary_path_button.clicked.connect(self._control.open_set_directory_summary_path)
        grade_path.textChanged.connect(self._control.set_grade_path)
        summary_path.textChanged.connect(self._control.set_summary_path)
        grade_a_min.textChanged.connect(self._control.set_a_min)
        grade_a_max.textChanged.connect(self._control.set_a_max)
        grade_b_min.textChanged.connect(self._control.set_b_min)
        grade_b_max.textChanged.connect(self._control.set_b_max)
        grade_c_min.textChanged.connect(self._control.set_c_min)
        grade_c_max.textChanged.connect(self._control.set_c_max)
        saveButton.clicked.connect(self.save)
        cancelButton.clicked.connect(self.close)

        # listen for model event signals
        self._model.grade_path_changed.connect(self.grade_path.setText)
        self._model.summary_path_changed.connect(self.summary_path.setText)
        self._model.a_min_changed.connect(self.grade_a_min.setText)
        self._model.a_max_changed.connect(self.grade_a_max.setText)
        self._model.b_min_changed.connect(self.grade_b_min.setText)
        self._model.b_max_changed.connect(self.grade_b_max.setText)
        self._model.c_min_changed.connect(self.grade_c_min.setText)
        self._model.c_max_changed.connect(self.grade_c_max.setText)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

    @Slot()
    def save(self):
        self._model.save()
        self.close()

    def showModal(self):
        return super().exec_()

    def closeEvent(self, e):
        self._parent_control.start_file_observe()