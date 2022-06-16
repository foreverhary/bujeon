import sys
from threading import Thread

from PyQt5.QtCore import QTimer, QCoreApplication
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QApplication

from process_package.Views.CustomComponent import Button
from process_package.defined_variable_function import logger


class TestThread(QWidget):
    def __init__(self):
        super(TestThread, self).__init__()
        self.setLayout(layout := QVBoxLayout())
        layout.addWidget(quit := Button('quit'))
        quit.clicked.connect(QCoreApplication.instance().quit)
        self.timer = QTimer(self)
        self.timer.start(2000)
        self.timer.timeout.connect(self.timeout)
        self.show()

    def timeout(self):
        logger.debug('timer')
        self.ok = Thread(target=self.tt)
        self.ok.start()

    def tt(self):
        logger.debug('ok')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TestThread()
    sys.exit(app.exec_())