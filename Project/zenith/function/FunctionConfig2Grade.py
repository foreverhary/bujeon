from PySide2.QtCore import QObject, Signal, Slot
from PySide2.QtWidgets import QFileDialog

from function.control.FunctionConfigControl import FunctionConfigControl
from function.model.FunctionConfigModel import FunctionConfigModel
from function.view.FunctionConfigView import FunctionConfigView
from process_package.component.CustomComponent import LeftAlignLabel, LineEdit, Button
from process_package.resource.size import FUNCTION_PATH_LINE_EDIT_FONT_SIZE
from process_package.resource.string import GRADE_FILE_PATH_2
from process_package.tools.Config import set_config_audio_bus, get_config_audio_bus


class FunctionConfig2Grade(QObject):
    def __init__(self, parent_control):
        super(FunctionConfig2Grade, self).__init__()
        self._parent_control = parent_control
        self._model = FunctionConfig2GradeModel()
        self._control = FunctionConfig2GradeControl(self._model)
        self._view = FunctionConfig2GradeView(self._model, self._control, self._parent_control)
        self._model.begin_config_read()
        self._view.showModal()


class FunctionConfig2GradeView(FunctionConfigView):
    def __init__(self, *args):
        super(FunctionConfig2GradeView, self).__init__(*args)
        main_config = self.grade_path.parent().layout()
        main_config.addWidget(LeftAlignLabel("Grade 2 Path"), 1, 0)
        main_config.addWidget(LeftAlignLabel("Result Path"), 2, 0)
        main_config.addWidget(grade2_path := LineEdit(font_size=FUNCTION_PATH_LINE_EDIT_FONT_SIZE), 1, 1)
        main_config.addWidget(self.summary_path, 2, 1)
        main_config.addWidget(grade2_path_button := Button('..'), 1, 2)
        main_config.addWidget(summary_path_button := Button('..'), 2, 2)

        self.grade2_path = grade2_path

        grade2_path_button.clicked.connect(self._control.open_set_directory_grade2_path)
        summary_path_button.clicked.connect(self._control.open_set_directory_summary_path)
        grade2_path.textChanged.connect(self._control.set_grade2_path)

        self._model.grade2_path_changed.connect(self.grade2_path.setText)


class FunctionConfig2GradeControl(FunctionConfigControl):
    def __init__(self, model):
        super(FunctionConfig2GradeControl, self).__init__(model)

    @Slot(str)
    def set_grade2_path(self, value):
        self._model.grade2_path = value

    @Slot()
    def open_set_directory_grade2_path(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self._model.grade2_path)):
            self._model.grade2_path = path


class FunctionConfig2GradeModel(FunctionConfigModel):
    grade2_path_changed = Signal(str)

    def __init__(self):
        super(FunctionConfig2GradeModel, self).__init__()

    @property
    def grade2_path(self):
        return self._grade2_path

    @grade2_path.setter
    def grade2_path(self, value):
        self._grade2_path = value
        self.grade2_path_changed.emit(value)

    def save(self):
        super().save()
        set_config_audio_bus(GRADE_FILE_PATH_2, self.grade2_path)

    def begin_config_read(self):
        super().begin_config_read()
        self.grade2_path = get_config_audio_bus(GRADE_FILE_PATH_2)