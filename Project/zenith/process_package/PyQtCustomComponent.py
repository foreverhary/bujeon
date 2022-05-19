from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QDateEdit

from process_package.defined_variable_function import DEFAULT_FONT_SIZE, WHITE, RED, YELLOW, LIGHT_YELLOW


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
        self.color = WHITE
        self.timer_color = QTimer(self)
        self.timer_color.start(100)
        self.timer_color.timeout.connect(self.change_color_in_msec)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;')
        self.change_color_in_msec()

    def keyPressEvent(self, event):
        pass

    def set_text_property(self, size=None, color=WHITE):
        self.fontSize = size or self.fontSize
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;'
                           f'color: {color}')

    def change_color_in_msec(self):
        if self.color in (RED, LIGHT_YELLOW):
            self.color = RED if self.color == LIGHT_YELLOW else LIGHT_YELLOW
            self.set_text_property(color=self.color)

    def set_color(self, color):
        self.color = color
        self.set_text_property(color=self.color)


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
