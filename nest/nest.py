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

    def run(self):
        if self.async:
            from .handlers.async import AsyncHandler

            self.handler = AsyncHandler(
                nest=self, app=self.app, socket=self.sock)
            self.handler.run()
        else:
            # TODO: Implement
            print('Not supported at the moment.')
