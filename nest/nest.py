import socket
import sys


class Nest(object):
    def __init__(self, **settings):
        self._clients = {}

        # Bind settings
        host = settings.get('host', '0.0.0.0')
        port = settings.get('port', 8000)
        self.addr = (host, port)

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))

        # App to host
        self.app = settings.get('app')

        # Use asynio by default for Python 3.4 and above
        self.async = settings.get('async', (sys.version_info[:2] >= (3, 4)))

        # Do not use this in production!
        self.auto_reload = settings.get('auto_reload', False)
        self.reloader = None

    def run(self):
        if self.auto_reload:
            from .reloader import Reloader
            self.reloader = Reloader.activate()

        if self.async:
            from .handlers.async import AsyncHandler

            self.handler = AsyncHandler(
                nest=self, app=self.app, socket=self.sock)
        else:
            from .handlers.sync import SyncHandler
            self.handler = SyncHandler(
                nest=self, app=self.app, socket=self.sock)

        self.handler.run()

    def shutdown(self):
        if self.reloader:
            self.reloader.shutdown()

        self.handler.shutdown()
        self.sock.close()
