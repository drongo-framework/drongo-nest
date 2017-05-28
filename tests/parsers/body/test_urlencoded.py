from nest.parsers.body.urlencoded import UrlEncodedParser

import unittest


class TestUrlEncodedParser(unittest.TestCase):
    def setUp(self):
        self.parser = UrlEncodedParser()

    def test_urlencoded(self):
        req = b'hello=world'
        env = dict(CONTENT_TYPE='application/x-www-form-urlencoded',
                   CONTENT_LENGTH=11)
        req = req[self.parser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])

    def test_urlencoded_chunked(self):
        req = b'hello=world'
        env = dict(CONTENT_TYPE='application/x-www-form-urlencoded',
                   CONTENT_LENGTH=11)
        while not self.parser.complete:
            req = req[self.parser.feed(req[:2], env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])
