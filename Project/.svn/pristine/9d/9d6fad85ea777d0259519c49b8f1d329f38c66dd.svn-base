import os
import sys

import qrcode as qrcode
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication

from qr_create_ui import QRCreateUI


def make_qr(text):
    img = qrcode.make(text)
    img.save(f"{text}.png")


class QRCreate(QRCreateUI):
    def __init__(self):
        super(QRCreate, self).__init__()

        self.createButton.clicked.connect(self.create_button_clicked)

        if not os.path.exists('qr_img'):
            os.mkdir('qr_img')
        self.setWindowTitle('QR 생성기')
        self.show()

    def create_button_clicked(self):
        if qrText := self.textInput.text():
            img = qrcode.make(qrText)
            print(type(img))
            img.save(imgpath := os.path.join('qr_img', f"{qrText}.png"))

            self.qrLabel.setPixmap(QPixmap(imgpath))
        else:
            pass


# 스크립트를 실행하려면 여백의 녹색 버튼을 누릅니다.s
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = QRCreate()
    sys.exit(app.exec_())

# https://www.jetbrains.com/help/pycharm/에서 PyCharm 도움말 참조
