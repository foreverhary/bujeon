import qdarkstyle as qdarkstyle
from PySide2.QtCore import QTimer, Qt, QDate
from PySide2.QtGui import QFontDatabase, QFont, QCursor
from PySide2.QtSerialPort import QSerialPort
from PySide2.QtWidgets import QPushButton, QLineEdit, QComboBox, QLabel, QDateEdit, QGroupBox, QVBoxLayout, QHBoxLayout, \
    QWidget, QMessageBox

from packages.controllers.serial_port import SerialPort
from packages.views.style import STYLE
from packages.resources.color import WHITE, BACK_GROUND_COLOR, LIGHT_BLUE, RED, LIGHT_YELLOW, BLUE
from packages.resources.variables import logger, get_serial_available_list

DEFAULT_FONT_SIZE = 30


class Widget(QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.m_Position = None
        self.m_flag = False

    def mousePressEvent(self, e):
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

    def keyPressEvent(self, e):
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
    def __init__(self, txt='', font_size=DEFAULT_FONT_SIZE, is_clean=False, clean_time=2000):
        super(Label, self).__init__(txt)
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


class GroupLabel(QGroupBox):
    def __init__(self, title='', is_clean=False, font_size=DEFAULT_FONT_SIZE):
        super(GroupLabel, self).__init__()
        self.setTitle(title)
        layout = QVBoxLayout(self)
        layout.addWidget(label := Label(is_clean=is_clean))

        self.label = label
        self.label.set_font_size(size=font_size)


class HBoxSerial(QHBoxLayout):

    def __init__(self, button_text='CONNECT'):
        super(HBoxSerial, self).__init__()
        self.serial = None
        self.addWidget(comport := QComboBox())
        self.addWidget(button := Button(button_text))

        self.comport = comport
        self.button = button

        self.button.clicked.connect(self.clicked_button)

    def check_connect(self):
        if self.serial.isOpen():
            self.button.set_clicked(BLUE)
            self.comport.setDisabled(True)
        else:
            self.button.set_clicked(RED)
            self.comport.setEnabled(True)

    def setup_serial(self, port, baudrate, serial_name):
        self.fill_available_ports()
        port = port or self.comport.currentText()
        self.serial = SerialPort(serial_name)
        self.serial.set_port_baudrate(port, baudrate)
        if not self.serial.toggle():
            logger.warn(f"{self.serial.port} cannot connect!!")
        self.check_connect()

    def fill_available_ports(self):
        self.comport.clear()
        self.comport.addItems(get_serial_available_list())

    def toggle_serial(self):
        return self.serial.close() if self.serial.isOpen() else self.serial.open()

    def set_port(self):
        self.serial.port = self.comport.currentText() or None

    def clicked_button(self):
        self.set_port()
        try:
            self.toggle_serial()
        except SerialException:
            logger.warn(f"{self.serial.port} cannot connect!!")
            msg = QMessageBox()
            msg.setWindowTitle("CONNECT ERROR")
            msg.setText(f"{self.serial.port} Connect Fail")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()
        self.check_connect()


def style_sheet_setting(app):
    app.setStyleSheet(STYLE)
    a = qdarkstyle.load_stylesheet_pyside2()
    fontDB = QFontDatabase()
    fontDB.addApplicationFont("./font/D2Coding-Ver1.3.2-20180524-all.ttc")
    app.setFont(QFont('D2Coding-Ver1.3.2-20180524-all'))
