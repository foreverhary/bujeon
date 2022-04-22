from PyQt5.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    def __init__(self, text, font_size=None):
        super().__init__()
        buttonStyle = '''
        QPushButton:hover {border:1px solid #0078d7; background-color:#e5f1fb;}
        QPushButton:pressed {background-color:#a7c8e3}
        QPushButton {font-family:NaNum Gothic; border:1px solid #d6d7d8; background-color#f0f1f1}
        '''
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setText(text)
        self.setStyleSheet(buttonStyle)
        if font_size:
            self.setStyleSheet("QPushButton {" + f"font-size: {font_size}px;" + "}")
