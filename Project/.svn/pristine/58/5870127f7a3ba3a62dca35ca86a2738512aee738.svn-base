from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout


class QRCreateUI(QWidget):
    def __init__(self):
        super(QRCreateUI, self).__init__()

        self.textInput = QLineEdit()
        self.createButton = QPushButton("생성")

        topLayout = QHBoxLayout()
        topLayout.addWidget(self.textInput)
        topLayout.addWidget(self.createButton)

        mainLayout = QVBoxLayout()

        mainLayout.addLayout(topLayout)

        self.qrLabel = QLabel()
        mainLayout.addWidget(self.qrLabel)

        self.setLayout(mainLayout)