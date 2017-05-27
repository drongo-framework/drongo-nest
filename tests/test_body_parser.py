from nest.parsers import RequestParser, HeaderParser, BodyParser

import unittest


class TestBodyParser(unittest.TestCase):
    def setUp(self):
        self.rparser = RequestParser()
        self.hparser = HeaderParser()
        self.bparser = BodyParser()

    def test_basic_post(self):
        req = (
            b'POST / HTTP/1.1\r\n'
            b'cache-control: no-cache\r\n'
            b'Postman-Token: d107c684-cc07-43df-9cab-51a01707fa38\r\n'
            b'Content-Type: application/x-www-form-urlencoded\r\n'
            b'User-Agent: PostmanRuntime/3.0.11-hotfix.2\r\n'
            b'Accept: */*\r\n'
            b'Host: localhost:5050\r\n'
            b'cookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\n'
            b'accept-encoding: gzip, deflate\r\n'
            b'content-length: 11\r\n'
            b'Connection: keep-alive\r\n\r\n'
            b'hello=world'
        )
        env = dict()
        req = req[self.rparser.feed(req, env):]
        req = req[self.hparser.feed(req, env):]
        req = req[self.bparser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])

    def test_basic_post_chunked(self):
        req = (
            b'POST / HTTP/1.1\r\n'
            b'cache-control: no-cache\r\n'
            b'Postman-Token: d107c684-cc07-43df-9cab-51a01707fa38\r\n'
            b'Content-Type: application/x-www-form-urlencoded\r\n'
            b'User-Agent: PostmanRuntime/3.0.11-hotfix.2\r\n'
            b'Accept: */*\r\n'
            b'Host: localhost:5050\r\n'
            b'cookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\n'
            b'accept-encoding: gzip, deflate\r\n'
            b'content-length: 11\r\n'
            b'Connection: keep-alive\r\n\r\n'
            b'hello=world'
        )
        env = dict()
        while not self.rparser.complete:
            req = req[self.rparser.feed(req[:2], env):]
        while not self.hparser.complete:
            req = req[self.hparser.feed(req[:2], env):]
        while not self.bparser.complete:
            req = req[self.bparser.feed(req[:2], env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])

    def test_multipart_post(self):
        req = (
            b'POST / HTTP/1.1\r\n'
            b'cache-control: no-cache\r\n'
            b'Postman-Token: 7345337a-50cb-4e8e-96f5-f642636f6e00\r\n'
            b'User-Agent: PostmanRuntime/3.0.11-hotfix.2\r\nAccept: */*\r\n'
            b'Host: localhost:5000\r\n'
            b'cookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\n'
            b'accept-encoding: gzip, deflate\r\n'
            b'content-type: multipart/form-data; '
            b'boundary=--------------------------830469423478890278155034\r\n'
            b'content-length: 434\r\n'
            b'Connection: keep-alive\r\n\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="test"; filename="hello.txt"\r\n'
            b'Content-Type: text/plain\r\n\r\n'
            b'Hello world\r\n\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="a"\r\n\r\n'
            b'100\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="b"\r\n\r\n'
            b'hello world\r\n'
            b'----------------------------830469423478890278155034--\r\n'
        )
        env = dict()
        req = req[self.rparser.feed(req, env):]
        req = req[self.hparser.feed(req, env):]
        req = req[self.bparser.feed(req, env):]

        self.assertEqual(len(env['POST']), 3)

    def test_multipart_post_chunked(self):
        req = (
            b'POST / HTTP/1.1\r\n'
            b'cache-control: no-cache\r\n'
            b'Postman-Token: 7345337a-50cb-4e8e-96f5-f642636f6e00\r\n'
            b'User-Agent: PostmanRuntime/3.0.11-hotfix.2\r\nAccept: */*\r\n'
            b'Host: localhost:5000\r\n'
            b'cookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\n'
            b'accept-encoding: gzip, deflate\r\n'
            b'content-type: multipart/form-data; '
            b'boundary=--------------------------830469423478890278155034\r\n'
            b'content-length: 434\r\n'
            b'Connection: keep-alive\r\n\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="test"; filename="hello.txt"\r\n'
            b'Content-Type: text/plain\r\n\r\n'
            b'Hello world\r\n\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="a"\r\n\r\n'
            b'100\r\n'
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="b"\r\n\r\n'
            b'hello world\r\n'
            b'----------------------------830469423478890278155034--\r\n'
        )
        env = dict()
        while not self.rparser.complete:
            req = req[self.rparser.feed(req[:2], env):]
        while not self.hparser.complete:
            req = req[self.hparser.feed(req[:2], env):]
        while not self.bparser.complete:
            req = req[self.bparser.feed(req[:2], env):]

        self.assertEqual(len(env['POST']), 3)
