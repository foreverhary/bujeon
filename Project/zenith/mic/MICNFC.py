import sys

from PySide2.QtWidgets import QApplication

from control.MICNFCControl import MICNFCControl
from view.MICNFCView import MICNFCView

MIC_VERSION = "MIC v1.34"


class MICNFC(QApplication):
    def __init__(self, sys_argv):
        super(MICNFC, self).__init__(sys_argv)
        self._control = MICNFCControl()
        self._view = MICNFCView(self)
        self._view.setWindowTitle(MIC_VERSION)


if __name__ == '__main__':
    app = MICNFC(sys.argv)
    sys.exit(app.exec_())
