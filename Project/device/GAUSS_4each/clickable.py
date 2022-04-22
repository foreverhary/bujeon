from PyQt5.QtCore import QObject, pyqtSignal, QEvent


def clickable(widget):
    class Filter(QObject):

        clicked = pyqtSignal()  # pyside2 사용자는 pyqtSignal() -> Signal()로 변경

        def eventFilter(self, obj, event):

            if (
                obj == widget
                and event.type() == QEvent.MouseButtonRelease
                and obj.rect().contains(event.pos())
            ):
                self.clicked.emit()
                # The developer can opt for .emit(obj) to get the object within the slot.
                return True

            return False

    filter = Filter(widget)
    widget.installEventFilter(filter)
    return filter.clicked
