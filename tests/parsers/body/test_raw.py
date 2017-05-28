from nest.parsers.body.raw import RawParser

import unittest


class TestRawParser(unittest.TestCase):
    def setUp(self):
        self.parser = RawParser()

    def test_raw(self):
        req = b'{"test": "hello world"}'
        env = dict(CONTENT_TYPE='application/json', CONTENT_LENGTH=23)
        req = req[self.parser.feed(req, env):]

        self.assertEqual(env['BODY'], b'{"test": "hello world"}')

    def test_raw_chunked(self):
        req = b'{"test": "hello world"}'
        env = dict(CONTENT_TYPE='application/json', CONTENT_LENGTH=23)
        while not self.parser.complete:
            req = req[self.parser.feed(req[:2], env):]

        self.assertEqual(env['BODY'], b'{"test": "hello world"}')
