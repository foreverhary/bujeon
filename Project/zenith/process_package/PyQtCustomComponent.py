from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QDateEdit

from process_package.defined_variable_function import DEFAULT_FONT_SIZE, WHITE, RED, YELLOW, LIGHT_YELLOW, \
    BACK_GROUND_COLOR


class Button(QPushButton):
    def __init__(self, txt, font_size=DEFAULT_FONT_SIZE):
        super(Button, self).__init__(txt)
        self.font_size = font_size
        self.background_color = WHITE
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;')

    def keyPressEvent(self, event):
        pass

    def set_clicked(self, color):
        self.background_color = color
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;'
                           f'background-color: {self.background_color}')


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
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, is_clean=False):
        super(Label, self).__init__(txt)
        self.fontSize = font_size
        self.is_clean = is_clean
        self.color = WHITE
        self.background_color = BACK_GROUND_COLOR
        self.timer_color = QTimer(self)
        self.timer_color.start(100)
        self.timer_color.timeout.connect(self.change_color_in_msec)

        self.timer_clean = QTimer(self)
        self.timer_clean.timeout.connect(self.clean)
        self.timer_clean.stop()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;')
        self.change_color_in_msec()

    def setText(self, txt):
        super().setText(txt)
        self.timer_clean.stop()
        if self.is_clean:
            self.timer_clean.start(2000)

    def clean(self):
        self.set_background_color()
        self.set_color(WHITE)
        self.clear()

    def set_background_color(self, color=BACK_GROUND_COLOR):
        self.background_color = color
        self.set_style_sheet()

    def keyPressEvent(self, event):
        pass

    def set_font_size(self, size=None):
        self.fontSize = size or self.fontSize
        self.set_style_sheet()

    def change_color_in_msec(self):
        if self.color in (RED, LIGHT_YELLOW):
            self.color = RED if self.color == LIGHT_YELLOW else LIGHT_YELLOW
            self.set_style_sheet()

    def set_style_sheet(self):
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;'
                           f'color: {self.color};'
                           f'background-color: {self.background_color}')

    def set_color(self, color):
        self.color = color
        self.set_style_sheet()


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
