from PyQt5.QtWidgets import QWidget, QGridLayout

from process_package.PyQtCustomComponent import Label


class CustomLabel(Label):
    def __init__(self, txt):
        super(CustomLabel, self).__init__(txt)
        self.setFixedWidth(300)


class ReleaseProcessUI(QWidget):
    def __init__(self):
        super(ReleaseProcessUI, self).__init__()

        mainLayout = QGridLayout()
        mainLayout.addWidget(CustomLabel('DM'), 0, 0)
        mainLayout.addWidget(CustomLabel(''), 0, 1)
        mainLayout.addWidget(CustomLabel('RESULT'), 0, 2)

        self.dmInputLabel = CustomLabel('')
        self.resultInputLabel = CustomLabel('')
        mainLayout.addWidget(self.dmInputLabel, 1, 0)
        mainLayout.addWidget(CustomLabel(''), 0, 1)
        mainLayout.addWidget(self.resultInputLabel, 1, 2)

        self.setLayout(mainLayout)
