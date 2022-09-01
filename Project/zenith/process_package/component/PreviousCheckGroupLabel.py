from PySide2.QtCore import Slot

from process_package.component.CustomMixComponent import GroupLabel
from process_package.resource.color import RED, LIGHT_SKY_BLUE
from process_package.resource.string import PROCESS_NAMES_WITHOUT_AIR_LEAK, STR_NG, PROCESS_FULL_NAMES, STR_MISS, \
    STR_DATA_MATRIX, PROCESS_NAMES_FROM_DATABASE, STR_PROCESS_RESULTS
from process_package.screen.NGScreen import NGScreen
from process_package.tools.CommonFunction import get_bit_in_one_byte


class PreviousCheckerGroupLabel(GroupLabel):
    def __init__(self, *args, **kwargs):
        self.process_name = kwargs.pop("process_name")
        super(PreviousCheckerGroupLabel, self).__init__(*args, **kwargs)

    @Slot(dict)
    def check_previous(self, value):
        error_msg = ''
        for index in range(PROCESS_NAMES_WITHOUT_AIR_LEAK.index(self.process_name)):
            if not get_bit_in_one_byte(
                    results_byte := value.get(STR_PROCESS_RESULTS),
                    index):
                error_msg += f"{PROCESS_FULL_NAMES[PROCESS_NAMES_WITHOUT_AIR_LEAK[index]]} : {STR_NG}\n"
        self.display_value(value.get(STR_DATA_MATRIX), error_msg)

    def display_value(self, data_matrix, error_msg):
        if error_msg:
            self.setText(f"{data_matrix}\n{error_msg}")
            self.set_background_color(RED)
        else:
            self.setText(f"{data_matrix}")
            self.set_background_color(LIGHT_SKY_BLUE)


class PreviousCheckerGroupLabelWithNGScreen(PreviousCheckerGroupLabel):
    def __init__(self, *args, **kwargs):
        super(PreviousCheckerGroupLabelWithNGScreen, self).__init__(*args, **kwargs)
        self.ng_screen_opened = False

    def display_value(self, data_matrix, error_msg):
        if error_msg:
            self.error_msg = f"{data_matrix}\n{error_msg[:-1]}"
            self.ng_screen_opened = True
            NGScreen(self)
        else:
            self.setText(f"{data_matrix}")
            self.set_background_color(LIGHT_SKY_BLUE)


class PreviousCheckerGroupLabelAirTouch(PreviousCheckerGroupLabel):
    def __init__(self, *args, **kwargs):
        super(PreviousCheckerGroupLabelAirTouch, self).__init__(*args, **kwargs)

    def check_previous(self, value):
        error_msg = ''
        for process_name in PROCESS_NAMES_FROM_DATABASE:
            if self.process_name == process_name:
                break
            if process := value.get(process_name):
                if process == STR_NG:
                    error_msg += f"{PROCESS_FULL_NAMES[process_name]} : {STR_NG}\n"
            else:
                error_msg += f"{PROCESS_FULL_NAMES[process_name]} : {STR_MISS}\n"
        self.display_value(value.get(STR_DATA_MATRIX), error_msg)
