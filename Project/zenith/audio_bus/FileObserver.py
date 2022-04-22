from threading import Thread

import pandas as pd
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class Target(Thread):
    def __init__(self, path=None, signal=None):
        super(Target, self).__init__()
        self.observer = Observer()
        self.watchDir = path
        self.signal = signal
        self.daemon = True

    def run(self):
        event_handler = Handler(self.observer, self.signal)
        self.observer.schedule(event_handler, self.watchDir, recursive=False)
        self.observer.start()
        self.observer.join()


class Handler(FileSystemEventHandler):
    def __init__(self, observer, signal):
        super(Handler, self).__init__()
        self.observer = observer
        self.signal = signal

    def on_moved(self, event):
        pass

    def on_created(self, event):
        pass

    def on_deleted(self, event):
        pass

    def on_modified(self, event):
        self.signal.emit(event.src_path)
        # self.observer.stop()


if __name__ == '__main__':
    df = pd.read_excel('AD2000Report.xls', sheet_name="Summary", header=None)
    a = df.iterrows()
    dl = {}
    for l in a:
        # print(l[1][1])
        if 'Summary' in l[1][0]:
            next(a)
            data = next(a)
            name = l[1][0].split('Summary:')[1].strip().upper()
            dl[name] = (lower := data[1][1], upper := data[1][2])
            print(name, lower, upper, type(lower))

    print(dl)

    #
    # a = list(map(lambda x: x.split('\n'), df.to_string().split('Summary:')[1:]))
    #
    # di = {}
    # for l in a:
    #     name = l[0].strip()
    #     ch, lower, upper = l[2].split()
    #     di[name] = (lower, upper)
    #     print(name)
    #     print(lower, upper)
    #
    # print(di)
