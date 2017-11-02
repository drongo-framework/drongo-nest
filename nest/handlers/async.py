import asyncio
import logging
import time

from ..parsers import HttpParser


__all__ = ['AsyncHandler']


class IOWrapper(object):
    __slots__ = ['_real', '_conn', 'byte_count']

    def __init__(self, real):
        self._real = real
        self._conn = None
        self.byte_count = 0

    def get_extra_info(self, *a, **kw):
        return self._real.get_extra_info(*a, **kw)

    def close(self):
        self._conn.close()
        self._real.close()

    @asyncio.coroutine
    def read(self, *a, **kw):
        result = yield from self._real.read(*a, **kw)
        self.byte_count += len(result)
        return result

    def write(self, *a, **kw):
        self.byte_count += len(a[0])
        return self._real.write(*a, **kw)


class ConnectionWrapper(object):
    __slots__ = ['_reader', '_writer', '_peer']

    _logger = logging.getLogger('nest_connection')

    def __init__(self, reader, writer):
        self._reader = reader
        self._writer = writer
        reader._conn = self
        writer._conn = self

        self._peer = writer.get_extra_info('peername')

        self._logger.info('New connection from [{peer}].'.format(
            peer=self._peer
        ))

    def close(self):
        self._logger.info('Disconnecting from [{peer}].'.format(
            peer=self._peer
        ))
        self._logger.info(
            'Received [{received} bytes] and send [{sent} bytes].'.format(
                received=self._reader.byte_count,
                sent=self._writer.byte_count
            )
        )


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
    _logger = logging.getLogger('nest')

    def __init__(self, nest, app, socket):
        self._clients = {}

        self.nest = nest
        self.app = app
        self.sock = socket

    def accept(self, reader, writer):
        reader = IOWrapper(reader)
        writer = IOWrapper(writer)
        ConnectionWrapper(reader, writer)

        self._ip, self._port = writer.get_extra_info('peername')

        task = self.loop.create_task(self.handle(reader, writer))
        self._clients[task] = (reader, writer)

        def client_done(task):
            task.exception()
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
                timer_start = time.time()
                if env is None:
                    break

                env['CLIENT_IP'] = self._ip
                env['CLIENT_PORT'] = self._port

                yield from responder.respond(env)
                timer_end = time.time()
                self._logger.info('Executed in [{time:0.3f} ms]'.format(
                    time=(timer_end - timer_start) * 1000
                ))
            except ConnectionResetError:
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
        self.server.close()
        for task, (r, w) in self._clients.items():
            w.close()

    def shutdown(self):
        self.loop.create_task(self.async_shutdown())

    def wait(self):
        pass
