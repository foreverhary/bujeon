import sys

from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

from process_package.SplashScreen import SplashScreen
from process_package.defined_variable_function import style_sheet_setting, window_center, NFC_IN, SENSOR_PREPROCESS, \
    NFC, BLUE, RED, logger, LIGHT_SKY_BLUE
from sensor_ui import SensorUI, NFC_IN_COUNT, NFC_OUT_COUNT


class SensorProcess(SensorUI):
    status_update_signal = pyqtSignal(object, str, str)
    machine_signal = pyqtSignal(str)

    def __init__(self, app):
        super(SensorProcess, self).__init__()
        self.app = app

        # variable
        self.nfc = []

        self.connect_event()

        self.load_window = SplashScreen("IR SENSOR")
        self.load_window.start_signal.connect(self.show_main_window)

    def show_main_window(self, nfc_list):
        self.load_window.close()
        self.init_serial(nfc_list)
        style_sheet_setting(self.app)

        self.show()
        window_center(self)

    def nfc_check(self):
        nfc_in_count = nfc_out_count = 0
        for nfc in self.nfc:
            nfc.previous_processes = SENSOR_PREPROCESS
            if nfc.serial_name not in self.__dict__:
                self.__setattr__(nfc.serial_name, nfc)
                if NFC_IN in nfc.serial_name:
                    nfc.signal.previous_process_signal.connect(self.received_previous_process)
                    nfc.signal.serial_error_signal.connect(self.receive_serial_error)
                    nfc.start_previous_process_check_thread()
                    nfc_in_count += 1
                elif NFC in nfc.serial_name:
                    nfc_out_count += 1

        return (nfc_in_count, nfc_out_count) == (NFC_IN_COUNT, NFC_OUT_COUNT)

    @pyqtSlot(object)
    def received_previous_process(self, nfc):
        if nfc.check_pre_process():
            msg = f"{nfc.dm} is PASS"
            color = LIGHT_SKY_BLUE
        else:
            msg = f"{nfc.dm} is FAIL"
            color = RED
        label = self.previous_process_label[int(nfc.serial_name.replace(NFC_IN, '')) - 1]
        self.status_update_signal.emit(label, msg, color)

    def init_serial(self, nfc_list):
        for frame in self.ch_frame:
            frame.fill_available_ports()
            frame.connect_machine_button(1)
            frame.serial_machine.signal.machine_result_signal.connect(self.receive_machine_result)

        self.nfc = nfc_list

        if self.nfc_check():
            self.status_update_signal.emit(self.status_label, "READY", BLUE)
        else:
            self.status_update_signal.emit(
                self.status_label,
                "CHECK NFC AND RESTART PROGRAM!!",
                RED
            )

    def connect_event(self):
        self.status_update_signal.connect(self.update_label)

    @pyqtSlot(str)
    def receive_serial_error(self, msg):
        self.status_update_signal.emit(self.status_label, msg, RED)

    @pyqtSlot(list)
    def receive_machine_result(self, result):
        logger.info(result)

    @pyqtSlot(object, str, str)
    def update_label(self, label, text, color):
        label.setText(text)
        label.set_text_property(color=color)

    def keyPressEvent(self, event):
        pass

    def closeEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SensorProcess(app)
    sys.exit(app.exec_())
