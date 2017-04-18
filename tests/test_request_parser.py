from nest.parsers import RequestParser

import unittest


class TestRequest(unittest.TestCase):
    def setUp(self):
        self.parser = RequestParser()

    def test_oneshot(self):
        env = dict()
        n = self.parser.feed(b'GET / HTTP/1.1\r\n', env)
        self.assertEqual(env['REQUEST_METHOD'], 'GET')

    def test_bytewisefeed(self):
        env = dict()
        req = b'GET / HTTP/1.1\r\n'
        i = 0
        for _ in range(len(req)):
            i += self.parser.feed(req[i:i+1], env)
        self.assertEqual(env['REQUEST_METHOD'], 'GET')

    def test_feedextra(self):
        env = dict()
        req = b'GET / HTTP/1.1\r\nhello world'
        req = req[self.parser.feed(req, env):]
        self.assertEqual(req, b'hello world')

    def test_get_query(self):
        env = dict()
        req = b'GET /?a=b HTTP/1.1\r\n'
        self.parser.feed(req, env)
        self.assertEqual(env['QUERY'], {'a': ['b']})

    def test_invalid_method(self):
        env = dict()
        req = b'HELLO /?a=b HTTP/1.1\r\n'
        with self.assertRaises(Exception):
            self.parser.feed(req, env)

    def test_malformed_request(self):
        env = dict()
        req = b'GET /?a=b HTTP/1.1 POST\r\n'
        with self.assertRaises(Exception):
            self.parser.feed(req, env)
