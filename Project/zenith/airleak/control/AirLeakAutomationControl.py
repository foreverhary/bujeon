from PySide2.QtCore import QObject, Slot, Signal

from process_package.resource.string import STR_NG, STR_OK
from process_package.tools.db_update_from_file import UpdateDB


class AirLeakAutomationControl(QObject):
    set_result_slot = Signal(int, str)

    def __init__(self, model):
        super(AirLeakAutomationControl, self).__init__()
        self._model = model

        self.update_db = UpdateDB()

        # controller event connect

    @Slot(str)
    def comport_save(self, comport):
        self._model.comport = comport

    @Slot(str)
    def receive_serial_data(self, value):
        if (index_ch := value.find('CH')) < 0:
            return

        channel = int(value[index_ch + 2:index_ch + 3]) - 1
        result = STR_OK if STR_OK in value else STR_NG

        self.set_result_slot.emit(channel, result)
