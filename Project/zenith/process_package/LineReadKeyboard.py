from pynput import keyboard
from pynput.keyboard import Key


class LineReadKeyboard:
    __slots__ = ['_line_data']

    def __init__(self):
        self._line_data = ''

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


if __name__ == '__main__':
    ex = LineReadKeyboard()
    print(ex.get_line())
