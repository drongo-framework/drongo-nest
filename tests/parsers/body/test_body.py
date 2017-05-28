from nest.parsers import BodyParser

import unittest


class TestBodyParser(unittest.TestCase):
    def setUp(self):
        self.parser = BodyParser()

    def test_urlencoded(self):
        req = b'hello=world'
        env = dict(CONTENT_TYPE='application/x-www-form-urlencoded',
                   CONTENT_LENGTH=11)
        req = req[self.parser.feed(req, env):]

        self.assertEqual(req, b'')
        self.assertEqual(env['POST']['hello'], ['world'])

    def test_raw(self):
        req = b'{"test": "hello world"}'
        env = dict(CONTENT_TYPE='application/json', CONTENT_LENGTH=23)
        req = req[self.parser.feed(req, env):]

        self.assertEqual(env['BODY'], b'{"test": "hello world"}')

    def test_multipart(self):
        req = (
            b'----------------------------830469423478890278155034\r\n'
            b'Content-Disposition: form-data; name="test"; '
            b'filename="hello.txt"\r\n'
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
        env = dict(
            CONTENT_TYPE='multipart/form-data; '
            'boundary=--------------------------830469423478890278155034',
            CONTENT_LENGTH=434
        )
        req = req[self.parser.feed(req, env):]

        self.assertEqual(len(env['POST']), 3)
