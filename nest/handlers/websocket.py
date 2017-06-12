from ..parsers import WebsocketParser

import queue


class WebsocketHandler(object):
    BUFFER_SIZE = 102400

    def __init__(self, socket):
        self.sock = socket
        self._queue = queue.Queue()
        self._callbacks = []
        self.reset()

    def reset(self):
        self.websocket_parser = WebsocketParser()

    def _on_message(self, data):
        for cb in self._callbacks:
            cb(data)

    def read(self):
        data = self.sock.recv(self.BUFFER_SIZE)
        self.websocket_parser.feed(data)
        if self.websocket_parser.complete:
            data = self.websocket_parser.data()
            self._queue.put(data)
            self._on_message(data=data)
            self.reset()

    def get(self):
        return self._queue.get()

    def register(self, callback):
        self._callbacks.append(callback)
