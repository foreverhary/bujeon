import time
from threading import Timer

import qdarkstyle
from PySide2.QtCore import Qt, QDate, QTimer, Signal, Slot
from PySide2.QtGui import QCursor, QFontDatabase, QFont
from PySide2.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QDateEdit, QWidget, QDesktopWidget, QMessageBox

from process_package.resource.color import WHITE, BACK_GROUND_COLOR, LIGHT_BLUE, RED, LIGHT_YELLOW, BLUE, LIGHT_SKY_BLUE
from process_package.resource.size import DEFAULT_FONT_SIZE
from process_package.resource.style import STYLE


class Widget(QWidget):
    right_clicked = Signal()
    mid_clicked = Signal()

    def __init__(self, *args):
        super(Widget, self).__init__()
        self.m_Position = None
        self.m_flag = False

    def mousePressEvent(self, e):
        if e.buttons() & Qt.MidButton:
            self._control.mid_clicked()
        if e.buttons() & Qt.LeftButton:
            self.m_flag = True
            self.m_Position = e.globalPos() - self.pos()
            e.accept()
            self.setCursor((QCursor(Qt.OpenHandCursor)))

    def mouseMoveEvent(self, e):
        if Qt.LeftButton and self.m_flag:
            self.move(e.globalPos() - self.m_Position)
            e.accept()

    def mouseReleaseEvent(self, e):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def mouseDoubleClickEvent(self, e):
        if e.buttons() & Qt.LeftButton:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()


class Button(QPushButton):
    def __init__(self, txt, font_size=DEFAULT_FONT_SIZE):
        super(Button, self).__init__(txt)
        self.font_size = font_size
        self.background_color = WHITE
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.font_size}px;')

    def keyPressEvent(self, event):
        pass

    def set_background_color(self, color):
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
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE):
        super(Label, self).__init__(txt)
        self.fontSize = font_size
        self.color = WHITE
        self.background_color = BACK_GROUND_COLOR

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;')

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

    def set_color(self, color):
        self.color = color
        self.set_style_sheet()

    def set_style_sheet(self):
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;'
                           f'color: {self.color};'
                           f'background-color: {self.background_color}')

    def setText(self, txt: str) -> None:
        super().setText(txt)
        if not txt:
            self.clean()
        if txt in ['OK', 'PASS']:
            self.set_background_color(LIGHT_SKY_BLUE)
        elif txt in ['NG', 'FAIL']:
            self.set_background_color(RED)


class LabelTimerClean(Label):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, is_clean=False, clean_time=2000):
        super(LabelTimerClean, self).__init__(txt, font_size=font_size)
        self.is_clean = is_clean
        self.clean_time = clean_time

        self.timer_clean = QTimer(self)
        self.timer_clean.timeout.connect(self.clean)
        self.timer_clean.stop()

    def setText(self, txt):
        super().setText(txt)
        self.timer_clean.stop()
        if self.is_clean:
            self.timer_clean.start(self.clean_time)


class LabelBlink(Label):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, blink_time=100):
        super(LabelBlink, self).__init__(txt, font_size)

        self.timer_color = QTimer(self)
        self.timer_color.start(blink_time)
        self.timer_color.timeout.connect(self.change_color_in_msec)

    def change_color_in_msec(self):
        if self.color in (RED, LIGHT_YELLOW):
            self.color = RED if self.color == LIGHT_YELLOW else LIGHT_YELLOW
            self.set_style_sheet()


class LabelNFC(LabelTimerClean):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, is_clean=False, clean_time=2000):
        super(LabelNFC, self).__init__(txt, font_size, is_clean, clean_time)

        self.timer_nfc_tag = QTimer(self)
        self.timer_nfc_tag.start(200)
        self.timer_nfc_tag.timeout.connect(self.blink_background)

    def blink_background(self):
        if self.background_color in [LIGHT_SKY_BLUE, BLUE]:
            self.set_background_color()

    def blink_text(self):
        tmp_text = self.text()
        self.clear()
        timer = Timer(0.1, self.setText, args=(tmp_text,))
        timer.daemon = True
        timer.start()


class LabelTirClean(QLabel):
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, is_clean=False, clean_time=2000):
        super(LabelTimerClean, self).__init__(txt, font_size)
        self.fontSize = font_size
        self.is_clean = is_clean
        self.color = WHITE
        self.background_color = BACK_GROUND_COLOR
        self.clean_time = clean_time
        self.timer_color = QTimer(self)
        self.timer_color.start(100)
        self.timer_color.timeout.connect(self.change_color_in_msec)

        self.timer_clean = QTimer(self)
        self.timer_clean.timeout.connect(self.clean)
        self.timer_clean.stop()

        self.timer_nfc_tag = QTimer(self)
        self.timer_nfc_tag.start(200)
        self.timer_nfc_tag.timeout.connect(self.blink_background)
        self.nfc_tag = False

        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet('font-weight: bold;'
                           f'font-size: {self.fontSize}px;')
        self.change_color_in_msec()

    def setText(self, txt):
        super().setText(txt)
        self.timer_clean.stop()
        if self.is_clean:
            self.timer_clean.start(self.clean_time)

    def clean(self):
        self.set_background_color()
        self.set_color(WHITE)
        self.clear()

    def set_background_color(self, color=BACK_GROUND_COLOR):
        self.background_color = color
        self.set_style_sheet()

    def blink_background(self):
        if self.background_color == LIGHT_BLUE:
            self.set_background_color()

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
        """

        :rtype: object
        """
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


def window_center(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())


def window_bottom_left(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().bottomLeft()
    qr.moveBottomLeft(cp)
    window.move(qr.topLeft())


def window_right(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().bottomRight()
    qr.moveBottomRight(cp)
    window.move(qr.topLeft())


def window_top_left(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().topLeft()
    qr.moveTopLeft(cp)
    window.move(qr.topLeft())


def style_sheet_setting(app):
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyqt5()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))


def make_error_popup(text):
    msg = QMessageBox()
    msg.setWindowTitle("ERROR")
    msg.setText(text)
    msg.setIcon(QMessageBox.Critical)
    x = msg.exec_()

# def trace(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         logger.debug(f'{func.__name__}({args!r}, {kwargs!r}')
#         result = func(*args, **kwargs)
#         logger.debug(f'{func.__name__} -> {result!r}')
#         return result
#
#     return wrapper
