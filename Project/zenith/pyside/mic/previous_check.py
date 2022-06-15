import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QVBoxLayout

from packages.component.CustomComponent import Widget, style_sheet_setting, Label
from packages.variable.size import MIC_PREVIOUS_CHECK_LABEL_FONT_SIZE, MIC_PREVIOUS_CHECK_LABEL_CLEAN_TIME
from packages.variable.variables import logger


class PreviousCheck(Widget):
    def __init__(self):
        super(PreviousCheck, self).__init__()
        self.result = None
        self.setup_ui()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.show()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(result := Label(font_size=MIC_PREVIOUS_CHECK_LABEL_FONT_SIZE, is_clean=True))
        result.setFixedSize(420, 230)
        self.result = result

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        if e.buttons() & Qt.MiddleButton:
            self.close()


if __name__ == '__main__':
    logger.info("previous checker start")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = PreviousCheck()
    sys.exit(app.exec())
