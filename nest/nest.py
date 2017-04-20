import asyncio
import socket
import uvloop

from .parsers import HttpParser


class HttpReader(object):
    __slots__ = ['reader']

    BUFFER_SIZE = 102400  # 100kb

    def __init__(self, reader):
        self.reader = reader

    async def get_one(self):
        http_parser = HttpParser()
        env = dict()
        while not http_parser.complete:
            data = await self.reader.read(self.BUFFER_SIZE)
            if not data:
                return None
            http_parser.feed(data, env)
        return env


class NestResponder(object):
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

    async def respond(self, env):
        res = self.app(env, self.start_response)
        for data in res:
            self.writer.write(data)
            await self.writer.drain()


class Nest(object):
    def __init__(self, host='0.0.0.0', port=8000, app=None):
        self._clients = {}
        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((host, port))
        self.app = app

    def accept(self, reader, writer):
        task = self.loop.create_task(self.handle(reader, writer))
        self._clients[task] = (reader, writer)

        def client_done(task):
            del self._clients[task]
            writer.close()
        task.add_done_callback(client_done)

    async def handle(self, reader, writer):
        http = HttpReader(reader)
        responder = NestResponder(writer, self.app)
        while True:
            env = await http.get_one()
            if env is None:
                break
            await responder.respond(env)

    def run(self):
        self.loop = uvloop.new_event_loop()
        server_coro = asyncio.start_server(
            self.accept, sock=self.sock, backlog=1000, loop=self.loop)
        server = self.loop.run_until_complete(server_coro)
        try:
            self.loop.run_forever()
        finally:
            server.close()
