from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QDateEdit
from PyQt5.QtCore import Qt, QDate

from process_package.defined_variable_function import DEFAULT_FONT_SIZE


class Button(QPushButton):
    def __init__(self, txt, font_size=DEFAULT_FONT_SIZE):
        super(Button, self).__init__(txt)
        self.font_size = font_size
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;')

    def keyPressEvent(self, event):
        pass

    def set_clicked(self, color):
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;'
                           f'background-color: {color}')


class LineEdit(QLineEdit):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE):
        super(LineEdit, self).__init__(txt)
        self.setMinimumHeight(50)
        self.font_size = font_size
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;')
        # self.setDisabled(True)

    def set_background_color(self, color=None):
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;'
                           f'background-color: {color}')


class ComboBox(QComboBox):
    def __init__(self, font_size=DEFAULT_FONT_SIZE):
        super(ComboBox, self).__init__()
        self.setMinimumHeight(50)
        self.font_size = font_size
        self.setStyleSheet(f'font-size: {self.font_size}px;')

    def set_text_color(self, color):
        self.setStyleSheet('font-size: 35px;'
                           f'color: {color}')

    def keyPressEvent(self, event):
        pass


class Label(QLabel):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE):
        super(Label, self).__init__(txt)
        self.fontSize = font_size
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;')

    def keyPressEvent(self, event):
        pass

    def set_text_property(self, size=None, color='white'):
        self.fontSize = size or self.fontSize
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;'
                           f'color: {color}')


class LeftAlignLabel(Label):
    def __init__(self, text):
        super(LeftAlignLabel, self).__init__(text)
        self.setMinimumHeight(50)
        self.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class RightAlignLabel(Label):
    def __init__(self, text):
        super(RightAlignLabel, self).__init__(text)
        self.setMinimumHeight(50)
        self.setAlignment(Qt.AlignRight | Qt.AlignVCenter)


class DateEdit(QDateEdit):
    def __init__(self, font_size=DEFAULT_FONT_SIZE):
        super(DateEdit, self).__init__(calendarPopup=True)
        self.setMinimumHeight(50)
        self.font_size = font_size
        self.setStyleSheet(f'font-size: {self.font_size}px;')
        self.calendarWidget().setSelectedDate(QDate.currentDate())
        self._today_button = Button(self.tr("Today"))
        self._today_button.clicked.connect(self._update_today)
        self.calendarWidget().layout().addWidget(self._today_button)
        self.lineEdit().setDisabled(True)

    def _update_today(self):
        self._today_button.clearFocus()
        today = QDate.currentDate()
        self.calendarWidget().setSelectedDate(today)
