import os
import sys
import time

from threading import Thread


class Reloader(Thread):
    __thread__ = None

    def __init__(self, app=None, interval=2):
        super(Reloader, self).__init__(name='reload_monitor')
        self.app = app
        self.interval = interval
        self.running = False
        self.mtimes = {}

    def _reload(self):
        print('Code change detected, reloading...')
        python = sys.executable
        if self.app:
            self.app.shutdown()
        os.execl(python, python, *sys.argv)

    def _scan(self):
        modules = [
            m.__file__ for m in sys.modules.values()
            if m is not None and '__file__' in m.__dict__
        ]

        for filename in modules:
            if filename.endswith('.pyc') or filename.endswith('.pyo'):
                filename = filename[:-1]

            try:
                stat = os.stat(filename)
            except OSError:
                continue

            mtime = stat.st_mtime

            if filename in self.mtimes:
                if mtime != self.mtimes[filename]:
                    Thread(target=self._reload).start()

            self.mtimes[filename] = mtime

    def run(self):
        self.running = True
        while self.running:
            self._scan()
            time.sleep(self.interval)

    @classmethod
    def activate(cls, app=None, interval=1):
        if cls.__thread__:
            return

        cls.app = app
        cls.__thread__ = cls(app=app, interval=interval)
        cls.__thread__.start()
        return cls.__thread__

    def shutdown(self):
        self.running = False
        self.join()
