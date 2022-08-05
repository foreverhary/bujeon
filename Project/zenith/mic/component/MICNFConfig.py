from PySide2.QtCore import QObject, Signal, Slot, Qt
from PySide2.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QHBoxLayout, QFileDialog

from process_package.component.CustomComponent import LeftAlignLabel, LineEdit, Button
from process_package.resource.size import AUDIO_BUS_PATH_LINE_EDIT_FONT_SIZE, AUDIO_BUS_PATH_LINE_EDIT_MIN_WIDTH
from process_package.resource.string import CONFIG_FILE_NAME, FILE_PATH, MIC_SECTION
from process_package.tools.Config import set_config_value, get_config_value


class MICNFCConfig(QDialog):
    def __init__(self, parent_control):
        super(MICNFCConfig, self).__init__()
        self._parent_control = parent_control
        self._model = MICNFCConfigModel()
        self._control = MICNFCConfigControl(self._model)

        # UI
        layout = QVBoxLayout(self)
        layout.addWidget(box := QGroupBox('File Path'))
        file_box_layout = QHBoxLayout(box)
        file_box_layout.addWidget(LeftAlignLabel("File Path"))
        file_box_layout.addWidget(path := LineEdit(font_size=AUDIO_BUS_PATH_LINE_EDIT_FONT_SIZE))
        file_box_layout.addWidget(path_button := Button('...'))

        layout.addLayout(button_layout := QHBoxLayout())
        button_layout.addWidget(save_button := Button('SAVE'))
        button_layout.addWidget(cancel_button := Button('CANCEL'))

        path.setMinimumWidth(AUDIO_BUS_PATH_LINE_EDIT_MIN_WIDTH)

        # signal
        path_button.clicked.connect(self._control.open_set_directory)
        save_button.clicked.connect(self.save)
        cancel_button.clicked.connect(self.close)

        path.textChanged.connect(self._control.change_path)

        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # linsten for model event
        self._model.mic_path_changed.connect(path.setText)

        self._model.begin()
        self.showModal()

    @Slot()
    def save(self):
        self._model.save()
        self.close()

    def showModal(self):
        return super().exec_()

    def closeEvent(self, e):
        self._parent_control.start_file_observe()


class MICNFCConfigControl(QObject):
    def __init__(self, model):
        super(MICNFCConfigControl, self).__init__()
        self._model = model

    def change_path(self, value):
        self._model.mic_path = value

    def open_set_directory(self):
        if path := str(QFileDialog.getExistingDirectory(directory=self._model.mic_path)):
            self._model.mic_path = path


class MICNFCConfigModel(QObject):
    mic_path_changed = Signal(str)

    def __init__(self):
        super(MICNFCConfigModel, self).__init__()

    @property
    def mic_path(self):
        return self._mic_path

    @mic_path.setter
    def mic_path(self, value):
        self._mic_path = value
        self.mic_path_changed.emit(value)

    def save(self):
        set_config_value(MIC_SECTION, FILE_PATH, self.mic_path)

    def begin(self):
        self.mic_path = get_config_value(MIC_SECTION, FILE_PATH)
