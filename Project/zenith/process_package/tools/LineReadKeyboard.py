from threading import Thread

from PySide2.QtCore import QObject, Signal
from pynput import keyboard
from pynput.keyboard import Key


class LineReadKeyboard(QObject):
    keyboard_input_signal = Signal(str)

    def __init__(self, keyboard_input_receiver=None):
        super(LineReadKeyboard, self).__init__()
        self.thread = None
        self._line_data = ''
        self.start_listen_keyboard()

        self.keyboard_input_signal.connect(keyboard_input_receiver)

    def get_line(self):
        listener = keyboard.Listener(
                on_press=self.on_press
        )
        listener.start()
        listener.join()
        return self._line_data

    def on_press(self, key):
        try:
            if key == Key.enter:
                if self._line_data:
                    return False
            else:
                self._line_data += key.char
        except AttributeError:
            pass
        except Exception as e:
            print(type(e), e)

    def start_listen_keyboard(self):
        self._line_data = ''
        self.thread = Thread(target=self.listen_keyboard, daemon=True)
        self.thread.start()

    def listen_keyboard(self):
        self.keyboard_input_signal.emit(self.get_line())
        self.start_listen_keyboard()


if __name__ == '__main__':
    ex = LineReadKeyboard()
    print(ex.get_line())
