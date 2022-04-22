from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox

from process_package.PyQtCustomComponent import Button, LineEdit, Label, ComboBox
from process_package.defined_serial_port import ports
from process_package.defined_variable_function import DM_FONT_SIZE, DM_LABEL_WIDTH_SIZE


class AirLeakMainLayout(QVBoxLayout):
    def __init__(self, parent=None):
        super(AirLeakMainLayout, self).__init__(parent)

        # component
        self.orderButton = Button('AUFNR', self)
        self.orderInput = LineEdit(parent=self)
        self.lineLabel = Label('LINE:', self)
        self.lineCombo = ComboBox(self)
        self.portLabel = Label('PORT:', self)
        self.comportCombo = ComboBox(self)
        self.connectButton = Button('CONNECT', self)

        self.leftUnitLabel = [Label(f"UNIT {index + 1}", self) for index in range(5)]
        self.rightUnitLabel = [Label(f"UNIT {index + 1}", self) for index in range(5)]
        self.leftUnitDM = [Label('', self) for _ in range(5)]
        self.rightUnitDM = [Label('', self) for _ in range(5)]
        self.resultLeftLabel = Label("RESULT")
        self.resultRightLabel = Label("RESULT")
        self.leftResult = Label('', self)
        self.rightResult = Label('', self)

        # component setting
        self.orderInput.setReadOnly(True)
        self.orderInput.setMinimumWidth(250)
        self.lineCombo.addItems([str(index) for index in range(1,10)])
        self.lineCombo.setMinimumWidth(50)
        self.comportCombo.addItems(ports)
        self.comportCombo.setMinimumWidth(200)
        list(map(lambda x: x.set_text_property(DM_FONT_SIZE), self.leftUnitDM))
        list(map(lambda x: x.set_text_property(DM_FONT_SIZE), self.rightUnitDM))

        # layout
        topMenuLayout = QHBoxLayout()

        topMenuLayout.addWidget(self.orderButton)
        topMenuLayout.addWidget(self.orderInput)
        topMenuLayout.addSpacing(70)
        topMenuLayout.addWidget(self.lineLabel)
        topMenuLayout.addWidget(self.lineCombo)
        topMenuLayout.addSpacing(70)
        topMenuLayout.addWidget(self.portLabel)
        topMenuLayout.addWidget(self.comportCombo)
        topMenuLayout.addWidget(self.connectButton)

        self.addLayout(topMenuLayout)
        slotLayout = QHBoxLayout()

        for side, unitLabel, unitDMs, resultLabel, result in zip(['left', 'right'],
                                                                 [self.leftUnitLabel, self.rightUnitLabel],
                                                                 [self.leftUnitDM, self.rightUnitDM],
                                                                 [self.resultLeftLabel, self.resultRightLabel],
                                                                 [self.leftResult, self.rightResult]):
            box = QGroupBox(f"{side.upper()} SLOT")
            box.setAlignment(Qt.AlignCenter)
            self.__setattr__(f"{side}Group", box)
            layout = QGridLayout()
            for index, (label, unitDM) in enumerate(zip(unitLabel, unitDMs)):
                layout.addWidget(label, index, 0)
                layout.addWidget(unitDM, index, 1)
                label.setFixedWidth(DM_LABEL_WIDTH_SIZE)
                unitDM.setFixedWidth(DM_LABEL_WIDTH_SIZE)
            layout.addWidget(resultLabel, 5, 0, 1, 2)
            layout.addWidget(result, 6, 0, 1, 2)
            box.setLayout(layout)
            slotLayout.addWidget(box)
        self.addLayout(slotLayout)

    def keyPressEvent(self, event):
        self.parent().keyPressEvent(event)
