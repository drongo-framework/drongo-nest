from nest.parsers import HttpParser

import unittest


class TestHttpParser(unittest.TestCase):
    def setUp(self):
        self.parser = HttpParser()

    def test_get(self):
        req = b'GET / HTTP/1.1\r\n\r\n'
        env = dict()
        req = req[self.parser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['REQUEST_METHOD'], 'GET')

    def test_post(self):
        req = (
            b'POST / HTTP/1.1\r\n'
            b'Content-Type: application/x-www-form-urlencoded\r\n'
            b'content-length: 11\r\n\r\n'
            b'hello=world'
        )
        env = dict()
        req = req[self.parser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])
