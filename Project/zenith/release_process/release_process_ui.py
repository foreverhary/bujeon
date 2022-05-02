from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QGroupBox, QTextBrowser

from process_package.PyQtCustomComponent import Label


class CustomLabel(Label):
    def __init__(self, txt=''):
        super(CustomLabel, self).__init__(txt)
        self.setFixedWidth(300)


class ReleaseProcessUI(QWidget):
    def __init__(self):
        super(ReleaseProcessUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(dm_groupbox := QGroupBox('DM'))
        dm_groupbox.setLayout(dm_layout := QVBoxLayout())
        dm_layout.addWidget(dm_input_label := CustomLabel())

        layout.addWidget(result_input_label := QTextBrowser())
        self.dm_input_label = dm_input_label
        self.result_input_label = result_input_label

