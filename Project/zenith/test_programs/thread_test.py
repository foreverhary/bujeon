import time, os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class Watcher:
    DIRECTORY_TO_WATCH = "d:/work/400.test/002.file_test"

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            # Take any action here when a file is first created.
            print(
            "Received created event - %s." % event.src_path)
            # def update(filename):
            # os.chmod (event.src_path, 0775)

        elif event.event_type == 'modified':
            # Taken any action here when a file is modified.
            print(
            "Received modified event - %s." % event.src_path)


if __name__ == '__main__':
    print(
    'Sites folder watchdog is running...')
    w = Watcher()
    w.run()
