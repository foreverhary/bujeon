from PySide2.QtCore import Slot, Signal
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGroupBox
from winsound import Beep

from process_package.SerialMachine import SerialMachine
from process_package.Views.CustomComponent import Button, ComboBox, Label, Widget, get_time, LabelTimerClean
from process_package.defined_serial_port import ports, get_serial_available_list
from process_package.resource.color import BLUE, RED, LIGHT_SKY_BLUE, LIGHT_BLUE
from process_package.resource.string import STR_CON_OS, STR_POGO_OS, STR_LED, STR_HALL_IC, STR_VBAT_ID, STR_C_TEST, \
    STR_BATTERY, STR_PROX_TEST, STR_MIC, STR_PCM, STR_SENSOR, CONFIG_FILE_NAME, COMPORT_SECTION, STR_OK
from process_package.tools.Config import get_config_value, set_config_value

NFC_IN_COUNT = 1
NFC_OUT_COUNT = 2
MACHINE_SERIAL_COUNT = 2


class SensorUI(Widget):
    def __init__(self):
        super(SensorUI, self).__init__()
        self.setLayout(layout := QVBoxLayout())

        # previous process
        layout.addLayout(previous_process_layout := QHBoxLayout())
        self.previous_process_label = []
        for _ in range(NFC_IN_COUNT):
            previous_process_layout.addWidget(previous_process_group := QGroupBox())
            previous_process_group.setTitle('PREVIOUS_PROCESS')
            previous_process_group.setLayout(group_layout := QVBoxLayout())
            self.previous_process_label.append(label := LabelTimerClean(is_clean=True))
            group_layout.addWidget(label)
            label.set_font_size(size=80)

        # Frame
        layout.addLayout(frame_layout := QHBoxLayout())
        self.ch_frame = []
        for index in range(MACHINE_SERIAL_COUNT):
            self.ch_frame.append(ch_frame := SensorChannelLayout(index + 1))
            frame_layout.addWidget(ch_frame)

        # status
        self.status_label = Label()

        layout.addWidget(self.status_label)

        self.setWindowTitle('IR SENSOR v0.1')

        self.setMinimumWidth(640)


class CustomLabel(Label):
    def __init__(self, txt):
        super(CustomLabel, self).__init__(txt)
        # self.setFixedWidth(300)


