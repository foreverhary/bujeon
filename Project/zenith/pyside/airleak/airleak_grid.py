from PySide6.QtWidgets import QGroupBox, QGridLayout

from packages.views.CustomComponent import Label
from packages.resources.size import AIR_LEAK_UNIT_FONT_SIZE, AIR_LEAK_UNIT_MINIMUM_WIDTH, AIR_LEAK_RESULT_MINIMUM_HEIGHT
from packages.resources.string import RESULT
from packages.resources.variables import MANUAL_AIR_LEAK_UNIT_COUNT


class AirLeakGroup(QGroupBox):
    def __init__(self):
        super(AirLeakGroup, self).__init__()
        self.setTitle("OUT")

        layout = QGridLayout(self)
        layout.addWidget(Label(RESULT), 0, 0)
        layout.addWidget(Label(RESULT), 0, 1)
        layout.addWidget(result := Label(), 1, 0, MANUAL_AIR_LEAK_UNIT_COUNT, 1)
        result.setMinimumSize(AIR_LEAK_UNIT_MINIMUM_WIDTH, AIR_LEAK_RESULT_MINIMUM_HEIGHT)

        self.result = result
        self.units = [Label() for _ in range(MANUAL_AIR_LEAK_UNIT_COUNT)]
        for index, unit in enumerate(self.units):
            unit.set_font_size(AIR_LEAK_UNIT_FONT_SIZE)
            unit.setMinimumWidth(AIR_LEAK_UNIT_MINIMUM_WIDTH)
            layout.addWidget(unit, index + 1, 1)
