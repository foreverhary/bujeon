from PySide6.QtWidgets import QGroupBox, QVBoxLayout

from packages.views.CustomComponent import HBoxSerial, Label
from packages.resources.size import SENSOR_RESULT_FIXED_HEIGHT, SENSOR_RESULT_FONT_SIZE, SENSOR_CHANNEL_GROUP_MINIMUM_WIDTH
from packages.resources.string import DM, RESULT


class ChannelGroup(QGroupBox):
    def __init__(self, channel):
        super(ChannelGroup, self).__init__()
        self.channel = channel
        self.setTitle(f"Channel {self.channel}")
        layout = QVBoxLayout(self)
        layout.addLayout(comport := HBoxSerial(button_text='CONN'))
        layout.addWidget(Label(DM))
        layout.addWidget(data_matrix := Label())
        layout.addWidget(Label(RESULT))
        layout.addWidget(result := Label())
        result.setFixedHeight(SENSOR_RESULT_FIXED_HEIGHT)
        result.set_font_size(SENSOR_RESULT_FONT_SIZE)

        self.comport = comport
        self.data_matrix = data_matrix
        self.result = result

        self.setMinimumWidth(SENSOR_CHANNEL_GROUP_MINIMUM_WIDTH)
