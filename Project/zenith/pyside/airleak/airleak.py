import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout

from airleak_grid import AirLeakGroup
from packages.views.CustomComponent import Widget, style_sheet_setting, HBoxSerial, Label
from packages.resources.variables import logger


class AirLeak(Widget):
    def __init__(self):
        super(AirLeak, self).__init__()
        self.status = None
        self.result = None
        self.comport = None
        self.setup_ui()
        self.show()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addLayout(comport := HBoxSerial())
        layout.addWidget(result := AirLeakGroup())
        layout.addWidget(status := Label())

        self.comport = comport
        self.result = result
        self.status = status
        

if __name__ == '__main__':
    logger.info("AirLeak Start")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = AirLeak()
    sys.exit(app.exec_())
