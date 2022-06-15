import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout

from packages.component.CustomComponent import Widget, style_sheet_setting, GroupLabel
from packages.variable.size import AUDIO_BUS_LABEL_MINIMUM_WIDTH
from packages.variable.string import PREVIOUS_PROCESS, GRADE, DATA_MATRIX, STATUS
from packages.variable.variables import logger


class AudioBus(Widget):
    def __init__(self):
        super(AudioBus, self).__init__()
        self.status = None
        self.data_matrix = None
        self.grade = None
        self.previous = None
        self.setup_ui()
        self.show()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(previous := GroupLabel(PREVIOUS_PROCESS))
        layout.addWidget(grade := GroupLabel(GRADE))
        layout.addWidget(data_matrix := GroupLabel(DATA_MATRIX))
        layout.addWidget(status := GroupLabel(STATUS))

        grade.label.setMinimumWidth(AUDIO_BUS_LABEL_MINIMUM_WIDTH)

        self.previous = previous
        self.grade = grade
        self.data_matrix = data_matrix
        self.status = status


if __name__ == '__main__':
    logger.info("audio bus start")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = AudioBus()
    sys.exit(app.exec())
