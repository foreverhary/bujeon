import os.path

from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget

from process_package.PyQtCustomComponent import Label, LineEdit, Button


class RegisterUI(QWidget):
    def __init__(self):
        super(RegisterUI, self).__init__()

        self.aufnrButton = Button('AUFNR')
        self.aufnrLineEdit = LineEdit()
        self.aufnrLineEdit.setReadOnly(True)

        self.dmLabel = Label("DM")

        self.dmInput = LineEdit()
        self.dmInput.setReadOnly(True)

        self.jigLabel = Label("JIG")
        self.jigInput = LineEdit()
        self.jigInput.setReadOnly(True)

        topHLayout = QHBoxLayout()
        topHLayout.addWidget(self.aufnrButton)
        topHLayout.addWidget(self.aufnrLineEdit)
        topHLayout.addWidget(self.dmLabel)
        topHLayout.addWidget(self.dmInput)
        # topHLayout.addWidget(self.jigLabel)
        # topHLayout.addWidget(self.jigInput)

        self.resetQR = Label()
        self.resetQR.setPixmap(QPixmap(os.path.join('icon', 'RESET.png')))

        self.resetLabel = Label("RESET")
        bodyLeftLayout = QVBoxLayout()
        bodyLeftLayout.addWidget(self.resetQR)
        bodyLeftLayout.addWidget(self.resetLabel)

        self.registerQR = Label()
        self.registerQR.setPixmap(QPixmap(os.path.join('icon', 'REGISTER.png')))

        self.registerLabel = Label("Register")
        bodyRightLayout = QVBoxLayout()
        bodyRightLayout.addWidget(self.registerQR)
        bodyRightLayout.addWidget(self.registerLabel)

        bodyLayout = QHBoxLayout()
        bodyLayout.addLayout(bodyLeftLayout)
        bodyLayout.addLayout(bodyRightLayout)

        # layout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(topHLayout)
        mainLayout.addLayout(bodyLayout)
        self.setLayout(mainLayout)
