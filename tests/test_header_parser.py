from nest.parsers import HeaderParser

import unittest


class TestHeaderParser(unittest.TestCase):
    def setUp(self):
        self.parser = HeaderParser()

    def test_valid_header(self):
        env = dict()
        headers = b'Host: localhost:5050\r\n' \
                  b'Connection: keep-alive\r\n' \
                  b'Upgrade-Insecure-Requests: 1\r\n' \
                  b'User-Agent: Test\r\n' \
                  b'Accept: text/html,application/xhtml+xml,application/xml;' \
                  b'q=0.9,image/webp,*/*;q=0.8\r\n' \
                  b'Accept-Encoding: gzip, deflate, sdch, br\r\n' \
                  b'Accept-Language: en-US,en;q=0.8\r\n\r\n'

        self.parser.feed(headers, env)

        self.assertEqual(env['HTTP_HOST'], 'localhost:5050')
        self.assertEqual(env['HTTP_CONNECTION'], 'keep-alive')
        self.assertTrue(self.parser.complete)

    def test_line_by_line(self):
        env = dict()
        headers = [
            b'Host: localhost:5050\r\n',
            b'Connection: keep-alive\r\n',
            b'Upgrade-Insecure-Requests: 1\r\n',
            b'User-Agent: Test\r\n',
            b'Accept: text/html,application/xhtml+xml,application/xml;'
            b'q=0.9,image/webp,*/*;q=0.8\r\n',
            b'Accept-Encoding: gzip, deflate, sdch, br\r\n',
            b'Accept-Language: en-US,en;q=0.8\r\n',
            b'\r\n'
        ]
        for h in headers:
            self.parser.feed(h, env)

        self.assertEqual(env['HTTP_HOST'], 'localhost:5050')
        self.assertEqual(env['HTTP_CONNECTION'], 'keep-alive')
        self.assertTrue(self.parser.complete)

    def test_feed_chunks(self):
        env = dict()
        headers = b'Host: localhost:5050\r\n' \
                  b'Connection: keep-alive\r\n' \
                  b'Upgrade-Insecure-Requests: 1\r\n' \
                  b'User-Agent: Test\r\n' \
                  b'Accept: text/html,application/xhtml+xml,application/xml;' \
                  b'q=0.9,image/webp,*/*;q=0.8\r\n' \
                  b'Accept-Encoding: gzip, deflate, sdch, br\r\n' \
                  b'Accept-Language: en-US,en;q=0.8\r\n\r\n'

        while headers:
            headers = headers[self.parser.feed(headers[:4], env):]

        self.assertEqual(env['HTTP_HOST'], 'localhost:5050')
        self.assertEqual(env['HTTP_CONNECTION'], 'keep-alive')
        self.assertTrue(self.parser.complete)

    def test_feed_bytewise(self):
        env = dict()
        headers = b'Host: localhost:5050\r\n' \
                  b'Connection: keep-alive\r\n' \
                  b'Upgrade-Insecure-Requests: 1\r\n' \
                  b'User-Agent: Test\r\n' \
                  b'Accept: text/html,application/xhtml+xml,application/xml;' \
                  b'q=0.9,image/webp,*/*;q=0.8\r\n' \
                  b'Accept-Encoding: gzip, deflate, sdch, br\r\n' \
                  b'Accept-Language: en-US,en;q=0.8\r\n\r\n'

        while headers:
            headers = headers[self.parser.feed(headers[:1], env):]

        self.assertEqual(env['HTTP_HOST'], 'localhost:5050')
        self.assertEqual(env['HTTP_CONNECTION'], 'keep-alive')
        self.assertTrue(self.parser.complete)