class SensorChannelLayout(QGroupBox):
    signal_update_sql = Signal(object)
    error_number = {
        STR_CON_OS: 1,
        STR_POGO_OS: 2,
        STR_LED: 3,
        STR_HALL_IC: 10,
        STR_VBAT_ID: 4,
        STR_C_TEST: 5,
        STR_BATTERY: 6,
        STR_PROX_TEST: 8,
        STR_MIC: 7,
        STR_PCM: 9,
    }

    def __init__(self, channel):
        super(SensorChannelLayout, self).__init__()
        self.channel = channel

        self.setTitle(f'Channel {self.channel}')
        layout = QVBoxLayout()

        self.serialComboBox = ComboBox()
        self.serialComboBox.addItems(ports)
        self.connectButton = Button('CONN')

        layout.addLayout(comportLayout := QHBoxLayout())
        comportLayout.addWidget(self.connectButton)
        comportLayout.addWidget(self.serialComboBox)

        dm_label = CustomLabel("DM")
        self.dmInput = CustomLabel('')
        layout.addWidget(dm_label)
        layout.addWidget(self.dmInput)

        result_label = CustomLabel("RESULT")
        self.resultInput = CustomLabel('')
        self.resultInput.setFixedHeight(350)
        self.resultInput.set_font_size(size=100)

        layout.addWidget(result_label)
        layout.addWidget(self.resultInput)

        self.setLayout(layout)

        self.error_code = {name: True for name in self.error_number}

        self.serial_machine = SerialMachine(baudrate=9600, serial_name=f'{STR_SENSOR}{self.channel}')
        self.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)

        self.connectButton.clicked.connect(self.connect_machine_button)

        self.write_nfc_msg = ''
        self.write_delay_count = 0

    def fill_available_ports(self):
        self.serialComboBox.clear()
        self.serialComboBox.addItems(get_serial_available_list())

    def connect_machine_button(self, not_key=None):
        if not_key:
            self.serialComboBox.setCurrentText(
                get_config_value(
                    CONFIG_FILE_NAME,
                    COMPORT_SECTION,
                    f"machine_comport_{self.channel}"
                )
            )

        if self.serial_machine.connect_serial(self.serialComboBox.currentText()):
            set_config_value(
                CONFIG_FILE_NAME,
                COMPORT_SECTION,
                f'machine_comport_{self.channel}',
                self.serial_machine.port
            )
            self.serial_machine.start_machine_read()
        self.check_serial_connection()

    def check_serial_connection(self):
        if self.serial_machine.is_open:
            self.connectButton.set_background_color(BLUE)
            self.serialComboBox.setDisabled(True)
        else:
            self.connectButton.set_background_color(RED)
            self.serialComboBox.setEnabled(True)

    @Slot(list)
    def receive_machine_result(self, result):
        if len(result) < 2:
            return
        self.init_result_true()
        if not result[-1]:
            result.pop()
        if result[-1] != STR_OK:
            for item, key in zip(result[1:-1], self.error_code):
                self.error_code[key] = item == STR_OK
        self.resultInput.set_background_color(LIGHT_SKY_BLUE if result[-1] == STR_OK else RED)
        self.resultInput.setText(result[-1])
        self.nfc.current_process_result = f"{'SENSOR_PROCESS'}:{result[-1]}"
        self.nfc.enable = True
        self.nfc.clean_check_dm()
        self.dmInput.clean()

    def init_result_true(self):
        self.error_code = {key: True for key in self.error_number}

    def get_ecode(self):
        return ','.join([
            str(self.error_number[key]) for key, value in self.error_code.items() if not value
        ])

    def received_previous_process(self, nfc):
        nfc.check_dm = ''
        self.dmInput.set_background_color(LIGHT_BLUE)
        if not nfc.check_pre_process_valid('SENSOR_PREVIOUS_PROCESS'):
            return
        msg = [self.nfc.dm]
        msg.extend(
            f"{process_name}:{self.nfc.nfc_previous_process[process_name]}"
            for process_name in 'PROCESS_NAMES'
            if process_name in self.nfc.nfc_previous_process
        )
        if self.write_delay_count:
            self.write_delay_count -= 1
            return
        if not self.resultInput.text():
            return
        if self.write_nfc_msg != ','.join(msg) :
            self.write_delay_count += 1
            write_msg = [self.nfc.dm]
            write_msg.extend(
                f"{process_name}:{self.nfc.nfc_previous_process[process_name]}"
                for process_name in 'SENSOR_PREVIOUS_PROCESS'
                if process_name in self.nfc.nfc_previous_process
            )
            write_msg.append(f"{'SENSOR_PROCESS'}:{self.resultInput.text()}")
            self.write_nfc_msg = ','.join(write_msg)
            msg = self.write_nfc_msg
            self.nfc.write(msg.encode())
            # self.nfc.readline()
        else:
            self.update_sql()
            self.display_nfc_write()

    def display_nfc_write(self):
        self.nfc.enable = False
        self.resultInput.clean()
        self.dmInput.setText(self.nfc.dm)
        self.signal_update_sql.emit(self.nfc)
        # Beep(FREQ + 1000, DUR)
        self.write_nfc_msg = ''

    def update_sql(self):
        self.mssql.start_query_thread(self.mssql.insert_pprd,
                                      self.nfc.dm,
                                      get_time(),
                                      self.resultInput.text(),
                                      STR_SENSOR,
                                      self.get_ecode()
                                      )
