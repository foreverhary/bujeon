from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox

from audio_bus.AudioBusConfig import AudioBusConfig
from process_package.Config import Config
from process_package.PyQtCustomComponent import Label
from process_package.mssql_dialog import MSSQLDialog


class AudioBusUI(QWidget):
    def __init__(self):
        super(AudioBusUI, self).__init__()

        layout = QVBoxLayout()

        # previous process
        previous_process_groupbox = QGroupBox()
        previous_process_groupbox.setTitle('PREVIOUS PROCESS')

        self.previous_process_label = Label('')

        previous_layout = QVBoxLayout()
        previous_layout.addWidget(self.previous_process_label)

        previous_process_groupbox.setLayout(previous_layout)

        # grade
        grade_groupbox = QGroupBox()
        grade_groupbox.setTitle('GRADE')
        grade_layout = QVBoxLayout()
        self.grade_label = Label('')
        self.grade_label.setMinimumWidth(600)
        grade_layout.addWidget(self.grade_label)
        grade_groupbox.setLayout(grade_layout)

        # process result
        process_groupbox = QGroupBox()
        process_groupbox.setTitle('PROCESS RESULT')


        self.status_label = Label('')
        self.status_label.setMinimumWidth(600)
        self.status_label.set_text_property(color='red')

        process_layout = QVBoxLayout()
        process_layout.addWidget(self.status_label)
        process_groupbox.setLayout(process_layout)

        layout.addWidget(previous_process_groupbox)
        layout.addWidget(grade_groupbox)
        layout.addWidget(process_groupbox)
        self.setLayout(layout)
        self.setWindowTitle('Audio Bus')

        # config
        self.config = Config('config.ini')

        # sub windows
        self.audio_bus_config_window = AudioBusConfig()
        self.mssql_config_window = MSSQLDialog()

    def mousePressEvent(self, e):
        if e.buttons() & Qt.RightButton:
            self.audio_bus_config_window.showModal()
        if e.buttons() & Qt.MidButton:
            self.mssql_config_window.show_modal()
        if e.buttons() & Qt.LeftButton:
            self.m_flag=True
            self.m_Position=e.globalPos()-self.pos()
            e.accept()
            self.setCursor((QCursor(Qt.OpenHandCursor)))

    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:
            self.move(QMouseEvent.globalPos()-self.m_Position)
            QMouseEvent.accept()

    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag=False
        self.setCursor(QCursor(Qt.ArrowCursor))
