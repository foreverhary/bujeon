import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout

from packages.component.CustomComponent import style_sheet_setting, Widget, GroupLabel, Label
from packages.variable.size import SENSOR_PREVIOUS_PROCESS_FONT_SIZE
from packages.variable.string import PREVIOUS_PROCESS
from packages.variable.variables import logger
from channel_group import ChannelGroup


class SensorProcess(Widget):
    def __init__(self):
        super(SensorProcess, self).__init__()
        self.status = None
        self.previous = None
        self.channel = None
        self.setup_ui()
        self.show()
        print(f"width : {self.channel[0].width()}")

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(previous := GroupLabel(PREVIOUS_PROCESS, is_clean=True))
        layout.addLayout(channel_layout := QHBoxLayout())
        previous.label.set_font_size(SENSOR_PREVIOUS_PROCESS_FONT_SIZE)

        self.channel = [ChannelGroup(channel + 1) for channel in range(2)]
        channel_layout.addWidget(self.channel[0])
        channel_layout.addWidget(self.channel[1])

        layout.addWidget(status := Label())

        self.previous = previous
        self.status = status


if __name__ == '__main__':
    logger.info("sensor start")
    app = QApplication(sys.argv)
    style_sheet_setting(app)
    ex = SensorProcess()
    sys.exit(app.exec())
