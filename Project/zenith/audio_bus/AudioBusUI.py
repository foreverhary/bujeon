from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from process_package.PyQtCustomComponent import Label
from process_package.defined_variable_function import RED, PREVIOUS_PROCESS, GRADE, STATUS


class AudioBusUI(QWidget):
    def __init__(self):
        super(AudioBusUI, self).__init__()

        layout = QVBoxLayout()

        # previous process
        previous_process_groupbox = QGroupBox()
        previous_process_groupbox.setTitle(PREVIOUS_PROCESS)

        self.previous_process_label = Label('')

        previous_layout = QVBoxLayout()
        previous_layout.addWidget(self.previous_process_label)

        previous_process_groupbox.setLayout(previous_layout)

        # grade
        grade_groupbox = QGroupBox()
        grade_groupbox.setTitle(GRADE)
        grade_layout = QVBoxLayout()
        self.grade_label = Label('')
        self.grade_label.setMinimumWidth(600)
        grade_layout.addWidget(self.grade_label)
        grade_groupbox.setLayout(grade_layout)

        # process result
        process_groupbox = QGroupBox()
        process_groupbox.setTitle(STATUS)

        self.status_label = Label('')
        self.status_label.setMinimumWidth(600)
        self.status_label.set_color(RED)

        process_layout = QVBoxLayout()
        process_layout.addWidget(self.status_label)
        process_groupbox.setLayout(process_layout)

        layout.addWidget(previous_process_groupbox)
        layout.addWidget(grade_groupbox)
        layout.addWidget(process_groupbox)
        self.setLayout(layout)
        self.setWindowTitle('Audio Bus')
