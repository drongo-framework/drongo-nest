from nest.parsers.body.multipart import MultipartParser

import unittest


class TestMultipartParser(unittest.TestCase):
    def setUp(self):
        self.parser = MultipartParser()

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

    def test_multipart_chunked(self):
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
        while not self.parser.complete:
            req = req[self.parser.feed(req[:2], env):]

        self.assertEqual(len(env['POST']), 3)
