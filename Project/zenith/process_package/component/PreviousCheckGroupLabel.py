from PySide2.QtCore import Slot

from process_package.component.CustomMixComponent import GroupLabel
from process_package.resource.color import RED, LIGHT_SKY_BLUE
from process_package.resource.string import PROCESS_NAMES_WITHOUT_AIR_LEAK, STR_NG, PROCESS_FULL_NAMES, STR_MISS, \
    STR_DATA_MATRIX


class PreviousCheckerGroupLabel(GroupLabel):
    def __init__(self, *args, **kwargs):
        self.process_name = kwargs["process_name"]
        del(kwargs["process_name"])
        super(PreviousCheckerGroupLabel, self).__init__(*args, **kwargs)

    @Slot(dict)
    def check_previous(self, value):
        error_msg = ''
        for process_name in PROCESS_NAMES_WITHOUT_AIR_LEAK:
            if self.process_name == process_name:
                break
            if process := value.get(process_name):
                if process == STR_NG:
                    error_msg += f"{PROCESS_FULL_NAMES[process_name]} : {STR_NG}\n"
            else:
                error_msg += f"{PROCESS_FULL_NAMES[process_name]} : {STR_MISS}\n"

        if error_msg:
            self.setText(f"{value.get(STR_DATA_MATRIX)}\n{error_msg[:-1]}")
            self.set_background_color(RED)
        else:
            self.setText(f"{value.get(STR_DATA_MATRIX)}")
            self.set_background_color(LIGHT_SKY_BLUE)
