from ..parsers import HttpParser

import asyncio


class Reader(object):
    __slots__ = ['reader']

    BUFFER_SIZE = 102400  # 100kb

    def __init__(self, reader):
        self.reader = reader

    @asyncio.coroutine
    def get_one(self):
        http_parser = HttpParser()
        env = dict()
        while not http_parser.complete:
            data = yield from self.reader.read(self.BUFFER_SIZE)
            if not data:
                return None
            http_parser.feed(data, env)
        return env


class Responder(object):
    __slots__ = ['writer', 'app']

    def __init__(self, writer, app):
        self.writer = writer
        self.app = app

    def start_response(self, status, headers):
        self.writer.write(b'HTTP/1.1 ')
        self.writer.write(status.encode('ascii'))
        self.writer.write(b'\r\n')
        for h in headers:
            self.writer.write(': '.join(h).encode('ascii'))
            self.writer.write(b'\r\n')
        self.writer.write(b'\r\n')

    @asyncio.coroutine
    def respond(self, env):
        res = self.app(env, self.start_response)
        for data in res:
            self.writer.write(data)


class AsyncHandler(object):
    def __init__(self, nest, app, socket):
        self._clients = {}

        self.nest = nest
        self.app = app
        self.sock = socket

    def accept(self, reader, writer):
        task = self.loop.create_task(self.handle(reader, writer))
        self._clients[task] = (reader, writer)

        def client_done(task):
            del self._clients[task]
            writer.close()
        task.add_done_callback(client_done)

    @asyncio.coroutine
    def handle(self, reader, writer):
        http = Reader(reader)
        responder = Responder(writer, self.app)
        while True:
            try:
                env = yield from http.get_one()
                if env is None:
                    break
                yield from responder.respond(env)
            except ConnectionResetError as _:
                break  # Ignore the connection error
            except BrokenPipeError:
                break  # Ignore the broken pipe error

    def run(self):
        print('Listening on', self.nest.addr, '...')

        self.loop = asyncio.get_event_loop()
        server_coro = asyncio.start_server(
            self.accept, sock=self.sock, backlog=1000, loop=self.loop)
        self.server = self.loop.run_until_complete(server_coro)

        self.loop.run_forever()

    @asyncio.coroutine
    def async_shutdown(self):
        for task, (r, w) in self._clients.items():
            w.close()

    def shutdown(self):
        self.loop.run_until_complete(self.async_shutdown())
        self.server.close()

    def wait(self):
        pass
