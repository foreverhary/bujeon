from PySide2.QtCore import QObject, Signal

from process_package.resource.string import GRADE_FILE_PATH, SUMMARY_FILE_PATH, A_GRADE_MIN, A_GRADE_MAX, B_GRADE_MIN, \
    B_GRADE_MAX, C_GRADE_MIN, C_GRADE_MAX
from process_package.tools.Config import get_config_audio_bus, set_config_audio_bus


class FunctionConfigModel(QObject):
    grade_path_changed = Signal(str)
    summary_path_changed = Signal(str)
    a_min_changed = Signal(str)
    a_max_changed = Signal(str)
    b_min_changed = Signal(str)
    b_max_changed = Signal(str)
    c_min_changed = Signal(str)
    c_max_changed = Signal(str)

    def __init__(self):
        super(FunctionConfigModel, self).__init__()

    @property
    def grade_path(self):
        return self._grade_path

    @grade_path.setter
    def grade_path(self, value):
        self._grade_path = value
        self.grade_path_changed.emit(value)

    @property
    def summary_path(self):
        return self._summary_path

    @summary_path.setter
    def summary_path(self, value):
        self._summary_path = value
        self.summary_path_changed.emit(value)

    @property
    def a_min(self):
        return self._a_min

    @a_min.setter
    def a_min(self, value):
        self._a_min = value
        self.a_min_changed.emit(value)

    @property
    def a_max(self):
        return self._a_max

    @a_max.setter
    def a_max(self, value):
        self._a_max = value
        self.a_max_changed.emit(value)

    @property
    def b_min(self):
        return self._b_min

    @b_min.setter
    def b_min(self, value):
        self._b_min = value
        self.b_min_changed.emit(value)

    @property
    def b_max(self):
        return self._b_max

    @b_max.setter
    def b_max(self, value):
        self._b_max = value
        self.b_max_changed.emit(value)

    @property
    def c_min(self):
        return self._c_min

    @c_min.setter
    def c_min(self, value):
        self._c_min = value
        self.c_min_changed.emit(value)

    @property
    def c_max(self):
        return self._c_max

    @c_max.setter
    def c_max(self, value):
        self._c_max = value
        self.c_max_changed.emit(value)

    def save(self):
        set_config_audio_bus(GRADE_FILE_PATH, self.grade_path)
        set_config_audio_bus(SUMMARY_FILE_PATH, self.summary_path)
        set_config_audio_bus(A_GRADE_MIN, self.a_min)
        set_config_audio_bus(A_GRADE_MAX, self.a_max)
        set_config_audio_bus(B_GRADE_MIN, self.b_min)
        set_config_audio_bus(B_GRADE_MAX, self.b_max)
        set_config_audio_bus(C_GRADE_MIN, self.c_min)
        set_config_audio_bus(C_GRADE_MAX, self.c_max)

    def begin_config_read(self):
        self.grade_path = get_config_audio_bus(GRADE_FILE_PATH)
        self.summary_path = get_config_audio_bus(SUMMARY_FILE_PATH)
        self.a_min = str(get_config_audio_bus(A_GRADE_MIN))
        self.a_max = str(get_config_audio_bus(A_GRADE_MAX))
        self.b_min = str(get_config_audio_bus(B_GRADE_MIN))
        self.b_max = str(get_config_audio_bus(B_GRADE_MAX))
        self.c_min = str(get_config_audio_bus(C_GRADE_MIN))
        self.c_max = str(get_config_audio_bus(C_GRADE_MAX))
