from nest.parsers import RequestParser, HeaderParser, BodyParser

import unittest


class TestBodyParser(unittest.TestCase):
    def setUp(self):
        self.rparser = RequestParser()
        self.hparser = HeaderParser()
        self.bparser = BodyParser()

    def test_basic_post(self):
        req = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: d107c684-cc07-43df-9cab-51a01707fa38\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/3.0.11-hotfix.2\r\nAccept: */*\r\nHost: localhost:5050\r\ncookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\naccept-encoding: gzip, deflate\r\ncontent-length: 11\r\nConnection: keep-alive\r\n\r\nhello=world'
        env = dict()
        req = req[self.rparser.feed(req, env):]
        req = req[self.hparser.feed(req, env):]
        req = req[self.bparser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['BODY_REQUEST']['hello'], ['world'])

    def test_basic_post_chunked(self):
        req = b'POST / HTTP/1.1\r\ncache-control: no-cache\r\nPostman-Token: d107c684-cc07-43df-9cab-51a01707fa38\r\nContent-Type: application/x-www-form-urlencoded\r\nUser-Agent: PostmanRuntime/3.0.11-hotfix.2\r\nAccept: */*\r\nHost: localhost:5050\r\ncookie: _drongo_sessid=27501a6668ef4183bcd07289a9896799\r\naccept-encoding: gzip, deflate\r\ncontent-length: 11\r\nConnection: keep-alive\r\n\r\nhello=world'
        env = dict()
        while not self.rparser.complete:
            req = req[self.rparser.feed(req[:2], env):]
        while not self.hparser.complete:
            req = req[self.hparser.feed(req[:2], env):]
        while not self.bparser.complete:
            req = req[self.bparser.feed(req[:2], env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['BODY_REQUEST']['hello'], ['world'])
