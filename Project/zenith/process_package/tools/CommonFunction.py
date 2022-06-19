from winsound import Beep

from process_package.tools.logger import get_logger

logger = get_logger("My Logger")

def read_beep():
    Beep(2500, 200)

def write_beep():
    Beep(3500, 200)