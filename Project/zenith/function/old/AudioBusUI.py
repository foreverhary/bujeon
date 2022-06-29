from PySide2.QtWidgets import QVBoxLayout, QGroupBox

from process_package.component.CustomComponent import Label, Widget
from process_package.old.defined_variable_function import RED, PREVIOUS_PROCESS, GRADE, STATUS


class AudioBusUI(Widget):
    def __init__(self):
        super(AudioBusUI, self).__init__()

        layout = QVBoxLayout()

        # previous process
        previous_process_groupbox = QGroupBox()
        previous_process_groupbox.setTitle(PREVIOUS_PROCESS)

        self.previous_process_label = Label(is_clean=True)

        previous_layout = QVBoxLayout()
        previous_layout.addWidget(self.previous_process_label)

        previous_process_groupbox.setLayout(previous_layout)

        # grade
        grade_groupbox = QGroupBox()
        grade_groupbox.setTitle(GRADE)
        grade_layout = QVBoxLayout()
        self.grade_label = Label()
        self.grade_label.setMinimumWidth(600)
        grade_layout.addWidget(self.grade_label)
        grade_groupbox.setLayout(grade_layout)

        # write
        write_groupbox = QGroupBox('WRITE STATUS')
        self.write_label = Label(is_clean=True, clean_time=1500)

        write_status_layout = QVBoxLayout()
        write_status_layout.addWidget(self.write_label)
        write_groupbox.setLayout(write_status_layout)

        # status
        status_groupbox = QGroupBox(STATUS)
        status_groupbox.setTitle(STATUS)

        self.status_label = Label()
        self.status_label.setMinimumWidth(600)
        self.status_label.set_color(RED)

        status_layout = QVBoxLayout()
        status_layout.addWidget(self.status_label)
        status_groupbox.setLayout(status_layout)

        layout.addWidget(previous_process_groupbox)
        layout.addWidget(grade_groupbox)
        layout.addWidget(write_groupbox)
        layout.addWidget(status_groupbox)
        self.setLayout(layout)
        self.setWindowTitle('Audio Bus')
