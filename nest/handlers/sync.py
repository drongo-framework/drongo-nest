from ..parsers import HttpParser

from threading import Lock

import select
import socket


class Reader(object):
    BUFFER_SIZE = 102400

    def __init__(self, socket):
        self.sock = socket
        self.reset()

    def reset(self):
        self.http_parser = HttpParser()
        self.env = dict()

    def get(self):
        data = self.sock.recv(self.BUFFER_SIZE)

        if len(data) == 0:
            raise EOFError

        self.http_parser.feed(data, self.env)

        if self.http_parser.complete:
            # return and reset
            env = self.env
            self.reset()
            return env


class Responder(object):
    def __init__(self, socket, app):
        self.sock = socket
        self.app = app

    def start_response(self, status, headers):
        self.sock.send(b''.join([
            b'HTTP/1.1 ',
            status.encode('ascii'),
            b'\r\n'
        ]))

        for h in headers:
            self.sock.send(b''.join([
                ': '.join(h).encode('ascii'),
                b'\r\n'
            ]))
        self.sock.send(b'\r\n')

    def respond(self, env):
        res = self.app(env, self.start_response)
        for data in res:
            self.sock.send(data)


class SyncHandler(object):
    def __init__(self, nest, app, socket):
        self._clients = []
        self._client_readers = {}

        self.nest = nest
        self.app = app
        self.sock = socket
        self.running = False
        self.lock = Lock()

    def handle_server(self):
        client, addr = self.sock.accept()
        reader = Reader(client)
        self._clients.append(client)
        self._client_readers[client] = reader

    def handle_client(self, sock):
        reader = self._client_readers.get(sock)
        try:
            env = reader.get()
            if env:
                responder = Responder(sock, self.app)
                responder.respond(env)
        except (EOFError, socket.error) as _:
            # TODO: Log the error
            sock.close()
            self._client_readers.pop(sock)
            self._clients.remove(sock)

    def run(self):
        with self.lock:
            print('Listening on', self.nest.addr, '...')
            self.sock.listen(5)
            self.running = True

            while self.running:
                rlist, wlist, xlist = select.select(
                    [self.sock] + self._clients,  # rlist
                    [],  # wlist
                    [],  # xlist
                    1  # timeout
                )

                for sock in rlist:
                    if sock == self.sock:
                        self.handle_server()
                    else:
                        self.handle_client(sock)

            for sock in self._clients:
                sock.close()

    def wait(self):
        with self.lock:
            pass

    def shutdown(self):
        self.running = False
