import sys

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication, QFileDialog

from AudioBusConfigUI import AudioBusConfigUI
from process_package.Config import Config, get_config_audio_bus, set_config_audio_bus
from process_package.defined_variable_function import *
from process_package.style.style import STYLE

PATH_MAX_LENGTH = 30


class AudioBusConfig(AudioBusConfigUI):
    close_signal = pyqtSignal()

    def __init__(self):
        super(AudioBusConfig, self).__init__()

        self.df = None

        # set component string
        self.grade = get_config_audio_bus(GRADE_FILE_PATH)
        self.summary = get_config_audio_bus(SUMMARY_FILE_PATH)
        self.grade_a_min.setText(str(get_config_audio_bus(A_GRADE_MIN)))
        self.grade_a_max.setText(str(get_config_audio_bus(A_GRADE_MAX)))
        self.grade_b_min.setText(str(get_config_audio_bus(B_GRADE_MIN)))
        self.grade_b_max.setText(str(get_config_audio_bus(B_GRADE_MAX)))
        self.grade_c_min.setText(str(get_config_audio_bus(C_GRADE_MIN)))
        self.grade_c_max.setText(str(get_config_audio_bus(C_GRADE_MAX)))

        # button event connect
        self.grade_path_button.clicked.connect(self.grade_path_clicked)
        self.result_path_button.clicked.connect(self.result_path_clicked)
        self.saveButton.clicked.connect(self.saveButtonClicked)
        self.cancelButton.clicked.connect(self.cancelButtonClicked)

    @property
    def grade(self):
        return self._grade_path

    @grade.setter
    def grade(self, path):
        if isinstance(path, str):
            self._grade_path = path
            self.grade_path.setText(self.path_max_display(path))

    @property
    def summary(self):
        return self._summary_path

    @summary.setter
    def summary(self, path):
        if isinstance(path, str):
            self._summary_path = path
            self.summary_path.setText(self.path_max_display(path))

    def grade_path_clicked(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self.grade)):
            self.grade = path

    def result_path_clicked(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self.summary)):
            self.summary = path

    def path_max_display(self, path):
        return path if len(path) < PATH_MAX_LENGTH else path[:PATH_MAX_LENGTH] + '...'

    def saveButtonClicked(self):
        set_config_audio_bus(GRADE_FILE_PATH, self.grade)
        set_config_audio_bus(SUMMARY_FILE_PATH, self.summary)
        set_config_audio_bus(A_GRADE_MIN, self.grade_a_min.text())
        set_config_audio_bus(A_GRADE_MAX, self.grade_a_max.text())
        set_config_audio_bus(B_GRADE_MIN, self.grade_b_min.text())
        set_config_audio_bus(B_GRADE_MAX, self.grade_b_max.text())
        set_config_audio_bus(C_GRADE_MIN, self.grade_c_min.text())
        set_config_audio_bus(C_GRADE_MAX, self.grade_c_max.text())

        self.close_signal.emit()
        self.close()

    def cancelButtonClicked(self):
        self.df = None
        self.close()

    def showModal(self):
        return super().exec_()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
    ex = AudioBusConfig(Config('config.ini'))
    ex.show()
    sys.exit(app.exec_())
